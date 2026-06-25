# Olist Marketplace Example

A TraceFrame-instrumented workflow inspired by the popular
[Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
on Kaggle.

This example uses a small bundled CSV subset so it runs without Kaggle credentials.
The flow mirrors common Olist analyses: load relational tables, filter delivered orders,
join customers and items, aggregate monthly revenue by state, chart results, and record a claim.

## Run

```bash
cd examples/olist
traceframe init
python analysis.py
traceframe status
traceframe lineage monthly_revenue_by_state --direction upstream
traceframe report
```

To use the full public dataset, download it from Kaggle into `data/` and point the
`read_csv` paths at the official `olist_*.csv` files.
