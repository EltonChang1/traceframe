# TraceFrame Handoff Summary

## Current State

TraceFrame is at `1.0.0` on `main`, synced to `origin/main`.

Latest important commits:

- `39bc68b` Harden CLI exits and type checks
- `04400af` Release TraceFrame v1.0 stable local tool
- `651440d` Build TraceFrame v0.6 local assistant planning
- `66cd6ca` Build TraceFrame v0.5 data quality checks
- `844ccef` Build TraceFrame v0.4 Polars support
- `94d077c` Build TraceFrame v0.3 source row evidence

TraceFrame is a local-first Python package for evidence tracking in data science. It stores all project metadata under `.traceframe/` and does not use cloud services or telemetry.

## Verification Baseline

These passed after the latest hardening commit:

```bash
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/black --target-version py311 --check .
.venv/bin/mypy src/traceframe
.venv/bin/python -m pip wheel . -w /tmp/traceframe-wheel
```

Expected test count at handoff: `24 passed`.

Package version checks:

```bash
.venv/bin/python -c "import traceframe, importlib.metadata as m; print(traceframe.__version__); print(m.version('traceframe'))"
```

Expected output:

```text
1.0.0
1.0.0
```

## Core Architecture

Main package: `src/traceframe/`

Key modules:

- `project.py`: initializes/locates `.traceframe/`, project metadata, active project root.
- `storage.py`: JSON read/write/append helpers.
- `evidence.py`: shared `EvidenceRecord` Pydantic model, IDs, timestamps.
- `io.py`: tracked CSV/Parquet readers, pandas and Polars engines, lazy scans.
- `tracking.py`: in-memory tracked objects, transformation tracking, filter tracking.
- `sql.py`: DuckDB SQL over tracked pandas/Polars objects.
- `source_rows.py`: source-row samples, export, chart DuckDB drilldown tables.
- `profiler.py`: pandas/Polars profiling.
- `charts.py`: Altair/Vega-Lite chart evidence.
- `checks.py`: lightweight data quality expectations.
- `claims.py`: written claim records.
- `metrics.py`: metric definition records.
- `runs.py`: run/notebook/cell context.
- `assistant.py`: local-safe heuristic assistant plans and optional user-provided local LLM command.
- `diagnostics.py`: `project_health()` used by `traceframe doctor` and reports.
- `report.py`: gathers metadata and renders HTML.
- `cli.py`: Typer CLI.
- `version.py`: central `__version__`.

Template:

- `src/traceframe/templates/report.html.j2`

## Local Metadata Layout

`traceframe init` / `tf.start(...)` creates `.traceframe/` with JSON metadata and local artifacts:

- `project.json`
- `data_manifest.json`
- `lineage.json`
- `metrics.json`
- `charts.json`
- `claims.json`
- `checks.json`
- `runs.json`
- `cell_events.json`
- `assistant_plans.json`
- `audit_logs/`
- `source_rows/`
- `reports/`

Generated files are ignored by `.gitignore`.

## Public API Surface

Common API:

```python
import traceframe as tf

tf.start("project_name", notebook_name=None)
tf.read_csv("orders.csv", name="orders")
tf.read_parquet("data.parquet", name="data")
tf.read_csv("orders.csv", name="orders", engine="polars")
tf.scan_csv("orders.csv", name="orders_lazy")
tf.scan_parquet("data.parquet", name="data_lazy")

tf.track(obj, name="clean_orders", source="orders", operation="...")
tf.filter_rows(df, "status != 'cancelled'", name="clean_orders")
tf.sql("SELECT ...", name="monthly_revenue")
tf.metric("revenue", "SUM(total_price)", source="clean_orders")
tf.chart(data, x="month", y="revenue", kind="line", name="monthly_chart")
tf.claim("Conclusion text", supports=["monthly_revenue"], confidence="high")
tf.export_report("audit.html")
```

Source rows and drilldown:

```python
tf.export_source_rows("clean_orders", limit=10)
tf.drilldown("monthly_chart", x="month", value="2026-01")
```

Checks:

```python
tf.expect_not_null(data, ["id", "amount"])
tf.expect_no_duplicates(data, subset=["id"])
tf.expect_unique(data, "id")
tf.expect_schema(data, {"id": "int64"})
tf.expect_column_between(data, "amount", min_value=0)
tf.expect("manual_review_complete", True)
```

Assistant:

```python
tf.plan_analysis("Create revenue evidence", data_paths=["orders.csv"])
```

