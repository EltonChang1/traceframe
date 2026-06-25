# TraceFrame — Local-First Evidence Tracking for Data Science

## Recommended repository name

**Repo name:** `traceframe`

## One-line description

**TraceFrame is a local-first, open-source developer tool for data scientists and data analysts that records the evidence behind every dataset, transformation, metric, chart, and conclusion.**

## Product positioning

TraceFrame is not a dashboard tool, not a no-code BI product, and not a replacement for pandas, Polars, DuckDB, Jupyter, or SQL.

TraceFrame is an **evidence layer** for technical data work.

It lets data scientists and analysts keep coding normally while automatically producing:

- dataset fingerprints
- transformation lineage
- metric definitions
- chart evidence cards
- source-row references
- claim/conclusion evidence
- reproducibility metadata
- local HTML audit reports

The product should run entirely on the user's local machine by default.

No user data should leave the local machine.

---

# 1. Problem

Technical data scientists and analysts already use Python, SQL, pandas, Polars, DuckDB, notebooks, and BI tools. Their problem is not that they cannot analyze data.

Their problem is that analysis is often hard to verify, reproduce, explain, and hand off.

Common pain points:

1. A chart is created, but later nobody knows exactly which data rows, filters, or transformations produced it.
2. A notebook works once, but cannot be reliably rerun because cells were executed out of order.
3. A metric like revenue, churn, retention, margin, or risk score is defined differently across notebooks.
4. A written conclusion in a report is not linked to the actual computation that supports it.
5. A data file changes and old results silently become stale.
6. An analyst has to manually answer, “Where did this number come from?”
7. Work done in notebooks is hard to convert into a trustworthy report or production workflow.

TraceFrame should solve this by making every result traceable and reproducible by default.

---

# 2. Core product promise

A user should be able to run TraceFrame locally and answer:

> “Where did this number, chart, model result, or conclusion come from?”

TraceFrame should show:

- source dataset
- file hash/version
- row count
- schema
- cleaning steps
- transformations
- filters
- metric formula
- generated SQL/Python evidence
- chart configuration
- source rows used
- assumptions
- reproducibility command

---

# 3. Target users

Primary users:

- data scientists
- data analysts
- analytics engineers
- ML engineers
- technical consultants
- researchers
- technical founders doing data analysis

Secondary users:

- finance analysts
- operations analysts
- aviation/logistics analysts
- healthcare/regulated-data analysts
- teams that need local/private data workflows

The tool must be code-first. Do not build a no-code app in the MVP.

---

# 4. Design principles

## 4.1 Local-first

TraceFrame must run locally.

Default behavior:

- no cloud account
- no hosted service
- no telemetry by default
- no uploading user data
- no external API calls required
- outputs stored in the local project directory

## 4.2 Developer-first

TraceFrame should fit into existing workflows:

- Python scripts
- Jupyter notebooks
- pandas
- Polars
- DuckDB
- SQL files
- local CSV/Excel/Parquet files

The user should not need to learn a new programming language for v0.1.

## 4.3 Evidence-first

Every important result should have an evidence record.

Evidence records should be stored in structured JSON so future tools can inspect, validate, diff, or render them.

## 4.4 Minimal friction

The API should feel simple:

```python
import traceframe as tf

tf.start("revenue_analysis")

orders = tf.read_csv("orders.csv")

clean = tf.track(
    orders.drop_duplicates("order_id").query("status != 'cancelled'"),
    name="clean_orders"
)

monthly = tf.sql("""
    SELECT month, SUM(revenue) AS revenue
    FROM clean_orders
    GROUP BY month
""", name="monthly_revenue")

tf.chart(monthly, x="month", y="revenue", kind="line")

tf.claim(
    "Revenue declined in June because enterprise order volume dropped.",
    supports=["monthly_revenue"]
)

tf.export_report("audit_report.html")
```

## 4.5 Use existing fast engines

Do not build a data engine from scratch.

Use:

- pandas compatibility
- Polars for fast profiling/cleaning
- DuckDB for local SQL analytics
- Altair/Vega-Lite for chart specs
- Jinja2 for HTML reports

