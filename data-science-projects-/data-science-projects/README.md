# Oviya Elangovan · Data Science Projects

Four reproducible learning projects covering SQL, predictive modelling, dashboard design, and data pipelines. Each project has its own source code, input generator, results, and README.

**All customer and employee datasets are synthetic.** Weather runs use explicit mock data by default. Results demonstrate implementations, not outcomes achieved at a real company.

| Project | Focus | Start here |
|---|---|---|
| [Retail SQL analytics](data-science-projects/retail_sql_analytics) | Ten queries, cohort denominators, RFM, window functions | [Query book](data-science-projects/retail_sql_analytics/queries.sql) |
| [Telco churn](data-science-projects/telco_churn_prediction) | Train/validation/test separation, baselines, frozen thresholds | [Held-out results](data-science-projects/telco_churn_prediction/test_metrics.csv) |
| [HR attrition](data-science-projects/hr_attrition_dashboard) | Data-quality constraints, offline dashboard, DAX instructions | Download and open `dashboard.html` inside that folder |
| [Weather ETL](data-science-projects/weather_etl_aws) | Validation, Parquet partitions, bounded retry/failure paths | [Local runner](data-science-projects/weather_etl_aws/local_run.py) |

## Run everything locally

Python **3.12** is the tested version. Download/clone this repository and open a terminal in its top-level folder:

```sh
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```sh
source .venv/bin/activate
```

Then:

```sh
python -m pip install -r requirements.txt
python -X utf8 run_all.py
```

This regenerates all datasets/results, builds the offline HR dashboard, trains the models, runs the local mock-weather pipeline, and executes the analytical and weather regression checks. It overwrites generated outputs. It **does not deploy AWS resources** or require credentials. Internet is required to install dependencies; runtime uses local/synthetic inputs by default.

Each project also has its own `requirements.txt` if you want to install only its dependencies. SQLite is included with Python. Joblib model files are generated locally and excluded from Git; never load a model file from an untrusted source.

## Dashboard

Open `data-science-projects/hr_attrition_dashboard/dashboard.html` in a browser. The finished HTML embeds both the current generated dataset and Chart.js 4.4.4, so it works offline. GitHub's file viewer shows HTML source; download it first. Power BI model instructions are supplied; no `.pbix` report is claimed.

## Verification

The `Portfolio checks` workflow installs the pinned runtime dependencies and runs `run_all.py` on Python 3.12. For optional real-browser checks:

```sh
python -m pip install -r requirements-browser.txt
python -m playwright install chromium --only-shell
python tests/check_dashboard.py
```

Browser tests run with networking blocked, verify every filter combination, compare chart data to the CSV, reconcile downloads, and check phone-width layout. See [VALIDATION.md](VALIDATION.md) for the tested scope and limits.

## Analytical boundaries

- Synthetic churn labels are generated from known rules. Test-set metrics measure recovery of a simulated pattern, not real-world generalization.
- HR is a single synthetic snapshot. Its flag is not a dated departure event, annual turnover rate, or basis for individual employment decisions.
- Retail revenue and margin come from a simulated fixed-price catalog. Customer spend is observed historical spend, not a forecast of lifetime value.
- Weather AWS templates are supplied for inspection. Local mock execution and a local ASL subset interpreter do not validate AWS packaging, permissions, orchestration equivalence, service costs, or deployment.

Prepared with AI-assisted implementation and review. Before presenting a project, reproduce it and be ready to explain the choices and limitations.
