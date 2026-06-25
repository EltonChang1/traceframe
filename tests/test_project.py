from traceframe.project import init_project, load_project, start


def test_init_project_creates_metadata_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    init_project(".", "demo")

    assert (tmp_path / ".traceframe" / "project.json").exists()
    assert (tmp_path / ".traceframe" / "data_manifest.json").exists()
    assert (tmp_path / ".traceframe" / "audit_logs").is_dir()


def test_start_sets_project_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    start("analysis")

    assert load_project()["project_name"] == "analysis"