---

# 5. MVP scope

The first MVP should prove this workflow:

> local file → tracked dataset → tracked transformation → metric/query → chart → claim → audit report → verify result

## Must-have v0.1 features

1. `traceframe init`
2. `.traceframe/` local metadata directory
3. `tf.start(project_name)`
4. `tf.read_csv(path)`
5. `tf.read_parquet(path)`
6. dataset fingerprinting
7. basic dataset profiling
8. `tf.track(obj, name=...)`
9. `tf.sql(query, name=...)` using DuckDB
10. `tf.metric(name, formula, source, description=None)`
11. `tf.chart(data, x, y, kind, title=None)`
12. `tf.claim(text, supports, confidence=None)`
13. `tf.export_report(path)`
14. `traceframe status`
15. `traceframe verify <artifact_id>`
16. local HTML audit report
17. JSON evidence files

## Out of scope for v0.1

Do not implement these in the first version:

- cloud sync
- hosted dashboard
- user accounts
- AI assistant
- Rust core
- Spark integration
- dbt integration
- full Jupyter extension
- enterprise permissions
- full automatic lineage tracking for all pandas operations
- automatic source-row extraction for every possible operation
- complex visualization builder
- full notebook execution engine

---

# 6. Recommended tech stack

## Main language

Use **Python** for v0.1.

Reason:

- target users are Python-heavy
- easiest adoption by data scientists
- easiest integration with pandas, Polars, DuckDB, Jupyter
- fastest MVP implementation

## Dependencies

Use the following dependencies in `pyproject.toml`:

```toml
dependencies = [
    "duckdb",
    "polars",
    "pandas",
    "pyarrow",
    "openpyxl",
    "typer",
    "rich",
    "pydantic",
    "jinja2",
    "altair"
]
```

Optional development dependencies:

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "ruff",
    "mypy",
    "black"
]
```

## Why not Rust first?

Rust can be added later for:

- fast hashing
- dataset diffing
- lineage graph performance
- standalone binary
- efficient source-row indexing

But v0.1 should be Python-only.

---

# 7. Repository structure

Create the repo as:

```text
traceframe/
├── README.md
├── LICENSE
├── pyproject.toml
├── CONTRIBUTING.md
├── ROADMAP.md
├── .gitignore
├── docs/
│   ├── getting-started.md
│   ├── local-first.md
│   ├── evidence-model.md
│   ├── api-reference.md
│   └── examples.md
├── examples/
│   ├── ecommerce/
│   │   ├── orders.csv
│   │   └── analysis.py
│   ├── finance/
│   │   ├── revenue.csv
│   │   └── analysis.py
│   └── aviation/
│       ├── maintenance.csv
│       └── aog_analysis.py
├── src/
│   └── traceframe/
│       ├── __init__.py
│       ├── cli.py
│       ├── project.py
│       ├── storage.py
│       ├── fingerprint.py
│       ├── profiler.py
│       ├── io.py
│       ├── tracking.py
│       ├── sql.py
│       ├── metrics.py
│       ├── charts.py
│       ├── claims.py
│       ├── lineage.py
│       ├── evidence.py
│       ├── report.py
│       └── templates/
│           └── report.html.j2
├── tests/
│   ├── test_fingerprint.py
│   ├── test_profiler.py
│   ├── test_project.py
│   ├── test_io.py
│   ├── test_sql.py
│   ├── test_metrics.py
│   ├── test_charts.py
│   ├── test_claims.py
│   └── test_report.py
└── outputs/
    └── .gitkeep