The default assistant is deterministic/local. `local_llm_command` only runs a command explicitly provided by the user.

## CLI Surface

Available commands:

```bash
traceframe init
traceframe profile data.csv
traceframe status
traceframe stale
traceframe source-rows ARTIFACT
traceframe drilldown CHART --x month --value 2026-01
traceframe checks --failed-only
traceframe assist "Build monthly revenue evidence" --data orders.csv
traceframe doctor
traceframe report
traceframe verify ARTIFACT
```

CLI error handling was hardened in `39bc68b`; use `_exit_with_error(...)` in `cli.py` for user-facing failures.

## Examples

Examples live in `examples/`:

- `examples/ecommerce/analysis.py`: richest pandas workflow.
- `examples/polars/analysis.py`: Polars + DuckDB workflow.
- `examples/finance/analysis.py`: small chart/report workflow.
- `examples/aviation/aog_analysis.py`: aviation-flavored metric/chart workflow.

Useful smoke checks:

```bash
cd examples/ecommerce
rm -rf .traceframe ecommerce_audit_report.html
../../.venv/bin/python analysis.py
../../.venv/bin/traceframe doctor
../../.venv/bin/traceframe status
../../.venv/bin/traceframe report

cd ../polars
rm -rf .traceframe polars_audit_report.html
../../.venv/bin/python analysis.py
../../.venv/bin/traceframe doctor
../../.venv/bin/traceframe status
```

## Important Implementation Notes

- Keep TraceFrame local-first. Do not add cloud sync, hosted dashboards, telemetry, or external API calls by default.
- JSON evidence is the source of truth for artifacts.
- In-memory tracking is reset on `tf.start(...)` via `reset_tracking()`.
- `get_project_root()` only reuses the active project when the current path is inside that project, preventing cross-test/project leakage.
- Polars `LazyFrame` support is intentionally schema/sample oriented. Some operations materialize lazy frames where required by DuckDB/Altair/source-row export.
- Chart drilldown uses `.traceframe/source_rows/chart_drilldown.duckdb`.
- `traceframe doctor` uses `diagnostics.project_health()` to report stale datasets, failed checks, and missing evidence files.
- Mypy is configured to suppress third-party untyped import noise with `disable_error_code = ["import-untyped"]`.

## Known Limitations

- No full automatic pandas/Polars operation lineage. Users should call `tf.track(...)` or `tf.filter_rows(...)`.
- Source-row samples are limited samples, not complete row-level lineage.
- Chart drilldown stores chart backing data, not every upstream source row.
- The assistant planner is heuristic by default. Local LLM integration is only a user-provided command.
- No notebook extension or cell execution engine.
- No dbt/Spark/Rust/cloud/enterprise features.
- Reports are static HTML, not an interactive app.

## Good v2 Directions

Strong candidates for v2:

1. **Stronger lineage graph**
   - Query upstream/downstream dependencies by artifact.
   - Add `traceframe lineage ARTIFACT`.
   - Render a simple lineage graph in reports.

2. **Better source-row evidence**
   - Store row IDs/indices more consistently.
   - Add optional larger source-row exports.
   - Add queryable source-row tables for datasets/transforms, not only chart drilldowns.

3. **Notebook ergonomics**
   - Improve notebook detection.
   - Add helpers for cell source hashing.
   - Possibly provide a small Jupyter-friendly API, still no full extension unless requested.

4. **Report improvements**
   - Add collapsible sections.
   - Add richer health summaries.
   - Add links from report rows to local evidence JSON paths.

5. **Data quality expansion**
   - Add grouped checks.
   - Add check suites.
   - Add `traceframe checks --json`.
   - Add severity-based `doctor` exit codes.

6. **Artifact validation**
   - Add schemas for every metadata JSON file.
   - Add `traceframe doctor --repair` for missing initialized files.

7. **Packaging and CI**
   - Add GitHub Actions for tests/lint/type checks.
   - Add release workflow.
   - Add `CHANGELOG.md`.

8. **Docs**
   - Replace placeholder docs with fuller examples.
   - Add generated report screenshot.
   - Add migration/upgrade notes.

## Recommended Next-Agent First Steps

1. Run:

```bash
git status --short --branch
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/black --target-version py311 --check .
.venv/bin/mypy src/traceframe
```

2. Smoke-test `examples/ecommerce` and `examples/polars`.
3. Pick one v2 direction and keep it small, verifiable, and local-first.
4. Add tests before or alongside behavior changes.
5. Push each completed patch.

