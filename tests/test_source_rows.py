import json

import traceframe as tf


def test_read_csv_writes_and_exports_source_row_sample(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text("id,total\n1,10\n2,20\n", encoding="utf-8")
    tf.start("source_rows")

    tf.read_csv("orders.csv", name="orders")
    output = tf.export_source_rows("orders", limit=1)

    exported = json.loads(output.read_text(encoding="utf-8"))
    assert exported["artifact_id"].startswith("ds_orders")
    assert exported["sample_size"] == 1
    assert exported["rows"][0]["values"] == {"id": 1, "total": 10}


def test_filter_rows_tracks_condition_and_source_rows(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text("id,total\n1,10\n2,25\n", encoding="utf-8")
    tf.start("filters")
    orders = tf.read_csv("orders.csv", name="orders")

    filtered = tf.filter_rows(orders, "total >= 20", name="large_orders")
    output = tf.export_source_rows("large_orders")

    assert len(filtered) == 1
    assert filtered.iloc[0]["id"] == 2
    exported = json.loads(output.read_text(encoding="utf-8"))
    assert exported["rows"][0]["values"]["total"] == 25


def test_chart_drilldown_queries_backing_duckdb_table(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text(
        "month,revenue\n2026-01,10\n2026-02,25\n", encoding="utf-8"
    )
    tf.start("drilldown")
    monthly = tf.read_csv("orders.csv", name="monthly")
    tf.chart(monthly, x="month", y="revenue", kind="bar", name="monthly_chart")

    rows = tf.drilldown("monthly_chart", x="month", value="2026-02")

    assert len(rows) == 1
    assert rows.iloc[0]["revenue"] == 25