```

---

# 8. Local project directory

When a user runs:

```bash
traceframe init
```

TraceFrame should create:

```text
.traceframe/
├── project.json
├── data_manifest.json
├── lineage.json
├── metrics.json
├── charts.json
├── claims.json
├── runs/
├── reports/
├── source_rows/
└── audit_logs/
```

## File responsibilities

### `.traceframe/project.json`

Stores project-level metadata.

Example:

```json
{
  "project_name": "revenue_analysis",
  "created_at": "2026-06-24T00:00:00Z",
  "traceframe_version": "0.1.0"
}
```

### `.traceframe/data_manifest.json`

Stores dataset fingerprints.

Example:

```json
{
  "datasets": [
    {
      "id": "ds_orders_001",
      "name": "orders",
      "path": "orders.csv",
      "file_hash": "sha256:abc123",
      "row_count": 128392,
      "column_count": 12,
      "schema": {
        "order_id": "string",
        "order_date": "datetime",
        "revenue": "float"
      },
      "created_at": "2026-06-24T00:00:00Z"
    }
  ]
}
```

### `.traceframe/lineage.json`

Stores transformations and dependency graph.

Example:

```json
{
  "nodes": [
    {"id": "ds_orders_001", "type": "dataset", "name": "orders"},
    {"id": "tf_clean_orders_001", "type": "transformation", "name": "clean_orders"}
  ],
  "edges": [
    {"from": "ds_orders_001", "to": "tf_clean_orders_001", "type": "derived_from"}
  ]
}
```

### `.traceframe/metrics.json`

Stores metric definitions.

Example:

```json
{
  "metrics": [
    {
      "id": "metric_revenue",
      "name": "revenue",
      "formula": "SUM(total_price)",
      "source": "clean_orders",
      "description": "Total non-cancelled order revenue"
    }
  ]
}
```

### `.traceframe/charts.json`

Stores chart evidence cards.

Example:

```json
{
  "charts": [
    {
      "id": "chart_monthly_revenue_001",
      "title": "Monthly Revenue",
      "kind": "line",
      "x": "month",
      "y": "revenue",
      "source": "monthly_revenue",
      "evidence_id": "ev_chart_monthly_revenue_001"
    }
  ]
}
```

### `.traceframe/claims.json`

Stores written claims and supporting evidence.

Example:

```json
{
  "claims": [
    {
      "id": "claim_001",
      "text": "Revenue declined in June because enterprise order volume dropped.",
      "supports": ["monthly_revenue", "chart_monthly_revenue_001"],
      "confidence": "medium"
    }
  ]
}
```

---

# 9. Core Python API

## 9.1 `tf.start(project_name: str)`

Initializes or loads a local TraceFrame project.

Expected behavior:

- create `.traceframe/` if missing
- write/update project metadata
- set global active project context

Example:

```python
tf.start("revenue_analysis")
```

## 9.2 `tf.read_csv(path: str, name: str | None = None)`

Reads a CSV file and tracks it.

Expected behavior:

- load into pandas DataFrame initially
- calculate file hash
- infer schema
- count rows/columns
- profile missing values
- register dataset in `data_manifest.json`
- return pandas DataFrame

Example:

```python
orders = tf.read_csv("orders.csv", name="orders")
```

## 9.3 `tf.read_parquet(path: str, name: str | None = None)`

Reads a Parquet file and tracks it.

Expected behavior should mirror `read_csv`.

## 9.4 `tf.track(obj, name: str, source: str | None = None, operation: str | None = None)`

Registers a transformation result.

Expected behavior:

- store object metadata
- store row count and column count if object is DataFrame-like
- store basic schema
- create lineage node
- create lineage edge if source is provided
- return original object unchanged

Example:

```python
clean_orders = tf.track(
    orders.drop_duplicates("order_id"),
    name="clean_orders",
    source="orders",
    operation="drop_duplicates(order_id)"
)
```

## 9.5 `tf.sql(query: str, name: str)`

Runs SQL locally using DuckDB.

Expected behavior:

- register currently tracked DataFrames as DuckDB tables
- execute query
- store SQL text
- store result metadata
- register result in lineage graph
- return pandas DataFrame

Example:

```python
monthly = tf.sql("""
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(revenue) AS revenue
    FROM clean_orders
    GROUP BY 1
    ORDER BY 1
""", name="monthly_revenue")
```

## 9.6 `tf.metric(name: str, formula: str, source: str, description: str | None = None)`

Registers a metric definition.

Example:

```python
tf.metric(
    name="revenue",
    formula="SUM(total_price)",
    source="clean_orders",
    description="Total non-cancelled order revenue"
)
```

## 9.7 `tf.chart(data, x: str, y: str, kind: str, title: str | None = None, name: str | None = None)`

Creates a chart evidence record.

For v0.1, this function does not need to render charts interactively. It should generate and save an Altair/Vega-Lite spec and metadata.

Supported chart kinds for v0.1:

- line
- bar
- scatter

Expected behavior:

- generate chart ID
- save Vega-Lite spec
- store source data reference
- store x/y fields
- create evidence record
- return chart object/spec

Example:

```python
tf.chart(
    monthly,
    x="month",
    y="revenue",
    kind="line",
    title="Monthly Revenue",
    name="monthly_revenue_chart"
)
```

## 9.8 `tf.claim(text: str, supports: list[str], confidence: str | None = None)`

Registers a written conclusion and links it to supporting results.

Example:

```python
tf.claim(
    "Revenue declined in June because enterprise order volume dropped.",
    supports=["monthly_revenue", "monthly_revenue_chart"],
    confidence="medium"
)
```

## 9.9 `tf.export_report(path: str = "traceframe_report.html")`

Generates a local static HTML report.

Expected report sections:

1. Project summary
2. Dataset manifest
3. Data quality summary
4. Lineage graph/table
5. Metric registry
6. Chart evidence cards
7. Claims and supporting evidence
8. Reproducibility instructions

Example:

```python
tf.export_report("audit_report.html")
```

---

# 10. CLI specification

Use `typer` for the CLI.

Main command:

```bash
traceframe
```

## 10.1 `traceframe init`

Creates `.traceframe/`.

Usage:

```bash
traceframe init
```

Expected output:

```text
Initialized TraceFrame project in .traceframe/
```

## 10.2 `traceframe profile <path>`

Profiles a local data file.

Usage:

```bash
traceframe profile data/orders.csv
```

Expected output:

```text
File: data/orders.csv
Rows: 128392
Columns: 12
Hash: sha256:abc123
Missing values: 4 columns contain missing values
Duplicate rows: 82 possible duplicates
```

## 10.3 `traceframe status`

Shows current tracked project information.

Usage:

```bash
traceframe status
```

Expected output:

```text
TraceFrame project: revenue_analysis
Datasets: 2
Transformations: 3
Metrics: 4
Charts: 2
Claims: 1
Reports: 1
```

## 10.4 `traceframe report`

Generates a local HTML report from `.traceframe/`.

Usage:

```bash
traceframe report
```

Expected output:

```text
Generated report: .traceframe/reports/traceframe_report.html
```

## 10.5 `traceframe verify <artifact_id>`

Shows evidence for a dataset, metric, chart, or claim.

Usage:

```bash
traceframe verify monthly_revenue_chart
```

Expected output:

```text
Artifact: monthly_revenue_chart
Type: chart
Source: monthly_revenue
Metric: revenue
X: month
Y: revenue
Evidence file: .traceframe/audit_logs/monthly_revenue_chart.json
```

---

# 11. Evidence model

Implement a shared Pydantic model for evidence records.

Suggested model:

```python
from pydantic import BaseModel
from typing import Any, Literal

