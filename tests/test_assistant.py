import json
import sys

import traceframe as tf


def test_plan_analysis_records_local_heuristic_plan(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tf.start("assistant")

    plan = tf.plan_analysis(
        "Create a revenue metric, quality checks, monthly SQL, chart, and claim",
        data_paths=["orders.csv"],
    )

    stored = json.loads(
        (tmp_path / ".traceframe" / "assistant_plans.json").read_text(encoding="utf-8")
    )["plans"]
    assert plan["mode"] == "heuristic"
    assert "No external API calls" in plan["privacy_notice"]
    assert any("metric" in step["title"].lower() for step in plan["steps"])
    assert stored[0]["id"] == plan["id"]


def test_plan_analysis_without_project_does_not_require_storage(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    plan = tf.plan_analysis("chart revenue", store=True)

    assert plan["stored"] is False
    assert plan["steps"]


def test_plan_analysis_can_use_explicit_local_command(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tf.start("local_llm")
    command = (
        f"{sys.executable} -c "
        '"import sys; data=sys.stdin.read(); print(\'tf.start(\\"local\\")\')"'
    )

    plan = tf.plan_analysis("Use a local model", local_llm_command=command)

    assert plan["mode"] == "local_llm"
    assert plan["steps"][0]["code"] == 'tf.start("local")'
