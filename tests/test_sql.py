import traceframe as tf


def test_sql_queries_tracked_dataframe(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text("id,total\n1,10\n2,20\n", encoding="utf-8")
    tf.start("sql")
    orders = tf.read_csv("orders.csv", name="orders")
    tf.track(orders, name="clean_orders", source="orders", operation="identity")

    result = tf.sql(
        "SELECT SUM(total) AS revenue FROM clean_orders", name="monthly_revenue"
    )

    assert result.loc[0, "revenue"] == 30
