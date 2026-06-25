from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from traceframe.project import get_traceframe_dir, load_project
from traceframe.storage import read_json


def _metadata() -> dict[str, Any]:
    trace_dir = get_traceframe_dir()
    return {
        "project": load_project(),
        "datasets": read_json(trace_dir / "data_manifest.json", {"datasets": []}).get("datasets", []),
        "lineage": read_json(trace_dir / "lineage.json", {"nodes": [], "edges": []}),
        "metrics": read_json(trace_dir / "metrics.json", {"metrics": []}).get("metrics", []),
        "charts": read_json(trace_dir / "charts.json", {"charts": []}).get("charts", []),
        "claims": read_json(trace_dir / "claims.json", {"claims": []}).get("claims", []),
    }


def render_report(metadata: dict[str, Any]) -> str:
    env = Environment(
        loader=PackageLoader("traceframe", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("report.html.j2")
    return template.render(**metadata)


def export_report(path: str | Path = "traceframe_report.html") -> Path:
    output_path = Path(path)
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path
    html = render_report(_metadata())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path

