import json

import traceframe as tf


def test_start_records_notebook_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    tf.start("notebook_project", notebook_name="analysis.ipynb")

    runs = json.loads(
        (tmp_path / ".traceframe" / "runs.json").read_text(encoding="utf-8")
    )
    run = runs["runs"][0]
    assert run["project_name"] == "notebook_project"
    assert run["context"]["kind"] == "notebook"
    assert run["context"]["notebook_name"] == "analysis.ipynb"


def test_note_cell_records_cell_event_and_evidence_context(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "orders.csv").write_text("id,total\n1,10\n", encoding="utf-8")
    tf.start("cells", notebook_name="analysis.ipynb")

    tf.note_cell(
        cell_id="cell-1", execution_count=3, source_hash="sha256:abc", tags=["load"]
    )
    tf.read_csv("orders.csv", name="orders")

    cells = json.loads(
        (tmp_path / ".traceframe" / "cell_events.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (tmp_path / ".traceframe" / "data_manifest.json").read_text(encoding="utf-8")
    )
    dataset_id = manifest["datasets"][0]["id"]
    evidence = json.loads(
        (tmp_path / ".traceframe" / "audit_logs" / f"{dataset_id}.json").read_text(
            encoding="utf-8"
        )
    )

    assert cells["cells"][0]["cell_id"] == "cell-1"
    assert evidence["run_id"] == manifest["datasets"][0]["run_id"]
    assert evidence["metadata"]["execution_context"]["cell_id"] == "cell-1"
