from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def read_json(path: str | Path, default: Any) -> Any:
    json_path = Path(path)
    if not json_path.exists():
        return deepcopy(default)
    with json_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str | Path, data: Any) -> None:
    json_path = Path(path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = json_path.with_suffix(json_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(json_path)


def append_record(path: str | Path, key: str, record: dict[str, Any]) -> None:
    data = read_json(path, {key: []})
    data.setdefault(key, [])
    data[key].append(record)
    write_json(path, data)

