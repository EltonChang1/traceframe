# API Reference

See `README.md` for the initial API.

## v0.2 additions

- `tf.start(project_name, notebook_name=None)` records a local run.
- `tf.note_cell(...)` attaches manual notebook cell context to later evidence.
- `tf.dataset_statuses()` returns current hash status for tracked datasets.
- `tf.stale_datasets()` returns changed or missing tracked datasets.

## v0.3 additions

- `tf.filter_rows(df, condition, name=None, source=None)` applies a pandas query and records the filter condition.
- `tf.export_source_rows(artifact_id_or_name, path=None, limit=None)` exports a stored source-row sample.
- `tf.drilldown(chart_id_or_name, x=None, value=None, limit=20)` queries a chart's local DuckDB backing table.

## v0.4 additions

- `tf.read_csv(path, name=None, engine="polars", lazy=False)` tracks Polars CSV reads.
- `tf.read_parquet(path, name=None, engine="polars", lazy=False)` tracks Polars Parquet reads.
- `tf.scan_csv(path, name=None)` tracks a Polars LazyFrame scan.
- `tf.scan_parquet(path, name=None)` tracks a Polars LazyFrame scan.

## v0.5 additions

- `tf.expect_not_null(data, columns)` records null checks.
- `tf.expect_no_duplicates(data, subset=None)` records duplicate-row checks.
- `tf.expect_unique(data, columns)` records unique-key checks.
- `tf.expect_schema(data, schema)` records type/schema checks.
- `tf.expect_column_between(data, column, min_value=None, max_value=None)` records threshold checks.
- `tf.expect(name, passed, ...)` records a generic local expectation.

## v0.6 additions

- `tf.plan_analysis(request, data_paths=None, local_llm_command=None)` creates local assistant plan records.
- `traceframe assist "request" --data orders.csv` prints and stores a local plan.
- `--local-llm-command` is optional and runs only the command you provide.
