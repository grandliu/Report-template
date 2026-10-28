"""Accuracy-first subprocess execution; generated artifacts stay in output."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import uuid
import re

from .execution import read_jsonl, reconcile_items
from . import profiler


@dataclass
class RunOptions:
    python: str = sys.executable
    msprof: str = "msprof"
    profiler: str = "op"
    device: int = 0
    warmup: int = 1
    iterations: int = 3
    timeout: float = 1800
    launch_count: int = 5000


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _process(argv, *, cwd, env, log, timeout):
    """No shell; terminate the process tree on timeout or interruption."""
    with Path(log).open("w", encoding="utf-8") as stream:
        try:
            process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                       start_new_session=os.name != "nt")
        except OSError as exc:
            stream.write(str(exc))
            return {"returncode": None, "error": str(exc)}
        try:
            return {"returncode": process.wait(timeout=timeout), "error": None}
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            else:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            process.wait()
            if isinstance(exc, KeyboardInterrupt):
                raise
            return {"returncode": None, "error": f"timeout after {timeout:g}s"}


def _task(catalog, operator, bundle, phase, options, selected=()):
    token = hashlib.sha256(operator["operator_id"].encode()).hexdigest()[:12]
    task_dir = Path(bundle) / "tasks" / token / phase
    task_dir.mkdir(parents=True)
    config = {"phase": phase, "root": catalog["root"], "operator": operator,
              "operator_dir": str(Path(catalog["root"]) / operator["directory"]),
              "task_dir": str(task_dir), "warmup": options.warmup, "iterations": options.iterations,
              "selected_nodeids": list(selected)}
    _write(task_dir / "config.json", config)
    env = dict(os.environ)
    env.pop("OPENTILE_PERF_ITEMS", None)
    suite_path = Path(catalog["root"]) / "suite.json"
    if suite_path.exists():
        suite = json.loads(suite_path.read_text(encoding="utf-8-sig"))
        number = re.match(r"0*(\d+)", operator["operator_id"])
        modes = suite.get("operators", {}).get(str(int(number[1])), []) if number else []
        for extra in suite.get("extra_tests", []):
            if Path(extra["path"]).parent.as_posix() == operator["directory"]:
                modes = extra.get("modes", [])
        if modes:
            env.pop("FUSION_MODE", None)
            env.pop("ENABLE_VF_OUTLINE", None)
            if modes[0] in {"max_parallel", "outline"}:
                env["FUSION_MODE"] = "max_parallel"
            if modes[0] == "outline":
                env["ENABLE_VF_OUTLINE"] = "1"
    env.update(REPORT_TASK_CONFIG=str(task_dir / "config.json"),
               ASCEND_RT_VISIBLE_DEVICES=str(options.device), OPENTILE_TEST_DEVICE="0",
               TRITON_CACHE_DIR=str(task_dir / "cache"), TRITON_DUMP_DIR=str(task_dir / "dump"),
               PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")
    env.update({str(k): str(v) for k, v in operator.get("execution", {}).get("env", {}).items()})
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1]) + os.pathsep + env.get("PYTHONPATH", "")
    if phase == "performance":
        env["PERF_ITERS"] = "1"
    files = sorted({str(Path(catalog["root"]) / test.split("::")[0]) for test in operator["tests"]})
    application = [options.python, "-m", "pytest", "-p", "report.pytest_plugin", "-q", "--tb=short",
                   "--rootdir=" + catalog["root"], "--junitxml=" + str(task_dir / "junit.xml"),
                   "-o", "python_functions=test*", "-o", "cache_dir=" + str(task_dir / "pytest_cache"), *files]
    argv = application
    if phase == "performance":
        executable = shutil.which(options.msprof) or options.msprof
        if str(executable).endswith(".py"):
            executable = [options.python, str(Path(executable).resolve())]
        argv = profiler.command(executable, application, task_dir / "msprof",
                                [k["kernel_name"] for k in operator["kernels"]],
                                backend=options.profiler, launch_count=options.launch_count)
    _write(task_dir / "invocation.json", {"argv": argv, "cwd": catalog["root"], "phase": phase,
        "device": options.device, "operator_id": operator["operator_id"],
        "environment": {k: env.get(k) for k in ("FUSION_MODE", "ENABLE_VF_OUTLINE", "TRITON_BACKEND", "ASCEND_RT_VISIBLE_DEVICES", "OPENTILE_TEST_DEVICE")}})
    print(f"[{phase}] {operator['operator_id']}", flush=True)
    outcome = _process(argv, cwd=catalog["root"], env=env, log=task_dir / "process.log", timeout=options.timeout)
    _write(task_dir / "process.json", outcome)
    return task_dir, outcome


def _outcomes(task_dir):
    grouped = defaultdict(list)
    for row in read_jsonl(Path(task_dir) / "items.jsonl"):
        grouped[row["nodeid"]].append(row)
    statuses = {}
    for node, rows in grouped.items():
        failed = [r for r in rows if r["outcome"] == "failed"]
        if failed:
            status = "failed" if failed[0]["when"] == "call" else "error"
        elif any(r["outcome"] == "skipped" for r in rows):
            status = "skipped"
        elif any(r["when"] == "call" and r["outcome"] == "passed" for r in rows) and any(r["when"] == "teardown" for r in rows):
            status = "passed"
        else:
            status = "error"
        statuses[node] = {"status": status, "message": next((r["message"] for r in rows if r.get("message")), None)}
    return statuses


def run_correctness(*, catalog, output_dir, options=None):
    options = options or RunOptions()
    records, tasks, warnings = [], [], []
    for operator in catalog["operators"]:
        if not operator["tests"]:
            warnings.append(f"{operator['operator_id']}: no pytest entry found")
            continue
        task_dir, outcome = _task(catalog, operator, output_dir, "accuracy", options)
        inventory_path = task_dir / "inventory.json"
        inventory = json.loads(inventory_path.read_text(encoding="utf-8")) if inventory_path.exists() else []
        reconcile_items(operator, inventory)
        statuses = _outcomes(task_dir)
        collection = read_jsonl(task_dir / "collection.jsonl")
        module_skipped = not inventory and collection and all(r["outcome"] == "skipped" for r in collection)
        if module_skipped:
            for test in operator["tests"]:
                records.append({"operator_id": operator["operator_id"], "nodeid": test,
                                "status": "skipped", "message": collection[0]["message"]})
        if outcome["error"] or (outcome["returncode"] not in (0, 1) and not module_skipped):
            warnings.append(f"{operator['operator_id']}: correctness process failed: {outcome}")
            records.append({"operator_id": operator["operator_id"], "nodeid": "collection/process",
                            "status": "error", "message": outcome["error"] or f"pytest exit {outcome['returncode']}"})
        passed = []
        for item in inventory:
            result = statuses.get(item["nodeid"], {"status": "error", "message": "test did not finish"})
            base = {"operator_id": operator["operator_id"], "nodeid": item["nodeid"], **result}
            if item["case_ids"]:
                records.extend({**base, "case_id": cid} for cid in item["case_ids"])
            else:
                records.append({**base, "nodeid": item["test"]})
            if result["status"] == "passed" and not outcome["error"] and outcome["returncode"] in (0, 1):
                passed.append(item["nodeid"])
        tasks.append({"operator_id": operator["operator_id"], "task_dir": str(task_dir), "passed": passed})
    _write(Path(output_dir) / "case_results.json", {"schema_version": 1, "records": records})
    status = "failed" if any(r["status"] in {"error", "failed"} for r in records) else "passed" if records and all(r["status"] == "passed" for r in records) else "partial"
    return {"status": status, "tasks": tasks, "warnings": warnings}


def run_performance(*, catalog, output_dir, correctness=None, options=None):
    options = options or RunOptions()
    correctness = correctness or {}
    records, totals, warnings, executed = [], [], [], []
    operators = {o["operator_id"]: o for o in catalog["operators"]}
    for task in correctness.get("tasks", []):
        operator = operators[task["operator_id"]]
        if not task["passed"]:
            continue
        if not operator["kernels"]:
            warnings.append(f"{operator['operator_id']}: no identified target kernels; performance skipped")
            continue
        task_dir, outcome = _task(catalog, operator, output_dir, "performance", options, task["passed"])
        rows, op_totals, issues, launches = profiler.extract(task_dir, operator, iterations=options.iterations)
        observed_launches = read_jsonl(task_dir / "launches.jsonl")
        statuses = _outcomes(task_dir)
        complete = outcome["returncode"] == 0 and all(statuses.get(node, {}).get("status") == "passed" for node in task["passed"])
        if not complete:
            issues.append(f"performance execution failed: {outcome}; affected samples excluded")
            valid_cases = {r["case_id"] for r in observed_launches
                           if statuses.get(r["nodeid"], {}).get("status") == "passed"}
            if outcome["error"] or outcome["returncode"] not in (0, 1):
                valid_cases.clear()
            rows = [r for r in rows if r["case_id"] in valid_cases]
            op_totals = [r for r in op_totals if r["case_id"] in valid_cases]
        for row in rows:
            if row.get("cceir"):
                row["cceir"] = (task_dir.relative_to(output_dir) / row["cceir"]).as_posix()
        records.extend(rows)
        totals.extend(op_totals)
        warnings.extend(f"{operator['operator_id']}: {issue}" for issue in issues)
        executed.extend({"case_id": r["case_id"], "kernel_name": r["kernel_name"]}
                        for r in observed_launches if r.get("case_id") and r["iteration"] >= 0)
        _write(task_dir / "matched_launches.json", launches)
    _write(Path(output_dir) / "performance.json", {"schema_version": 1, "records": records})
    return {"status": "passed" if records and not warnings else "partial", "warnings": warnings,
            "operator_totals": totals, "executed_kernels": executed}


def execute(*, catalog, output_dir, options=None):
    """Run all correctness first, then eligible items; export an offline bundle."""
    options = options or RunOptions()
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    bundle = output / "raw" / stamp
    bundle.mkdir(parents=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1]) + os.pathsep + env.get("PYTHONPATH", "")
    environment_result = _process([options.python, "-m", "report", "env", "--output", str(bundle / "environment.json")],
                                  cwd=catalog["root"], env=env, log=bundle / "environment.log", timeout=min(options.timeout, 60))
    _write(bundle / "run_info.json", {"run_id": stamp, "generated_at": datetime.now().astimezone().isoformat(),
        "scope": catalog["testcases_dir"], "profiler": "msprof " + options.profiler,
        "correctness_target": catalog["testcases_dir"], "benchmark_target": "passed pytest items",
        "execution": "automatic", "warmup": options.warmup, "iterations": options.iterations,
        "device": options.device})
    accuracy = run_correctness(catalog=catalog, output_dir=bundle, options=options)
    if environment_result["returncode"] != 0:
        accuracy["warnings"].append(f"test environment collection failed: {environment_result}")
    performance = run_performance(catalog=catalog, output_dir=bundle, correctness=accuracy, options=options)
    catalog["known_case_count"] = sum(len(op["cases"]) for op in catalog["operators"])
    _write(bundle / "catalog.json", catalog)
    execution = {"correctness": accuracy, "performance": performance}
    _write(bundle / "execution.json", execution)
    return bundle, execution


def run_stages(*, catalog, output_dir, correctness_runner=None, performance_runner=None):
    """Compatibility helper for injected whole-stage execution gates."""
    correctness_runner = correctness_runner or run_correctness
    performance_runner = performance_runner or run_performance
    accuracy = correctness_runner(catalog=catalog, output_dir=output_dir)
    if accuracy.get("status") != "passed":
        return {"correctness": accuracy, "performance": {"status": "skipped", "reason": "accuracy gate did not pass"}}
    if performance_runner is run_performance:
        performance = performance_runner(catalog=catalog, output_dir=output_dir, correctness=accuracy)
    else:
        performance = performance_runner(catalog=catalog, output_dir=output_dir)
    return {"correctness": accuracy, "performance": performance}