class EvidenceRecord(BaseModel):
    id: str
    artifact_type: Literal["dataset", "transformation", "metric", "chart", "claim", "sql_result"]
    name: str
    created_at: str
    source_ids: list[str] = []
    file_hashes: list[str] = []
    row_count_before: int | None = None
    row_count_after: int | None = None
    columns: list[str] = []
    operation: str | None = None
    formula: str | None = None
    sql: str | None = None
    chart_spec_path: str | None = None
    assumptions: list[str] = []
    warnings: list[str] = []
    metadata: dict[str, Any] = {}
```

Each artifact should have an evidence record.

---

# 12. Implementation details by module

## 12.1 `project.py`

Responsibilities:

- locate project root
- create `.traceframe/`
- initialize metadata JSON files
- load active project
- provide project paths

Functions:

- `init_project(path: str = ".")`
- `get_project_root()`
- `get_traceframe_dir()`
- `load_project()`
- `write_project_metadata()`

## 12.2 `storage.py`

Responsibilities:

- read/write JSON metadata files
- append evidence records
- safely create directories
- provide helper functions for manifests

Functions:

- `read_json(path, default)`
- `write_json(path, data)`
- `append_record(file_name, key, record)`

## 12.3 `fingerprint.py`

Responsibilities:

- compute SHA256 file hash
- maybe sample hash for large files later

Functions:

- `sha256_file(path: str) -> str`

Implementation rule:

- stream file in chunks
- do not load entire file into memory

## 12.4 `profiler.py`

Responsibilities:

- infer schema
- count rows/columns
- compute missing-value counts
- compute duplicate estimate
- detect basic data quality issues

Functions:

- `profile_dataframe(df) -> dict`
- `profile_csv(path) -> dict`

Use pandas for v0.1, Polars optional.

## 12.5 `io.py`

Responsibilities:

- implement tracked readers
- register dataset metadata

Functions:

- `read_csv(path, name=None)`
- `read_parquet(path, name=None)`
- later: `read_excel(path, name=None)`

## 12.6 `tracking.py`

Responsibilities:

- track transformations
- assign artifact IDs
- register lineage nodes
- store before/after metadata

Functions:

- `track(obj, name, source=None, operation=None)`

## 12.7 `sql.py`

Responsibilities:

- manage DuckDB connection
- register tracked DataFrames
- execute SQL
- store query and result metadata

Functions:

- `sql(query, name)`
- `register_table(name, df)`
- `get_connection()`

## 12.8 `metrics.py`

Responsibilities:

- register metric definitions
- store formula, source, description

Functions:

- `metric(name, formula, source, description=None)`

## 12.9 `charts.py`

Responsibilities:

- generate Vega-Lite/Altair specs
- store chart evidence

Functions:

- `chart(data, x, y, kind, title=None, name=None)`

Use Altair for v0.1.

## 12.10 `claims.py`

Responsibilities:

- register written claims
- link claims to supporting artifacts

Functions:

- `claim(text, supports, confidence=None)`

## 12.11 `lineage.py`

Responsibilities:

- maintain nodes and edges
- query lineage graph
- serialize lineage

Functions:

- `add_node(id, type, name)`
- `add_edge(from_id, to_id, type="derived_from")`
- `get_lineage_for(id)`

## 12.12 `report.py`

Responsibilities:

- load metadata
- render report template
- write static HTML file

Functions:

- `export_report(path)`
- `render_report(metadata)`

## 12.13 `cli.py`

Responsibilities:

- expose Typer CLI
- call project/profile/report/verify functions

Commands:

- `init`
- `profile`
- `status`
- `report`
- `verify`

---

# 13. Example workflow to include in `examples/ecommerce/analysis.py`

```python
import traceframe as tf

