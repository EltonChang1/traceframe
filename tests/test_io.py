import json

import traceframe as tf


def test_read_csv_tracks_dataset(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text("id,total\n1,10\n2,\n", encoding="utf-8")
    tf.start("orders")

    df = tf.read_csv("orders.csv", name="orders")

    manifest = json.loads((tmp_path / ".traceframe" / "data_manifest.json").read_text(encoding="utf-8"))
    dataset = manifest["datasets"][0]
    assert len(df) == 2
    assert dataset["name"] == "orders"
    assert dataset["row_count"] == 2
    assert dataset["missing_values"]["total"] == 1

