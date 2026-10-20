# HR attrition: a synthetic snapshot and offline dashboard

A data-analysis exercise over **1,470 generated employee records**, with a single-file HTML dashboard and manual Power BI/DAX model instructions. This is not real IBM employee data, a completed `.pbix` file, or a deployed Power BI report.

## Run

Install this folder's `requirements.txt` or the repository-wide requirements:

```sh
python generate_hr_data.py
python eda.py
python build_dashboard.py
```

Open `dashboard.html` in a browser. It embeds the dataset and vendored Chart.js 4.4.4, so no CDN or internet connection is needed at runtime. Changing the CSV requires rebuilding the HTML. Source hashes are recorded in `dashboard_manifest.json`; the Chart.js license is retained in `vendor/`.

## Data quality and scope

Age is 20–59. Total working years cannot exceed age minus 18; tenure cannot exceed total working years; time in role, with manager, and since promotion are bounded appropriately. IDs are unique, and missing values, duplicate rows, career consistency, group totals, and embedded-data freshness are checked.

The generator intentionally injects associations into a synthetic attrition flag. That flag has no departure date or observation period; **15.24% of this snapshot is flagged**, which is not an annual attrition rate. Role, compensation, and career patterns remain simplified and do not recreate a real workforce.

## Reproduced descriptive findings

| Synthetic segment | Flag rate | Group size |
|---|---:|---:|
| Entire snapshot | 15.24% | 1,470 |
| Overtime: Yes | 23.02% | 391 |
| Overtime: No | 12.42% | 1,079 |
| Age 20–29 | 25.33% | 383 |
| Age 50+ | 10.06% | 338 |

These patterns reflect the data generator. They do not establish that changing overtime causes departures to fall. Check group sizes and avoid conclusions based on tiny slices.

## Dashboard

- Department, overtime, gender and business-travel filters update all cards/charts.
- Counts and rates can be inspected in a department table.
- Filtered CSV export includes only the currently selected rows.
- Buttons support keyboard focus and pressed-state announcements; selection counts use a live status region.
- Phone-width layouts stack cards/charts without horizontal page overflow.
- Empty selections show N/A for undefined averages and rates.

The Python, HTML and Power BI instructions use identical band boundaries. The final tenure band is **11+**. See `dax_measures.md` for the snapshot model; time-intelligence measures are intentionally omitted because dates are absent.
