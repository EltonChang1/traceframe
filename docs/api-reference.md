# API Reference

See `README.md` for the initial API.

## v0.2 additions

- `tf.start(project_name, notebook_name=None)` records a local run.
- `tf.note_cell(...)` attaches manual notebook cell context to later evidence.
- `tf.dataset_statuses()` returns current hash status for tracked datasets.
- `tf.stale_datasets()` returns changed or missing tracked datasets.
