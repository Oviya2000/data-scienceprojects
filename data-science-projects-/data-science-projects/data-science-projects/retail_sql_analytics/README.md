# Retail SQL analytics

Ten executable SQLite analyses over generated retail data: 5,000 customers, 500 products, 10 categories, 11,430 orders and 28,478 order lines. The observed orders cover September 2024 through August 2026. All records and business outcomes are synthetic.

## Run

Install this folder's `requirements.txt` or the repository-wide requirements:

```sh
python build_db.py
python run_queries.py
```

`build_db.py` replaces the local generated `retail.db`; the database is not committed. Foreign-key enforcement is enabled during generation. `run_queries.py` writes ten CSVs to `results/`.

## Query guide

| Query | Question | Definition or caveat |
|---|---|---|
| Q1 | Monthly revenue and growth | Distinct orders/customers; first growth value is NULL |
| Q2 | Top products | Share denominator includes all product revenue |
| Q3 | Category revenue | Running sum and share of total |
| Q4 | Customer spend deciles | Observed spend among purchasers, not predicted lifetime value |
| Q5 | RFM segments | Snapshot at 2026-09-01; purchaser-only population; deterministic customer-ID tie breaks |
| Q6 | Signup-cohort activity | All signups in denominator; not-yet-observed horizons remain NULL |
| Q7 | Repeat purchases by country | At least two orders / all signed-up customers |
| Q8 | Two leading products per category | Per-category window ranking |
| Q9 | Basket value and gross margin | Generated catalog prices/costs; not net profit |
| Q10 | Days between orders | Counts all orders, including the first purchase; average uses only consecutive gaps |

Q6 rates are activity among the signup cohort at a given month offset, not retention of month-zero purchasers. Horizon eligibility is based on the last observed calendar month; a real production report should use an explicit data-completeness watermark. Do not treat an unobserved future month as zero activity. Q10 orders on the same date are ordered by order_id to keep the window deterministic.

These queries use SQLite-specific `strftime`, `julianday`, and date modifiers. Port the date expressions and validate outputs before using PostgreSQL; unchanged cross-database compatibility is not claimed.

## Checks

The repository regression suite verifies database integrity, foreign keys, revenue reconciliation across queries, full customer counts in Q10, cohort denominators, and NULL future horizons. See the top-level README for commands.
