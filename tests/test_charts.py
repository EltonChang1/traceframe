import json

import pandas as pd

import traceframe as tf


def test_chart_registers_spec(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tf.start("charts")
    df = pd.DataFrame({"month": ["2026-01"], "revenue": [100]})

    spec = tf.chart(df, x="month", y="revenue", kind="bar", name="revenue_chart")

    charts = json.loads(
        (tmp_path / ".traceframe" / "charts.json").read_text(encoding="utf-8")
    )
    assert spec["mark"]["type"] == "bar"
    assert charts["charts"][0]["name"] == "revenue_chart"
