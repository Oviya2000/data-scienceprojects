# Improvements in this revision

## Churn

Replaced test-set model/threshold selection with separate training, validation and test sets. Added a reproducible split manifest, source hashes, independent preprocessing per candidate, validation threshold selection, average precision, a constant-probability baseline, and clearly labeled final test metrics. Removed the distributed serialized model; it is regenerated locally.

## Retail

Q10 now counts the first order and includes genuine three-order customers. Window ties have explicit IDs where customer segmentation depends on ordering. Q6 now uses every signup in the denominator and leaves future unobserved horizons blank. Documentation distinguishes observed spend from predicted lifetime value and acknowledges SQLite-specific expressions.

## HR

Constrained tenure and total work experience by age; rebuilt the synthetic snapshot and all findings. Matched band boundaries across Python, HTML and Power BI instructions. Added an offline dashboard builder, CSV export, empty-slice handling, accessible filter state, a counts table, and responsive layout. Removed unsupported dated-event/time-intelligence claims from Power BI instructions.

## Weather

Separated mock and live modes, retained per-row provenance, added robust timestamp/numeric validation, required real Parquet, partitioned by each observation's UTC date, and made object naming repeatable per run. Repaired the local error-loop/terminal-failure behavior and added tests for failure paths. Narrowed the source template's load permissions and documented unverified AWS packaging/partition-registration work.

## Repository

Added a main project index, pinned dependencies, one-command regeneration, regression checks, optional network-blocked browser checks, and a GitHub Actions workflow. Generated SQLite databases, caches, weather outputs and model binaries are ignored. No live deployment, real-customer outcome, native Power BI report or revenue gain is claimed.
