# Getting Started

This guide walks through a complete local evidence workflow in about five minutes.

## Install

```bash
git clone https://github.com/EltonChang1/traceframe.git
cd traceframe
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Python 3.10+ is required.

## Run the example

TraceFrame ships with a small ecommerce analysis under `examples/ecommerce/`:

```bash
cd examples/ecommerce
traceframe init
python analysis.py
```

The script loads `orders.csv`, tracks transformations, runs SQL, records a metric and chart, writes a claim, and exports an HTML audit report.

## Inspect evidence

From the same directory:

```bash
traceframe status
traceframe doctor
traceframe lineage monthly_revenue --direction upstream
traceframe checks
traceframe verify monthly_revenue
traceframe report
```

Expected outcomes:

- `status` lists datasets, metrics, charts, claims, and checks
- `doctor` reports project health with no issues on a clean run
- `lineage` shows the path from `orders` to `monthly_revenue`
- `report` writes `.traceframe/reports/traceframe_report.html`

Open `ecommerce_audit_report.html` or the generated report in a browser to review the audit page.

## Use it in your own project

1. `cd` into your analysis directory and run `traceframe init`.
2. In a script or notebook, call `import traceframe as tf` and `tf.start("project_name")`.
3. Wrap the steps you care about: reads, transforms, SQL, metrics, charts, and claims.
4. Add checks with `tf.expect_not_null`, `tf.expect_unique`, and related helpers.
5. Run `traceframe doctor` and `traceframe report` before sharing results.

For notebook context, pass `notebook_name=` to `tf.start(...)` and call `tf.note_cell(...)` before important cells.

See also `examples/olist/` for a multi-table marketplace workflow inspired by the Olist dataset.

## Next steps

- [API reference](api-reference.md)
- [Evidence model](evidence-model.md)
- [Contributing](../CONTRIBUTING.md)
- [Roadmap](../ROADMAP.md)
