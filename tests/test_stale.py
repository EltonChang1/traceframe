import traceframe as tf


def test_stale_datasets_detects_changed_source_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data_path = tmp_path / "orders.csv"
    data_path.write_text("id,total\n1,10\n", encoding="utf-8")
    tf.start("stale")
    tf.read_csv("orders.csv", name="orders")

    data_path.write_text("id,total\n1,20\n", encoding="utf-8")

    stale = tf.stale_datasets()
    assert len(stale) == 1
    assert stale[0]["name"] == "orders"
    assert stale[0]["status"] == "stale"
