# Telco churn: validation-selected models and operating points

A reproducible classification exercise over **7,043 synthetic customers**. The simulated labels are generated in `generate_data.py`; the source is not the real IBM Telco dataset. Findings are not evidence about actual customers.

## Run

Install this folder's `requirements.txt` or the repository-wide requirements, then run from this folder:

```sh
python generate_data.py
python train.py
python threshold_tune.py
```

## Evaluation design

`evaluation.py` creates deterministic stratified **60% training / 20% validation / 20% test** splits. The row counts and customer IDs are saved in `summary.json` and `split_manifest.json`.

1. Fit preprocessing and three candidate classifiers on training rows only. Each candidate gets an independent preprocessor.
2. Select the model with the highest **validation** ROC-AUC. `metrics.csv` contains validation results, not test results.
3. Choose the best-F1 threshold and the best-precision threshold satisfying validation recall ≥0.70 on validation rows only.
4. Freeze those choices and evaluate them on the untouched test rows. `test_metrics.csv` reports the result alongside a constant-prevalence baseline.

The model is not refit on validation rows; thresholds apply to the same fitted model. ROC-AUC and average precision are reported because thresholded accuracy alone obscures the minority class. A recall target met on validation is not guaranteed on the test set or future data.

## Reproduced test results

| Operating point | Frozen threshold | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Default | 0.50 | 0.613 | 0.243 | 0.348 |
| Validation best F1 | 0.26 | 0.443 | 0.672 | 0.534 |
| Validation recall ≥0.70 target | 0.24 | 0.414 | 0.694 | 0.519 |

The validation-selected logistic regression achieves test **ROC-AUC 0.810** and **average precision 0.494**. The constant-probability baseline has ROC-AUC 0.500 and average precision 0.190. All metrics describe this synthetic split; they are not a demonstrated retention benefit.

## Outputs and interpretation

- `metrics.csv`: model comparison on validation, default threshold 0.5.
- `summary.json`: dataset hash, split counts, selection rule and selected model.
- `feature_importance.csv`: signed logistic coefficients or tree importances, depending on the selected estimator. Numeric inputs are standardized; one-hot category indicators are not. Coefficients are associations under this synthetic model, not causal effects.
- `threshold_grid.csv`: validation precision, recall and F1 over thresholds 0.05–0.95.
- `threshold_summary.json`: validation choices, final test metrics, source/model hashes.
- `test_metrics.csv`, `roc_curve.png`, `confusion_matrix.png`: held-out performance, with the confusion matrix using the validation-selected F1 threshold.
- `best_model.joblib`: local training output; deliberately not distributed in Git. Run training before threshold evaluation.

A single held-out split does not quantify uncertainty across populations or time. If iterating after reviewing test outcomes, establish a fresh untouched holdout before making a new final claim. Real use would require real consented data, temporal validation, calibration checks, and an outreach experiment.