tf.start("ecommerce_revenue_analysis")

orders = tf.read_csv("orders.csv", name="orders")

clean_orders = tf.track(
    orders.drop_duplicates("order_id"),
    name="clean_orders",
    source="orders",
    operation="drop_duplicates(order_id)"
)

tf.metric(
    name="revenue",
    formula="SUM(total_price)",
    source="clean_orders",
    description="Total order revenue after duplicate order IDs are removed."
)

monthly = tf.sql("""
    SELECT
        strftime(order_date, '%Y-%m') AS month,
        SUM(total_price) AS revenue,
        COUNT(*) AS order_count
    FROM clean_orders
    GROUP BY 1
    ORDER BY 1
""", name="monthly_revenue")

tf.chart(
    monthly,
    x="month",
    y="revenue",
    kind="line",
    title="Monthly Revenue",
    name="monthly_revenue_chart"
)

tf.claim(
    "Monthly revenue trend was calculated after removing duplicate order IDs.",
    supports=["monthly_revenue", "monthly_revenue_chart"],
    confidence="high"
)

tf.export_report("ecommerce_audit_report.html")
```

---

# 14. Acceptance criteria for MVP

The coding agent should consider v0.1 complete when all of the following work:

## Setup

- `pip install -e .` works.
- `traceframe --help` works.
- `traceframe init` creates `.traceframe/`.

## Data tracking

- `tf.read_csv()` loads a CSV and registers it in `.traceframe/data_manifest.json`.
- File hash, row count, column count, schema, and missing values are stored.

## Transformation tracking

- `tf.track()` stores transformation metadata and lineage edge.
- Row/column counts are captured when possible.

## SQL execution

- `tf.sql()` can query tracked DataFrames through DuckDB.
- Query text is stored in the evidence record.
- Result is returned as a pandas DataFrame.

## Metrics

- `tf.metric()` writes metric definition to `.traceframe/metrics.json`.

## Charts

- `tf.chart()` generates a Vega-Lite/Altair spec.
- Chart evidence is stored in `.traceframe/charts.json`.

## Claims

- `tf.claim()` stores claim text and supporting artifact IDs.

## Reports

- `tf.export_report()` creates a readable local HTML report.
- `traceframe report` creates a report from saved metadata.

## Verification

- `traceframe verify <artifact_id>` prints useful artifact evidence.
- If artifact ID is not found, it shows a clear error.

## Tests

- Unit tests pass with `pytest`.
- At minimum, tests cover fingerprinting, project initialization, CSV tracking, metric registration, chart registration, and report generation.

---

# 15. README requirements

The README should include:

1. Project name and tagline
2. Problem statement
3. Install instructions
4. Quickstart example
5. CLI commands
6. Python API example
7. Example generated report screenshot placeholder
8. Local-first privacy statement
9. Roadmap
10. Contributing guide link

Suggested README opening:

```markdown
# TraceFrame

