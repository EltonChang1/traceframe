from __future__ import annotations

from typing import Any

from traceframe.project import get_traceframe_dir
from traceframe.storage import read_json, write_json


def _lineage_path():
    return get_traceframe_dir() / "lineage.json"


def add_node(id: str, type: str, name: str, metadata: dict[str, Any] | None = None) -> None:
    path = _lineage_path()
    lineage = read_json(path, {"nodes": [], "edges": []})
    if not any(node["id"] == id for node in lineage["nodes"]):
        lineage["nodes"].append({"id": id, "type": type, "name": name, "metadata": metadata or {}})
    write_json(path, lineage)


def add_edge(from_id: str, to_id: str, type: str = "derived_from") -> None:
    path = _lineage_path()
    lineage = read_json(path, {"nodes": [], "edges": []})
    edge = {"from": from_id, "to": to_id, "type": type}
    if edge not in lineage["edges"]:
        lineage["edges"].append(edge)
    write_json(path, lineage)


def get_lineage_for(id: str) -> dict[str, list[dict[str, Any]]]:
    lineage = read_json(_lineage_path(), {"nodes": [], "edges": []})
    nodes = [node for node in lineage["nodes"] if node["id"] == id or node["name"] == id]
    edges = [edge for edge in lineage["edges"] if edge["from"] == id or edge["to"] == id]
    return {"nodes": nodes, "edges": edges}

