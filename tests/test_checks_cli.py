import json

from typer.testing import CliRunner

from traceframe.cli import app


def test_checks_json_output(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    trace_dir = tmp_path / ".traceframe"
    trace_dir.mkdir()
    (trace_dir / "project.json").write_text('{"project_name": "demo"}', encoding="utf-8")
    (trace_dir / "checks.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "name": "not_null_id",
                        "passed": True,
                        "check_type": "not_null",
                        "severity": "error",
                        "source": "orders",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["checks", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["checks"][0]["name"] == "not_null_id"
