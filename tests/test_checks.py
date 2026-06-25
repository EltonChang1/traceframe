import json

import traceframe as tf


def test_data_quality_checks_record_pass_and_failures(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text(
        "id,total,status\n1,10,complete\n1,,complete\n3,200,cancelled\n",
        encoding="utf-8",
    )
    tf.start("checks")
    orders = tf.read_csv("orders.csv", name="orders")

    not_null = tf.expect_not_null(orders, "total")
    unique = tf.expect_unique(orders, "id")
    no_duplicates = tf.expect_no_duplicates(orders, subset=["id"])
    threshold = tf.expect_column_between(orders, "total", min_value=0, max_value=150)
    generic = tf.expect("manual_review_complete", True, metadata={"reviewer": "local"})

    checks = json.loads(
        (tmp_path / ".traceframe" / "checks.json").read_text(encoding="utf-8")
    )["checks"]
    assert not not_null["passed"]
    assert not unique["passed"]
    assert not no_duplicates["passed"]
    assert not threshold["passed"]
    assert generic["passed"]
    assert len(checks) == 5


def test_schema_check_and_polars_not_null(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text("id,total\n1,10\n2,20\n", encoding="utf-8")
    tf.start("polars_checks")
    orders = tf.read_csv("orders.csv", name="orders", engine="polars")

    schema = tf.expect_schema(orders, {"id": "int64", "total": "int64"})
    not_null = tf.expect_not_null(orders, ["id", "total"])

    assert schema["passed"]
    assert not_null["passed"]
