# Weather ETL: explicit provenance and testable failure paths

A local weather pipeline and an undeployed AWS SAM template for fetch → validate → transform → partitioned Parquet. The AWS design uses Lambda, Step Functions, S3, Glue, Athena and SNS. **No AWS deployment or production readiness is claimed.**

## Local setup and execution

Install this folder's `requirements.txt` or the repository-wide requirements, then run here:

```sh
python local_run.py
python tests/run_tests.py
```

The default command explicitly uses **mock** readings for ten fixed cities and writes local Parquet. `data_source=mock` is retained in every record. It clears AWS bucket/topic environment variables so this entry point cannot upload or send notifications accidentally.

For a deliberate live API run:

```sh
python local_run.py --live
```

Live mode requests public Open-Meteo weather. A failed API request raises an error; it is never silently replaced by mock observations. Mock readings demonstrate the pipeline only and are not current weather.

## Changes that matter

- Validator rejects missing fields, nonnumeric/boolean/nonfinite measurements, out-of-range values, and invalid or timezone-free timestamps without crashing on a bad row.
- UTC observation date determines each partition. A batch spanning midnight creates separate partition files.
- PyArrow writes genuine Parquet with a schema matching the Glue fields. There is no JSONL fallback under a `.parquet` contract. Install dependencies before running.
- Names include a hash of run_id. Retrying the same run and partition reuses the object key; different run IDs are separated. This is not a full exactly-once ingestion guarantee.
- Failure notification leads to a terminal **Fail** state; the local runner no longer loops when error context reaches the notification handler.
- Local tests exercise malformed rows, mock provenance, live-fetch failure, partition boundaries, retries, empty batches and terminal failure.

The local runner supports only the Task/Choice/Pass/Fail patterns used by this repository. It is not a general Step Functions emulator and does not validate every AWS retry/error/result-path semantic.

## AWS scope and remaining work

`template.yaml` includes the service definitions and `lambdas/requirements.txt` includes runtime packaging dependencies. Fetch has no S3 write policy; load requests S3 write access rather than a broad Glue console policy. Inspect and validate all resource permissions before deployment.

AWS SAM, CloudFormation, Lambda packaging, account permissions, live Step Functions executions and Athena queries have **not** been tested in an AWS account. Before deploying:

1. Run SAM build/validation for the intended platform, review the generated artifacts, and verify the PyArrow dependency fits the runtime/package limits.
2. Choose a unique bucket name and inspect the deployment changeset and expected charges.
3. Run a sandbox execution and inspect the typed Parquet/Glue compatibility.
4. Register new partitions in Glue (for example with Athena `MSCK REPAIR TABLE`) or implement projection. The loader does **not** automatically repair partitions.
5. Configure and verify an SNS subscription if notifications are required. No Slack integration is included.

The `raw/` lifecycle rule in the template does not apply to curated outputs. This implementation writes only `curated/`; retention and costs require a separate policy. Do not assume the pipeline is free to operate.

## External API

Open-Meteo endpoint: https://api.open-meteo.com/v1/forecast. Follow its applicable attribution and usage terms for any deployed use. Source fields are tagged `open-meteo`; deterministic fixtures are tagged `mock`.
