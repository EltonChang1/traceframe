# Evidence Model

Evidence records are JSON documents that describe datasets, transformations, metrics, charts, claims, and SQL results.

In v0.2, evidence records can include a `run_id` plus execution context metadata. This keeps notebook/script provenance local and inspectable.

In v0.3, DataFrame-like artifacts can include `source_rows` metadata pointing to local JSON samples under `.traceframe/source_rows/`. Chart evidence can also include `drilldown` metadata pointing to a local DuckDB table.

In v0.4, profiling metadata includes an `engine` field for pandas, Polars, and Polars LazyFrame artifacts.

In v0.5, data quality checks are stored in `.traceframe/checks.json` and mirrored as `check` evidence records.
