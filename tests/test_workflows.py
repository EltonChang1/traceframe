import json

import polars as pl

import traceframe as tf
from traceframe.diagnostics import project_health


def test_pandas_duckdb_end_to_end_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text(
        "order_id,order_date,status,total_price\n"
        "1,2026-01-01,complete,10.5\n"
        "2,2026-02-01,complete,25.0\n",
        encoding="utf-8",
    )

    tf.start("pandas_workflow")
    orders = tf.read_csv("orders.csv", name="orders")
    clean = tf.filter_rows(orders, "status == 'complete'", name="clean_orders")
    tf.expect_not_null(clean, "total_price")
    tf.metric("revenue", "SUM(total_price)", source="clean_orders")
    monthly = tf.sql(
        "SELECT strftime('%Y-%m', CAST(order_date AS DATE)) AS month, "
        "SUM(total_price) AS revenue FROM clean_orders GROUP BY 1 ORDER BY 1",
        name="monthly_revenue",
    )
    tf.chart(monthly, x="month", y="revenue", kind="bar", name="monthly_chart")
    tf.claim("Revenue is tracked from complete orders.", ["monthly_revenue"], "high")
    report = tf.export_report("audit.html")

    health = project_health()
    assert report.exists()
    assert health["status"] == "ok"
    assert tf.drilldown("monthly_chart").shape[0] == 2


def test_polars_duckdb_end_to_end_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text(
        "order_id,order_date,status,total_price\n"
        "1,2026-01-01,complete,10.5\n"
        "2,2026-02-01,complete,25.0\n",
        encoding="utf-8",
    )

    tf.start("polars_workflow")
    orders = tf.read_csv("orders.csv", name="orders", engine="polars")
    clean = tf.filter_rows(orders, "status == 'complete'", name="clean_orders")
    tf.expect_unique(clean, "order_id")
    monthly = tf.sql(
        "SELECT strftime('%Y-%m', CAST(order_date AS DATE)) AS month, "
        "SUM(total_price) AS revenue FROM clean_orders GROUP BY 1 ORDER BY 1",
        name="monthly_revenue",
    )
    tf.chart(monthly, x="month", y="revenue", kind="line", name="monthly_chart")
    tf.export_report("audit.html")

    manifest = json.loads(
        (tmp_path / ".traceframe" / "data_manifest.json").read_text(encoding="utf-8")
    )
    assert isinstance(clean, pl.DataFrame)
    assert manifest["datasets"][0]["schema"]["total_price"].startswith("Float")
    assert project_health()["status"] == "ok"
