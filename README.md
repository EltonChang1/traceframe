# TraceFrame

[![Test](https://github.com/EltonChang1/traceframe/actions/workflows/test.yml/badge.svg)](https://github.com/EltonChang1/traceframe/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

TraceFrame is a local-first evidence tracker for data science workflows. It records datasets, transformations, SQL outputs, metrics, charts, claims, checks, source-row samples, and lineage under a project-local `.traceframe/` directory.

No cloud service, telemetry, or external API call is used by default.

## Install

```bash
pip install -e .
```

Python 3.10+ is required.

## Minimal Workflow

```python
import traceframe as tf

tf.start("revenue_analysis")

orders = tf.read_csv("orders.csv", name="orders")
clean_orders = tf.filter_rows(
    orders,
    "status == 'complete'",
    name="clean_orders",
)

tf.expect_not_null(clean_orders, ["order_id", "total_price"])
tf.expect_unique(clean_orders, "order_id")
tf.metric("revenue", "SUM(total_price)", source="clean_orders")

monthly = tf.sql(
    """
    SELECT strftime('%Y-%m', CAST(order_date AS DATE)) AS month,
           SUM(total_price) AS revenue
    FROM clean_orders
    GROUP BY 1
    ORDER BY 1
    """,
    name="monthly_revenue",
)

tf.chart(monthly, x="month", y="revenue", kind="line", name="monthly_revenue_chart")
tf.claim("Revenue is calculated from complete orders.", ["monthly_revenue"], "high")
tf.export_report("audit_report.html")
```

## Python API

Project and data:

```python
tf.start("project_name", notebook_name=None)
tf.read_csv("orders.csv", name="orders")
tf.read_parquet("orders.parquet", name="orders")
tf.read_csv("orders.csv", name="orders", engine="polars")
tf.scan_csv("orders.csv", name="orders_lazy")
tf.track(df, name="clean_orders", source="orders", operation="drop_duplicates")
tf.filter_rows(df, "total_price >= 100", name="large_orders")
```

Evidence:

```python
tf.sql("SELECT ... FROM clean_orders", name="monthly_revenue")
tf.metric("revenue", "SUM(total_price)", source="clean_orders")
tf.chart(monthly, x="month", y="revenue", kind="bar", name="monthly_chart")
tf.claim("Conclusion text", supports=["monthly_revenue"], confidence="high")
tf.export_report("audit_report.html")
```

Checks:

```python
tf.expect_not_null(df, ["id", "amount"])
tf.expect_unique(df, "id")
tf.expect_no_duplicates(df, subset=["id"])
tf.expect_schema(df, {"id": "int64"})
tf.expect_column_between(df, "amount", min_value=0)
tf.expect("manual_review_complete", True)
```

Lineage and source rows:

```python
tf.lineage_graph("monthly_revenue", direction="upstream")
tf.export_source_rows("clean_orders", limit=10)
tf.drilldown("monthly_chart", x="month", value="2026-01")
```

Notebook context:

```python
tf.start("revenue_analysis", notebook_name="revenue_analysis.ipynb")
tf.note_cell(cell_id="metric-cell", execution_count=7, tags=["metric"])
```

Local assistant planning:

```python
tf.plan_analysis(
    "Create monthly revenue evidence with checks and a chart",
    data_paths=["orders.csv"],
)
```

The default planner is deterministic and local. `local_llm_command` runs only when explicitly provided by the caller.

## CLI

```bash
traceframe init
traceframe profile data/orders.csv
traceframe status
traceframe stale
traceframe lineage monthly_revenue --direction upstream
traceframe lineage orders --direction downstream --depth 1
traceframe lineage monthly_revenue --json
traceframe lineage monthly_revenue --json --include-metadata
traceframe source-rows clean_orders --limit 10
traceframe drilldown monthly_chart --x month --value 2026-01
traceframe checks --failed-only
traceframe assist "Build monthly revenue evidence" --data orders.csv
traceframe doctor
traceframe report
traceframe verify monthly_revenue
```

## Metadata Layout

TraceFrame stores project evidence in `.traceframe/`:

```text
.traceframe/
  project.json
  data_manifest.json
  lineage.json
  metrics.json
  charts.json
  claims.json
  checks.json
  runs.json
  cell_events.json
  assistant_plans.json
  audit_logs/
  source_rows/
  reports/
```

JSON metadata is the source of truth. Source-row samples are stored locally as JSON. Chart drilldown data is stored in a local DuckDB database under `.traceframe/source_rows/`.

## Verification

```bash
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/black --target-version py311 --check .
.venv/bin/mypy src/traceframe
```

## Current MVP Surface (v0.1)

TraceFrame tracks explicit local evidence for pandas, DuckDB SQL, and Polars workflows. It does not provide automatic full operation tracing, cloud sync, hosted dashboards, telemetry, notebook extensions, or complete row-level lineage.

## License

TraceFrame is released under the [MIT License](LICENSE).

## Documentation

- [Getting started](docs/getting-started.md)
- [API reference](docs/api-reference.md)
- [Evidence model](docs/evidence-model.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
