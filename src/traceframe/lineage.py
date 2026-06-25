from __future__ import annotations

from typing import Any, Literal

from traceframe.project import get_traceframe_dir
from traceframe.storage import read_json, write_json

LineageDirection = Literal["upstream", "downstream", "both"]


def _lineage_path():
    return get_traceframe_dir() / "lineage.json"


def add_node(
    id: str, type: str, name: str, metadata: dict[str, Any] | None = None
) -> None:
    path = _lineage_path()
    lineage = read_json(path, {"nodes": [], "edges": []})
    if not any(node["id"] == id for node in lineage["nodes"]):
        lineage["nodes"].append(
            {"id": id, "type": type, "name": name, "metadata": metadata or {}}
        )
    write_json(path, lineage)


def add_edge(from_id: str, to_id: str, type: str = "derived_from") -> None:
    path = _lineage_path()
    lineage = read_json(path, {"nodes": [], "edges": []})
    edge = {"from": from_id, "to": to_id, "type": type}
    if edge not in lineage["edges"]:
        lineage["edges"].append(edge)
    write_json(path, lineage)


def _load_lineage() -> dict[str, list[dict[str, Any]]]:
    return read_json(_lineage_path(), {"nodes": [], "edges": []})


def _node_ids_for(lineage: dict[str, list[dict[str, Any]]], artifact: str) -> list[str]:
    return [
        node["id"]
        for node in lineage["nodes"]
        if node.get("id") == artifact or node.get("name") == artifact
    ]


def _walk(
    edges: list[dict[str, Any]],
    start_ids: set[str],
    direction: Literal["upstream", "downstream"],
    max_depth: int | None,
) -> tuple[list[str], set[tuple[str, str, str]]]:
    visited = set(start_ids)
    frontier = set(start_ids)
    ordered_ids: list[str] = []
    selected_edges: set[tuple[str, str, str]] = set()
    depth = 0

    while frontier and (max_depth is None or depth < max_depth):
        next_frontier: set[str] = set()
        for edge in edges:
            from_id = edge.get("from")
            to_id = edge.get("to")
            edge_type = edge.get("type", "derived_from")
            if direction == "upstream" and to_id in frontier:
                adjacent_id = from_id
            elif direction == "downstream" and from_id in frontier:
                adjacent_id = to_id
            else:
                continue

            if not isinstance(adjacent_id, str):
                continue
            selected_edges.add((str(from_id), str(to_id), str(edge_type)))
            if adjacent_id not in visited:
                visited.add(adjacent_id)
                ordered_ids.append(adjacent_id)
                next_frontier.add(adjacent_id)

        frontier = next_frontier
        depth += 1

    return ordered_ids, selected_edges


def lineage_graph(
    artifact: str,
    direction: LineageDirection = "both",
    max_depth: int | None = None,
) -> dict[str, Any]:
    if direction not in {"upstream", "downstream", "both"}:
        raise ValueError("direction must be one of: upstream, downstream, both")
    if max_depth is not None and max_depth < 1:
        raise ValueError("max_depth must be at least 1 when provided")

    lineage = _load_lineage()
    center_ids = _node_ids_for(lineage, artifact)
    if not center_ids:
        raise KeyError(f"Lineage artifact not found: {artifact}")

    node_by_id = {node["id"]: node for node in lineage["nodes"]}
    center_set = set(center_ids)
    upstream_ids: list[str] = []
    downstream_ids: list[str] = []
    selected_edges: set[tuple[str, str, str]] = set()

    if direction in {"upstream", "both"}:
        upstream_ids, upstream_edges = _walk(
            lineage["edges"], center_set, "upstream", max_depth
        )
        selected_edges.update(upstream_edges)
    if direction in {"downstream", "both"}:
        downstream_ids, downstream_edges = _walk(
            lineage["edges"], center_set, "downstream", max_depth
        )
        selected_edges.update(downstream_edges)

    ordered_node_ids = [*center_ids, *upstream_ids, *downstream_ids]
    nodes = [
        node_by_id[node_id]
        for index, node_id in enumerate(ordered_node_ids)
        if node_id in node_by_id and node_id not in ordered_node_ids[:index]
    ]
    edges = [
        {"from": from_id, "to": to_id, "type": edge_type}
        for from_id, to_id, edge_type in sorted(selected_edges)
    ]
    edge_rows = [
        {
            **edge,
            "from_name": node_by_id.get(edge["from"], {}).get("name"),
            "from_type": node_by_id.get(edge["from"], {}).get("type"),
            "to_name": node_by_id.get(edge["to"], {}).get("name"),
            "to_type": node_by_id.get(edge["to"], {}).get("type"),
        }
        for edge in edges
    ]

    return {
        "artifact": artifact,
        "direction": direction,
        "max_depth": max_depth,
        "center_ids": center_ids,
        "nodes": nodes,
        "edges": edges,
        "edge_rows": edge_rows,
        "upstream": [
            node_by_id[node_id] for node_id in upstream_ids if node_id in node_by_id
        ],
        "downstream": [
            node_by_id[node_id] for node_id in downstream_ids if node_id in node_by_id
        ],
    }


def get_lineage_for(id: str) -> dict[str, list[dict[str, Any]]]:
    graph = lineage_graph(id, direction="both", max_depth=1)
    return {"nodes": graph["nodes"], "edges": graph["edges"]}


def all_lineage() -> dict[str, list[dict[str, Any]]]:
    return _load_lineage()
