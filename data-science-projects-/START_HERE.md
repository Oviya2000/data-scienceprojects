# Use the improved projects

The `improved-data-science-projects` folder contains the complete updated repository, including the offline HR dashboard. Start with its README.

## Run locally

Open a terminal inside that folder, install `requirements.txt` in a Python 3.12 virtual environment, then run:

```sh
python -X utf8 run_all.py
```

## Update the existing GitHub repository

GitHub denied the connected integration permission to create an update branch, so these changes have not been pushed. The patch is based on commit aa31364e58dc486b107bec0de0e247651ae68894 of Oviya2000/data-science-projects1.

If you have Git installed, use a fresh clone to avoid overwriting local work:

```sh
git clone https://github.com/Oviya2000/data-science-projects1.git portfolio-update
cd portfolio-update
git switch -c improve-project-quality
git apply --check "/absolute/path/to/portfolio-improvements.patch"
git apply "/absolute/path/to/portfolio-improvements.patch"
git add -A
git commit -m "Improve project evaluation, analytics, dashboard and pipeline reliability"
git push -u origin improve-project-quality
```

Replace the quoted patch path with the actual extracted file path; a Windows path also works in Git for Windows. If the check fails, stop and inspect the conflict rather than forcing the patch. The final push uses your normal GitHub sign-in. Open the branch on GitHub and create a pull request into main to review the changes.

Alternatively, upload the **contents** of `improved-data-science-projects` to the existing repository while preserving paths. Do not add another extra project folder around those contents. If using manual upload, separately remove the old `data-science-projects/telco_churn_prediction/best_model.joblib`; uploads do not delete files. This model is regenerated locally and intentionally excluded from the update.

The package includes 82 repository files, but GitHub upload limits and file selection behavior may vary. The patch route preserves additions, changes and the model-file removal together.

## Validation

All four projects rebuilt. Eighteen analytical/weather tests passed. The offline HR dashboard passed all 144 filter combinations, CSV reconciliation and widths 320/390/768/1440 with zero external requests. AWS deployment and native Power BI reports remain unverified.
