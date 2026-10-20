"""Fit on training rows and select by validation AUC; never evaluate the test set."""
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from evaluation import dataset_splits, features, target, score, data_hash

HERE = Path(__file__).resolve().parent

def main():
    splits = dataset_splits()
    train, val = splits['train'], splits['validation']
    X = features(train)
    numeric = ['tenure', 'MonthlyCharges', 'TotalCharges', 'SeniorCitizen']
    categorical = [c for c in X if c not in numeric]
    pre = ColumnTransformer([('num', StandardScaler(), numeric),
                             ('cat', OneHotEncoder(handle_unknown='ignore'), categorical)])
    models = {
        'LogisticRegression': LogisticRegression(max_iter=1000, C=.5, random_state=42),
        'RandomForest': RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_leaf=5, random_state=42, n_jobs=2),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=250, max_depth=3, learning_rate=.08, random_state=42),
    }
    results, fitted = [], {}
    for name, estimator in models.items():
        pipe = Pipeline([('pre', clone(pre)), ('clf', estimator)])
        pipe.fit(X, target(train))
        result = {'model': name, 'evaluation_split': 'validation', **score(target(val), pipe.predict_proba(features(val))[:, 1], .5)}
        results.append(result)
        fitted[name] = pipe
    metrics = pd.DataFrame(results).sort_values(['roc_auc', 'model'], ascending=[False, True])
    metrics.to_csv(HERE/'metrics.csv', index=False)
    best_name = metrics.iloc[0]['model']
    best = fitted[best_name]
    joblib.dump(best, HERE/'best_model.joblib')
    names = best.named_steps['pre'].get_feature_names_out()
    estimator = best.named_steps['clf']
    if hasattr(estimator, 'coef_'):
        importance = pd.DataFrame({'feature': names, 'value': estimator.coef_[0], 'kind': 'coefficient'})
    else:
        importance = pd.DataFrame({'feature': names, 'value': estimator.feature_importances_, 'kind': 'tree_importance'})
    importance['absolute_value'] = importance.value.abs()
    importance.sort_values('absolute_value', ascending=False).to_csv(HERE/'feature_importance.csv', index=False)
    summary = {'dataset': 'synthetic', 'dataset_sha256': data_hash(), 'split_seed': 42,
               'split_counts': {k: len(v) for k, v in splits.items()},
               'selection_rule': 'highest validation ROC-AUC; no test metric used',
               'best_model': best_name, 'validation_metrics': metrics.iloc[0].to_dict(),
               'test_evaluated': False}
    (HERE/'summary.json').write_text(json.dumps(summary, indent=2))
    manifest = {k: sorted(v.customerID.tolist()) for k,v in splits.items()}
    (HERE/'split_manifest.json').write_text(json.dumps(manifest, indent=2))
    print(metrics.round(4).to_string(index=False))
    print('Selected', best_name, 'on validation only. Run threshold_tune.py for the final test evaluation.')

if __name__ == '__main__':
    main()
