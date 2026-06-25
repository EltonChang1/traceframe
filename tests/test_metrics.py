import json

import traceframe as tf


def test_metric_registers_definition(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tf.start("metrics")

    tf.metric("revenue", "SUM(total)", source="orders", description="Total revenue")

    data = json.loads((tmp_path / ".traceframe" / "metrics.json").read_text(encoding="utf-8"))
    assert data["metrics"][0]["name"] == "revenue"
    assert data["metrics"][0]["formula"] == "SUM(total)"

