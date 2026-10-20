# Validation scope

Local checks performed on 2026-10-20 using Python 3.12 and the versions pinned in `requirements.txt`.

## Rebuilt and checked

- All four project entry points executed successfully with local/synthetic inputs.
- Retail: database integrity and foreign keys; raw-vs-aggregate revenue; Q10 counts including first purchases; cohort denominators and NULL unobserved horizons.
- Churn: separate stratified 60/20/20 customer splits; preprocessing fitted on training only; model selection and threshold choice based on validation only; final test results and a prevalence baseline.
- HR: unique IDs, complete values, career-length consistency, matching CSV/embedded data, aggregate denominator reconciliation and matching Python/HTML band boundaries.
- Weather: explicit mock provenance, no live-to-mock fallback, malformed/nonfinite observations, timezone-aware timestamps, partition dates, repeat-run keys, retries, empty records and notification followed by terminal failure.

The core suite has **9 analytical regression checks** and the weather suite has **9 tests**. Run `python -X utf8 run_all.py` to rebuild and execute them.

## Optional browser checks

`tests/check_dashboard.py` blocks HTTP/HTTPS requests, checks all **144** combinations of selected/unselected filters, compares KPI and chart data against the source CSV, reconciles an exported CSV by EmployeeID, and checks page overflow at 320, 390, 768 and 1440 px. It requires the optional browser dependencies and a Chromium download.

## Limits

No AWS account deployment, SAM build, Athena execution, or Power BI Desktop report was verified. Browser tests cover core interactions and widths; they are not a full screen-reader/accessibility audit. Runtime tests do not establish real business value, causal relationships, or generalization beyond the synthetic data generator. GitHub CI results must be checked after publication; local success is not a remote workflow run.
