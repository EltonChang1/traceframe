import traceframe as tf


def test_export_report_writes_html(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tf.start("report")

    output = tf.export_report("audit.html")

    assert output.exists()
    assert "TraceFrame Audit Report" in output.read_text(encoding="utf-8")
    assert "Stale Checks" in output.read_text(encoding="utf-8")
