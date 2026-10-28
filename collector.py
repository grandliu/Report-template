"""Collect a versioned offline result bundle; logs are evidence, never guessed metrics."""
from __future__ import annotations

import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

STATUSES = {"passed", "failed", "error", "skipped", "not_run"}


def read_json(path, default, warnings):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        warnings.append(f"{path.name}: {exc}")
        return default


def parse_junit(path):
    root = ET.parse(path).getroot()
    records = []
    for case in root.iter("testcase"):
        props = {p.get("name"): p.get("value", "") for p in case.findall("./properties/property")}
        status, message = "passed", None
        for tag in ("failure", "error", "skipped"):
            child = case.find(tag)
            if child is not None:
                status = {"failure": "failed", "error": "error", "skipped": "skipped"}[tag]
                message = child.get("message") or child.text
                break
        records.append({"operator_id": props.get("operator_id"), "case_id": props.get("case_id"),
                        "kernel_name": props.get("kernel_name"), "mode": props.get("mode", "normal"),
                        "nodeid": props.get("nodeid") or "::".join(filter(None, [case.get("classname"), case.get("name")])),
                        "status": status, "message": message, "properties": props,
                        "source": path.name})
    # Collection failures can exist at suite level without a testcase.
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    declared_errors = sum(int(s.get("errors", 0)) for s in suites)
    return {"records": records, "unassigned_errors": max(0, declared_errors - sum(r["status"] == "error" for r in records))}


def _records(payload, filename, warnings):
    records = payload.get("records", []) if isinstance(payload, dict) else None
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        warnings.append(f"{filename}: expected an object with a records array")
        return []
    if payload.get("schema_version") != 1:
        warnings.append(f"{filename}: unsupported/missing schema_version (expected 1)")
        return []
    validated = []
    for record in records:
        if any(key in record and record[key] is not None and not isinstance(record[key], str)
               for key in ("operator_id", "case_id", "kernel_name", "mode", "nodeid", "kernel_source", "cceir")):
            warnings.append(f"{filename}: identifier, mode, and artifact path fields must be strings")
            continue
        validated.append(record)
    return validated


def load_artifact(base, relative, warnings):
    if not relative:
        return None
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        warnings.append(f"artifact outside input directory: {relative}")
        return None
    try:
        return {"path": str(relative), "content": path.read_text(encoding="utf-8-sig")}
    except (OSError, UnicodeError) as exc:
        warnings.append(f"artifact {relative}: {exc}")
        return None


def collect(input_dir=None):
    if input_dir is None:
        return {"metadata": {}, "environment": None, "correctness": [], "performance": [],
                "logs": [], "warnings": [], "unassigned_errors": 0}
    base = Path(input_dir).resolve()
    if not base.is_dir():
        raise ValueError(f"input directory does not exist: {base}")
    warnings = []
    metadata = read_json(base / "run_info.json", {}, warnings)
    environment = read_json(base / "environment.json", None, warnings)
    if not isinstance(metadata, dict):
        warnings.append("run_info.json: expected an object")
        metadata = {}
    if environment is not None and not isinstance(environment, dict):
        warnings.append("environment.json: expected an object")
        environment = None
    correctness, unassigned_errors = [], 0
    if (base / "correctness.xml").is_file():
        try:
            junit = parse_junit(base / "correctness.xml")
            correctness.extend(junit["records"])
            unassigned_errors = junit["unassigned_errors"]
        except (OSError, ValueError, ET.ParseError) as exc:
            warnings.append(f"correctness.xml: {exc}")
            unassigned_errors += 1
    path = base / "case_results.json"
    if path.is_file():
        for record in _records(read_json(path, {}, warnings), path.name, warnings):
            record = dict(record, source=path.name)
            if not isinstance(record.get("status"), str) or record["status"] not in STATUSES:
                warnings.append(f"case_results.json: invalid status {record.get('status')!r}")
                continue
            correctness.append(record)
    performance = []
    path = base / "performance.json"
    if path.is_file():
        for original in _records(read_json(path, {}, warnings), path.name, warnings):
            record = dict(original)
            samples = record.get("task_duration_us", [])
            if not isinstance(samples, list) or not samples or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0 for v in samples):
                warnings.append(f"performance.json: invalid task_duration_us for {record.get('case_id')}")
                continue
            if record.get("unit", "us") != "us":
                warnings.append(f"performance.json: unsupported unit for {record.get('case_id')}")
                continue
            record["source"] = path.name
            record["kernel_source"] = load_artifact(base, record.get("kernel_source"), warnings)
            record["cceir"] = load_artifact(base, record.get("cceir"), warnings)
            performance.append(record)
    execution = read_json(base / "execution.json", {}, warnings)
    if isinstance(execution, dict):
        for stage in ("correctness", "performance"):
            warnings.extend(execution.get(stage, {}).get("warnings", []))
    logs = []
    for path in sorted((base / "logs").rglob("*.log")) if (base / "logs").exists() else []:
        try:
            logs.append({"path": path.relative_to(base).as_posix(), "content": path.read_text(encoding="utf-8", errors="replace")})
        except OSError as exc:
            warnings.append(f"{path.name}: {exc}")
    for path in sorted((base / "tasks").rglob("process.log")) if (base / "tasks").exists() else []:
        try:
            logs.append({"path": path.relative_to(base).as_posix(), "content": path.read_text(encoding="utf-8", errors="replace")})
        except OSError as exc:
            warnings.append(f"{path.name}: {exc}")
    if (base / "environment.log").exists():
        logs.append({"path": "environment.log", "content": (base / "environment.log").read_text(encoding="utf-8", errors="replace")})
    return {"metadata": metadata, "environment": environment, "correctness": correctness,
            "performance": performance, "logs": logs, "warnings": warnings,
            "unassigned_errors": unassigned_errors, "input_dir": str(base), "execution": execution}
