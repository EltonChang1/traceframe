import json

import polars as pl

import traceframe as tf


def test_read_csv_with_polars_engine_tracks_dataset(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text("id,total\n1,10\n2,20\n", encoding="utf-8")
    tf.start("polars")

    df = tf.read_csv("orders.csv", name="orders", engine="polars")

    manifest = json.loads(
        (tmp_path / ".traceframe" / "data_manifest.json").read_text(encoding="utf-8")
    )
    assert isinstance(df, pl.DataFrame)
    assert manifest["datasets"][0]["schema"]["total"].startswith("Int")
    assert manifest["datasets"][0]["row_count"] == 2


def test_scan_csv_tracks_lazy_polars_schema_without_full_profile(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text("id,total\n1,10\n2,20\n", encoding="utf-8")
    tf.start("polars_lazy")

    lazy = tf.scan_csv("orders.csv", name="orders_lazy")

    manifest = json.loads(
        (tmp_path / ".traceframe" / "data_manifest.json").read_text(encoding="utf-8")
    )
    assert isinstance(lazy, pl.LazyFrame)
    assert manifest["datasets"][0]["row_count"] is None
    assert manifest["datasets"][0]["schema"]["id"].startswith("Int")


def test_polars_filter_and_sql_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text("id,total\n1,10\n2,25\n", encoding="utf-8")
    tf.start("polars_workflow")
    orders = tf.read_csv("orders.csv", name="orders", engine="polars")

    large = tf.filter_rows(orders, "total >= 20", name="large_orders")
    result = tf.sql("SELECT SUM(total) AS revenue FROM large_orders", name="revenue")

    assert isinstance(large, pl.DataFrame)
    assert result.iloc[0]["revenue"] == 25
