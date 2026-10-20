# Power BI model for the supplied synthetic snapshot

A `.pbix` report is not included. These are manual Power BI Desktop build instructions; the delivered working dashboard is `dashboard.html`.

## Model and scope

Import `hr_attrition.csv` as **FactEmployee**, one row per EmployeeID. Set age, income, tenure, job level and satisfaction fields to Whole Number; categorical fields to Text. Verify EmployeeID uniqueness and the expected row count in `data_quality.json`.

Use a single flat snapshot table for this small dataset. Do not add hire/termination dates or time-intelligence measures: those source fields do not exist. The Attrition flag is a synthetic outcome indicator, not a dated departure event or annual attrition rate.

Optional dimensions for Department and JobRole must have unique keys and one-to-many, single-direction relationships to FactEmployee. Keep the following baseline measure aligned with whichever model you build.

## Add measures one at a time

```DAX
Employees = COUNTROWS(FactEmployee)
Leavers = CALCULATE(COUNTROWS(FactEmployee), FactEmployee[Attrition] = "Yes")
Stayers = [Employees] - [Leavers]
Attrition Rate = DIVIDE([Leavers], [Employees])
Avg Monthly Income = AVERAGE(FactEmployee[MonthlyIncome])
Avg Tenure Years = AVERAGE(FactEmployee[YearsAtCompany])
Company Attrition Rate = CALCULATE([Attrition Rate], REMOVEFILTERS())
Difference vs Company = [Attrition Rate] - [Company Attrition Rate]
```

Format Attrition Rate as a percentage. Format Difference vs Company as percentage points, not relative growth. Leave empty slices blank rather than showing zero attrition for a group with no employees.

## Bands: identical to Python and HTML

| Band | Definition |
|---|---|
| Age | [20,30), [30,40), [40,50), [50,100) |
| Tenure | [0,3), [3,6), [6,11), [11,100) |
| Income | [0,3000), [3000,5000), [5000,8000), [8000,12000), [12000,∞) |

Create columns with nested `if` statements in Power Query, using `<` for each successive upper boundary. Label the final tenure group **11+**. Denominators are group headcounts, not all-company headcount.

## Recreate and reconcile

Use Department, OverTime, Gender, and BusinessTravel slicers. Add cards for headcount, leavers, attrition rate, average income, and average tenure. Add department counts and job-role/age/tenure/income/overtime/travel rates. Compare unfiltered cards and selected slices with `dashboard.html` and aggregate CSVs. Display group size alongside every rate, particularly for small slices.

This dataset supports a descriptive snapshot only. Do not present generated associations as real-world causes, interventions, individual employment decisions, or a forecast of actual departures.