TraceFrame is a local-first evidence layer for data science. It records the source data, transformations, metrics, charts, and claims behind your analysis so every result can be verified and reproduced.

## Why?

Data scientists often create charts, metrics, and reports in notebooks, but the evidence behind those results is hard to trace. TraceFrame makes the evidence automatic.

## Local-first

TraceFrame runs on your machine. No data leaves your environment by default.
```

---

# 16. Roadmap

## v0.1 — Local evidence MVP

- Python package
- CLI
- local `.traceframe/` project folder
- CSV/Parquet tracking
- basic profiling
- DuckDB SQL execution
- metric registry
- chart evidence
- claim registry
- HTML report
- verify command

## v0.2 — Better notebook support

- detect active notebook name if possible
- record cell execution metadata if possible
- warn about stale artifacts manually
- richer report UI

## v0.3 — Better source-row evidence

- source row sampling
- source row export
- filter tracking
- SQL-backed drilldown for chart points

## v0.4 — Polars support

- native Polars tracking
- lazy frame profiling
- streaming support for larger local files

## v0.5 — Data quality checks

- null checks
- duplicate checks
- type checks
- unique-key checks
- threshold checks
- Great Expectations-style lightweight assertions

## v0.6 — AI-assisted mode, optional and local-safe

- optional natural language to TraceFrame steps
- optional local LLM integration
- never send data externally by default

## v1.0 — Stable local tool

- stable API
- stronger reports
- documentation
- examples
- tested workflow for pandas + DuckDB + Polars

---

# 17. Important implementation rules

1. Keep v0.1 simple.
2. Do not implement a web app yet.
3. Do not implement cloud sync.
4. Do not add AI in v0.1.
5. Do not build a custom programming language yet.
6. Make the Python API pleasant first.
7. Store evidence as JSON.
8. Make the local HTML report readable.
9. Write tests early.
10. Make the project useful even with small CSV examples.

---

# 18. Final product definition

TraceFrame is:

> A local-first, open-source developer tool for data scientists and analysts that automatically records the evidence behind every dataset, transformation, metric, chart, and conclusion.

TraceFrame should help users:

- trust their analysis
- reproduce old results
- defend numbers
- debug stale notebooks
- hand off work to others
- turn exploratory analysis into an auditable workflow

The MVP is not about doing more analysis.

The MVP is about making existing analysis **verifiable**.
