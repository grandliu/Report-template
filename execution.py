"""Runtime inventory reconciliation shared by the runner and its pytest plugin."""
from __future__ import annotations

import json
from pathlib import Path

from .catalog import make_case


def json_value(value):
    """Normalize parameters without reading tensor contents or invoking repr."""
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, (tuple, list)):
        return [json_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if type(value).__name__ == "dtype":
        return str(value).removeprefix("torch.")
    return {"unresolved_type": type(value).__name__}


def match_cases(operator, test, params, label=None):
    candidates = [c for c in operator["cases"] if c["test"] == test]
    if label is not None:
        labeled = [c for c in candidates if c.get("label") == label]
        if len(labeled) == 1:
            return labeled
    flat = dict(params)
    for value in params.values():
        if isinstance(value, dict):
            flat.update(value)
    matched = []
    for case in candidates:
        common = set(flat) & set(case["params"])
        if common and all(json_value(case["params"][k]) == flat[k] for k in common):
            matched.append(case)
    return matched if matched else candidates if len(candidates) == 1 else []


def reconcile_items(operator, inventory):
    """Add dynamically discovered pytest items; preserve bundled shape inventories."""
    for item in inventory:
        test, params = item["test"], item["params"]
        cases = match_cases(operator, test, params, item.get("label"))
        if not cases and (params or not any(c["test"] == test for c in operator["cases"])):
            case = make_case(operator["operator_id"], test, params, item.get("label"))
            case["source_occurrences"] = 1
            case["inventory_origin"] = "pytest collection"
            operator["cases"].append(case)
            cases = [case]
        item["case_ids"] = [c["case_id"] for c in cases]
        item["bundled"] = not cases and any(c["test"] == test for c in operator["cases"])
    return inventory


def read_jsonl(path):
    path = Path(path)
    if not path.is_file():
        return []
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except ValueError as exc:
                raise ValueError(f"{path}:{number}: invalid runtime JSON: {exc}") from exc
    return rows
