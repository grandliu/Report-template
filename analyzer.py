"""Join logical inputs, accuracy, and per-kernel timings into canonical run data."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime
from statistics import median


def _resolve(record, operators, cases):
    identifier = record.get("case_id")
    if identifier in cases:
        op_id, case = cases[identifier]
        if record.get("operator_id") and record["operator_id"] != op_id:
            return [], "case_id/operator_id mismatch"
        return [(op_id, case)], None
    if identifier:
        return [], f"unknown case_id {identifier}"
    node = str(record.get("nodeid", "")).replace("\\", "/")
    fn = node.split("::")[-1].split("[")[0]
    label = node.split("[", 1)[1].rsplit("]", 1)[0] if "[" in node else None
    matches = []
    for op in operators:
        if record.get("operator_id") and record["operator_id"] != op["operator_id"]:
            continue
        for case in op["cases"]:
            test_file, test_fn = case["test"].split("::")
            source_match = test_file.replace("/", ".").removesuffix(".py") in node.replace("/", ".") or test_file in node
            if test_fn == fn and (record.get("operator_id") or source_match):
                if label is None or label == case.get("label"):
                    matches.append((op["operator_id"], case))
    if not matches:
        return [], f"cannot map JUnit node {node!r}; provide case_id properties or case_results.json"
    if label is not None and len(matches) != 1:
        return [], f"ambiguous parameterized node {node!r}; provide case_id"
    if len(matches) > 1 and record.get("status") not in {"passed", "skipped"}:
        return [], f"bundle {node!r} did not pass; per-input outcomes required"
    return matches, None


def analyze(catalog, collected, setup):
    operators = deepcopy(catalog["operators"])
    cases = {case["case_id"]: (op["operator_id"], case) for op in operators for case in op["cases"]}
    op_lookup = {op["operator_id"]: op for op in operators}
    warnings = [*catalog["warnings"], *collected["warnings"]]
    accuracy, timings, unmatched = {}, {}, []
    attempted_ops = set()
    execution = collected.get("execution", {})
    performance_stage = execution.get("performance", {})
    observed = {}
    for record in performance_stage.get("executed_kernels", []):
        observed.setdefault(record["case_id"], set()).add(record["kernel_name"])
    for record in collected["correctness"]:
        if record.get("operator_id") in op_lookup and record.get("status") != "not_run":
            attempted_ops.add(record["operator_id"])
        node = str(record.get("nodeid", "")).replace("\\", "/")
        for op in operators:
            if any(test in node or test.replace("/", ".").removesuffix(".py") in node.replace("/", ".") for test in op["tests"]):
                attempted_ops.add(op["operator_id"])
        resolved, issue = _resolve(record, operators, cases)
        if issue:
            warnings.append(issue)
            unmatched.append(record)
            continue
        mode = record.get("mode", "normal")
        for op_id, case in resolved:
            key = (case["case_id"], mode, record.get("kernel_name"))
            if record.get("kernel_name") and record["kernel_name"] not in {k["kernel_name"] for k in op_lookup[op_id]["kernels"]}:
                warnings.append(f"{op_id}: unknown accuracy kernel {record['kernel_name']!r}")
                continue
            # Structured per-input outcomes override JUnit's enclosing test outcome.
            existing = accuracy.get(key)
            if existing and existing["source"] == "case_results.json" and record["source"] != "case_results.json":
                continue
            if existing and existing["source"] == record["source"] and existing["status"] != record["status"]:
                warnings.append(f"conflicting accuracy results for {key}; latest explicit record used")
            accuracy[key] = {**record, "operator_id": op_id, "case_id": case["case_id"],
                             "accuracy_scope": "case" if record.get("case_id") or len(resolved) == 1 else "enclosing_test"}
    for record in collected["performance"]:
        resolved, issue = _resolve(record, operators, cases)
        if issue or len(resolved) != 1:
            warnings.append(issue or "performance record must identify one input")
            continue
        op_id, case = resolved[0]
        kernel = record.get("kernel_name")
        if kernel not in {k["kernel_name"] for k in op_lookup[op_id]["kernels"]}:
            warnings.append(f"{op_id}: unknown entry kernel {kernel!r}")
            continue
        key = (case["case_id"], record.get("mode", "normal"), kernel)
        if key in timings:
            timings[key]["task_duration_us"].extend(record["task_duration_us"])
            # Artifacts are tied to this exact input+mode+kernel specialization.
            for artifact in ("kernel_source", "cceir"):
                if record.get(artifact):
                    timings[key][artifact] = record[artifact]
        else:
            timings[key] = deepcopy(record)
    all_results, total_outcomes = [], []
    measured_ops, measured_cases = attempted_ops, set()
    for op in operators:
        details, outcomes = [], []
        op_ids = {c["case_id"] for c in op["cases"]}
        for case in op["cases"]:
            cid = case["case_id"]
            modes = {mode for key, mode, _ in accuracy if key == cid} | {mode for key, mode, _ in timings if key == cid} or {"normal"}
            statuses = [r["status"] for (key, _, _), r in accuracy.items() if key == cid]
            if any(s != "not_run" for s in statuses) or any(key[0] == cid for key in timings):
                measured_ops.add(op["operator_id"])
                measured_cases.add(cid)
            # Coverage ignores repeated modes; failure in any mode remains a failure.
            status = next((s for s in ("error", "failed", "passed", "skipped") if s in statuses), "not_run")
            if status != "not_run":
                outcomes.append(status)
                total_outcomes.append(status)
            for mode in sorted(modes):
                for kernel in op["kernels"]:
                    if cid in observed and kernel["kernel_name"] not in observed[cid]:
                        continue  # Conditional stages absent from this actual execution.
                    acc = accuracy.get((cid, mode, kernel["kernel_name"])) or accuracy.get((cid, mode, None))
                    timing = timings.get((cid, mode, kernel["kernel_name"]))
                    runtime = {**(acc or {}), **(timing or {})}
                    detail = {"operator_id": op["operator_id"], "case_id": cid, "test": case["test"],
                        "params": case["params"], "shape": runtime.get("shape", case["shape"]), "dtype": runtime.get("dtype", case["dtype"]), "mode": mode,
                        "kernel_name": kernel["kernel_name"], "accuracy": acc["status"] if acc else "not_run",
                        "accuracy_scope": acc.get("accuracy_scope") if acc else None,
                        "message": acc.get("message") if acc else None,
                        "latency_us": median(timing["task_duration_us"]) if timing else None,
                        "task_duration_us": timing["task_duration_us"] if timing else [],
                        "measurement_scope": timing.get("measurement_scope", "kernel_launch") if timing else None,
                        "kernel_source": timing.get("kernel_source") if timing and timing.get("kernel_source") else {"path": kernel["file"], "line": kernel["line"], "content": kernel["source"], "origin": "catalog source snapshot"},
                        "cceir": timing.get("cceir") if timing else None}
                    if timing and (not acc or acc["status"] != "passed"):
                        warnings.append(f"{cid}/{mode}/{kernel['kernel_name']}: timing present without passing accuracy gate")
                    details.append(detail)
        counts = Counter(outcomes)
        latencies = [r["latency_us"] for r in details if r["latency_us"] is not None]
        op["summary"] = {"total_cases": len(op_ids), "tested_cases": len(op_ids & measured_cases),
            "correctness_cases": len(outcomes), "passed": counts["passed"], "failed": counts["failed"] + counts["error"],
            "skipped": counts["skipped"], "pass_rate": counts["passed"] / len(outcomes) if outcomes else None,
            "task_duration_range_us": {"min": min(latencies), "max": max(latencies)} if latencies else None}
        op["details"] = details
        op["device_totals"] = [{**record, "latency_us": median(record["task_duration_us"])}
            for record in performance_stage.get("operator_totals", []) if record["case_id"] in op_ids]
        all_results.extend(details)
    counts = Counter(total_outcomes)
    failures = counts["failed"] + counts["error"]
    unmapped_failures = sum(r.get("status") in {"failed", "error"} for r in unmatched) + collected["unassigned_errors"]
    timing_rows = [r for r in all_results if r["latency_us"] is not None]
    expected_rows = [r for r in all_results if r["accuracy"] == "passed"]
    status = "failed" if failures or unmapped_failures else "not_run" if not measured_cases else "passed" if timing_rows and expected_rows and all(r["latency_us"] is not None for r in expected_rows) and all(r["accuracy"] == "passed" for r in timing_rows) and counts["skipped"] == 0 and len(total_outcomes) == len(measured_cases) else "partial"
    if execution and status == "passed" and performance_stage.get("status") != "passed":
        status = "partial"
    metadata = {"run_id": "offline", "generated_at": datetime.now().astimezone().isoformat(), **collected["metadata"]}
    return {"schema_version": 1, "status": status, "metadata": metadata, "setup": setup,
        "summary": {"total_operators": len(operators), "tested_operators": len(measured_ops),
            "total_cases": len(cases) if catalog["inventory_complete"] else None,
            "known_cases": len(cases), "inventory_complete": catalog["inventory_complete"],
            "tested_cases": len(measured_cases), "correctness_cases": len(total_outcomes),
            "passed_cases": counts["passed"], "failed_cases": failures + unmapped_failures,
            "unassigned_failures": unmapped_failures, "skipped_cases": counts["skipped"],
            "pass_rate": counts["passed"] / len(total_outcomes) if total_outcomes else None,
            "performance_rows": len(timing_rows)},
        "operators": operators, "unmatched_correctness": unmatched, "execution": execution,
        "logs": collected["logs"], "warnings": list(dict.fromkeys(warnings)),
        "policy": {"latency": "median of positive finite Task Duration(us) samples",
            "range": "min/max of per-input per-kernel median latencies",
            "coverage": "unique logical case_id; execution modes and kernel launches do not multiply coverage",
            "inventory": "all source input configurations, including optional full FA tile sweeps",
            "automatic_performance": "sum source-kernel tasks per complete test iteration, then take median; target-kernel device totals exclude reference kernels and are not end-to-end latency",
            "automatic_launches": "synchronized target launch windows; no Task Duration inferred from host wall time"}}
