"""Select thresholds on validation data; report frozen choices on held-out test data."""
import hashlib
import json
from pathlib import Path
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve
from evaluation import dataset_splits, features, target, score, data_hash

HERE = Path(__file__).resolve().parent

def select_thresholds(y, probabilities):
    grid = pd.DataFrame([score(y, probabilities, round(float(t), 2)) for t in np.linspace(.05, .95, 91)])
    # Deterministic tie-break: prefer the higher threshold among equal F1s.
    best = grid.sort_values(['f1', 'threshold'], ascending=[False, False]).iloc[0]
    eligible = grid[grid.recall >= .70]
    recall = eligible.sort_values(['precision', 'threshold'], ascending=[False, False]).iloc[0] if len(eligible) else None
    return grid, best, recall

def main():
    metadata = json.loads((HERE/'summary.json').read_text())
    if metadata['dataset_sha256'] != data_hash():
        raise ValueError('Dataset changed since training. Run train.py again.')
    # Load only a model generated locally by train.py; do not load untrusted joblib files.
    model = joblib.load(HERE/'best_model.joblib')
    splits = dataset_splits()
    val, test = splits['validation'], splits['test']
    grid, best, recall = select_thresholds(target(val), model.predict_proba(features(val))[:, 1])
    grid.to_csv(HERE/'threshold_grid.csv', index=False)
    selected = {'default_0_5': .5, 'validation_best_f1': float(best.threshold)}
    if recall is not None:
        selected['validation_recall_ge_0_70'] = float(recall.threshold)
    y = target(test)
    test_probability = model.predict_proba(features(test))[:, 1]
    # Thresholds above are fixed before looking at held-out test performance.
    test_results = [{'operating_point': name, 'evaluation_split': 'test', **score(y, test_probability, t)} for name,t in selected.items()]
    # Predicting the training prevalence is a reproducible constant-probability baseline.
    baseline = np.full(len(test), float(target(splits['train']).mean()))
    test_results.append({'operating_point': 'constant_prevalence_baseline', 'evaluation_split': 'test', **score(y, baseline, .5)})
    pd.DataFrame(test_results).to_csv(HERE/'test_metrics.csv', index=False)
    output = {'threshold_selection_split': 'validation', 'final_evaluation_split': 'test',
              'dataset_sha256': data_hash(),
              'model_sha256': hashlib.sha256((HERE/'best_model.joblib').read_bytes()).hexdigest(),
              'validation_best_f1': best.to_dict(),
              'validation_recall_ge_0_70': recall.to_dict() if recall is not None else None,
              'test_results': test_results}
    (HERE/'threshold_summary.json').write_text(json.dumps(output, indent=2))
    fig, ax = plt.subplots(figsize=(6.5,4.5))
    for label in ['precision','recall','f1']:
        ax.plot(grid.threshold, grid[label], label=label)
    ax.axvline(best.threshold, ls='--', color='gray', label=f'Validation best F1 @ {best.threshold:.2f}')
    ax.set(xlabel='Threshold', ylabel='Validation score', title='Threshold selection uses validation rows only')
    ax.legend();fig.tight_layout();fig.savefig(HERE/'threshold_curve.png',dpi=140);plt.close(fig)
    chosen = selected['validation_best_f1']
    cm = confusion_matrix(y, test_probability >= chosen)
    fig, ax = plt.subplots(figsize=(5,4))
    ax.imshow(cm,cmap='Blues')
    for i in range(2):
        for j in range(2):
            ax.text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>cm.max()/2 else 'black')
    ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['Stay','Churn'],yticklabels=['Stay','Churn'],xlabel='Predicted',ylabel='Actual',title=f'Test set, frozen threshold {chosen:.2f}')
    fig.tight_layout();fig.savefig(HERE/'confusion_matrix.png',dpi=140);plt.close(fig)
    fpr,tpr,_ = roc_curve(y,test_probability)
    fig,ax=plt.subplots(figsize=(5,4))
    ax.plot(fpr,tpr,label=f"Test AUC {test_results[0]['roc_auc']:.3f}");ax.plot([0,1],[0,1],'--',color='gray')
    ax.set(xlabel='False positive rate',ylabel='True positive rate',title='Held-out test ROC');ax.legend()
    fig.tight_layout();fig.savefig(HERE/'roc_curve.png',dpi=140);plt.close(fig)
    print(pd.DataFrame(test_results).round(4).to_string(index=False))

if __name__ == '__main__':
    main()
