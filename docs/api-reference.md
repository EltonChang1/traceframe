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
