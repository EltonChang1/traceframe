import json

from typer.testing import CliRunner

import traceframe as tf
from traceframe.cli import app


def _build_lineage_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text("id,total\n1,10\n2,20\n", encoding="utf-8")
    tf.start("lineage")
    orders = tf.read_csv("orders.csv", name="orders")
    tf.track(orders, name="clean_orders", source="orders", operation="identity")
    tf.sql("SELECT SUM(total) AS revenue FROM clean_orders", name="monthly_revenue")


def test_lineage_graph_traverses_upstream_by_name(tmp_path, monkeypatch):
    _build_lineage_project(tmp_path, monkeypatch)

    graph = tf.lineage_graph("monthly_revenue", direction="upstream")

    upstream_names = [node["name"] for node in graph["upstream"]]
    assert graph["center_ids"][0].startswith("sql_monthly_revenue")
    assert upstream_names == ["clean_orders", "orders"]
    assert len(graph["edges"]) == 2


def test_lineage_graph_limits_depth(tmp_path, monkeypatch):
    _build_lineage_project(tmp_path, monkeypatch)

    graph = tf.lineage_graph("monthly_revenue", direction="upstream", max_depth=1)

    assert [node["name"] for node in graph["upstream"]] == ["clean_orders"]
    assert len(graph["edges"]) == 1


def test_lineage_cli_prints_dependencies(tmp_path, monkeypatch):
    _build_lineage_project(tmp_path, monkeypatch)

    result = CliRunner().invoke(app, ["lineage", "orders", "--direction", "downstream"])

    assert result.exit_code == 0
    assert "Artifact: orders" in result.stdout
    assert "Downstream: 2" in result.stdout
    assert "clean_orders [transformation]" in result.stdout
    assert "monthly_revenue [sql_result]" in result.stdout
    assert "orders [dataset]" in result.stdout


def test_lineage_cli_prints_json(tmp_path, monkeypatch):
    _build_lineage_project(tmp_path, monkeypatch)

    result = CliRunner().invoke(app, ["lineage", "orders", "--json"])

    assert result.exit_code == 0
    graph = json.loads(result.stdout)
    assert graph["artifact"] == "orders"
    assert graph["center_ids"][0].startswith("ds_orders")
    assert "metadata" not in graph["nodes"][0]
    assert graph["edge_rows"][0]["from_name"] == "orders"


def test_lineage_cli_can_include_json_metadata(tmp_path, monkeypatch):
    _build_lineage_project(tmp_path, monkeypatch)

    result = CliRunner().invoke(
        app, ["lineage", "orders", "--json", "--include-metadata"]
    )

    assert result.exit_code == 0
    graph = json.loads(result.stdout)
    assert "metadata" in graph["nodes"][0]


def test_lineage_cli_missing_artifact_has_clean_error(tmp_path, monkeypatch):
    _build_lineage_project(tmp_path, monkeypatch)

    result = CliRunner().invoke(app, ["lineage", "unknown"])

    assert result.exit_code == 1
    assert result.stdout.strip() == "Lineage artifact not found: unknown"
