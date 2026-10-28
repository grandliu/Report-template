"""Ascend profiler command and raw CSV adapter, independent of report rendering."""
from __future__ import annotations

from collections import defaultdict
import csv
import math
from pathlib import Path
import re

from .execution import read_jsonl


def command(msprof, application, output, kernels, *, backend="op", launch_count=5000):
    prefix = list(msprof) if isinstance(msprof, (list, tuple)) else [msprof]
    if backend == "op":
        # msOpProf defaults to the first task only. BasicInfo supplies task time;
        # disable profiler-internal warmup, since our iterations are explicit.
        names = "|".join(sorted(set(kernels)))
        if not names or any(not re.fullmatch(r"[A-Za-z0-9_]+", k) for k in kernels):
            raise ValueError("msprof op requires identified kernel symbols")
        if len(names) > 1024:
            raise ValueError("msprof op kernel filter exceeds 1024 characters")
        return [*prefix, "op", "--output=" + str(output), "--kernel-name=" + names,
                "--launch-count=" + str(launch_count), "--warm-up=0",
                "--aic-metrics=BasicInfo", *application]
    return [*prefix, "--output=" + str(output), "--ai-core=on", "--task-time=l2", *application]


def _number(value):
    try:
        result = float(str(value).strip())
        return result if math.isfinite(result) and result > 0 else None
    except (ValueError, TypeError):
        return None


def _natural(path):
    return [int(s) if s.isdigit() else s for s in re.split(r"(\d+)", str(path))]


def extract(task_dir, operator, *, iterations):
    """Match measured device tasks to observed source launches, never wall time.

    msprof: timestamp containment in synchronized launch windows.
    msprof op: when timestamps are absent, require an exact per-symbol launch
    count and consume rows in natural file/row order, including warmups.
    Ambiguous or incomplete data is diagnosed and excluded from aggregates.
    """
    task_dir = Path(task_dir)
    warnings = []
    launches = read_jsonl(task_dir / "launches.jsonl")
    known = {k["kernel_name"] for k in operator["kernels"]}
    profiler_dir = task_dir / "msprof"
    files = sorted(profiler_dir.rglob("OpBasicInfo*.csv"), key=_natural)
    if not files:
        files = sorted(profiler_dir.rglob("op_summary*.csv"), key=_natural)
    if not files:
        return [], [], ["profiler produced no OpBasicInfo.csv or op_summary*.csv"], []
    tasks = []
    for path in files:
        with path.open(encoding="utf-8-sig", errors="replace", newline="") as stream:
            for index, raw in enumerate(csv.DictReader(stream)):
                row = {k.strip(): v for k, v in raw.items() if k}
                name = (row.get("Op Name") or row.get("Kernel Name") or "").strip()
                # msOpProf supports prefix matching; retain it only if source
                # attribution is unique and the next character is a separator.
                matches = [k for k in known if name == k or re.match(re.escape(k) + r"(?:_|\W)", name)]
                if name in known:
                    matches = [name]
                duration = _number(row.get("Task Duration(us)"))
                if len(matches) != 1 or duration is None:
                    continue
                tasks.append({"kernel_name": matches[0], "duration_us": duration,
                              "start_us": _number(row.get("Task Start Time(us)")),
                              "source": str(path.relative_to(task_dir)), "row": index + 2})
    assigned = defaultdict(list)
    by_kernel = defaultdict(list)
    for index, launch in enumerate(launches):
        by_kernel[launch["kernel_name"]].append((index, launch))
    for kernel, observed in by_kernel.items():
        rows = [t for t in tasks if t["kernel_name"] == kernel]
        if rows and all(t["start_us"] is not None for t in rows):
            for row in rows:
                matches = [i for i, launch in observed if launch["start_us"] <= row["start_us"] <= launch["end_us"]]
                if len(matches) == 1:
                    assigned[matches[0]].append(row)
        elif len(rows) == len(observed) and rows:
            for (index, _), row in zip(observed, rows):
                assigned[index].append(row)
        else:
            warnings.append(f"{kernel}: {len(observed)} observed launches versus {len(rows)} profiler tasks; cannot attribute safely")
    matched_launches = []
    invalid_cases = set()
    per_kernel = defaultdict(lambda: defaultdict(float))
    per_case = defaultdict(lambda: defaultdict(float))
    artifacts = {}
    for index, launch in enumerate(launches):
        if launch["iteration"] < 0:
            continue
        cid = launch.get("case_id")
        rows = assigned[index]
        # A single source launch can generate several device tasks; sum them
        # inside that invocation, then inside the complete test iteration.
        if not cid or not rows:
            warnings.append(f"{launch['kernel_name']}: launch {launch['invocation']} has no unique case or profiler task")
            if cid:
                invalid_cases.add(cid)
            continue
        duration = sum(t["duration_us"] for t in rows)
        matched_launches.append({**launch, "duration_us": duration, "tasks": rows})
        per_kernel[(cid, launch["kernel_name"])][launch["iteration"]] += duration
        per_case[cid][launch["iteration"]] += duration
        if launch.get("cceir"):
            artifacts[(cid, launch["kernel_name"])] = launch["cceir"]
    records, totals = [], []
    for (cid, kernel), samples in per_kernel.items():
        if cid in invalid_cases or set(samples) != set(range(iterations)):
            warnings.append(f"{cid}/{kernel}: incomplete iterations; excluded from performance statistics")
            invalid_cases.add(cid)
    for (cid, kernel), samples in per_kernel.items():
        if cid not in invalid_cases:
            records.append({"operator_id": operator["operator_id"], "case_id": cid,
                "kernel_name": kernel, "task_duration_us": [samples[i] for i in range(iterations)],
                "unit": "us", "measurement_scope": "kernel_total_per_test_iteration",
                "cceir": artifacts.get((cid, kernel))})
    for cid, samples in per_case.items():
        if cid not in invalid_cases and set(samples) == set(range(iterations)):
            totals.append({"case_id": cid, "task_duration_us": [samples[i] for i in range(iterations)],
                           "measurement_scope": "sum_of_observed_target_kernel_tasks"})
    if not records:
        warnings.append("no complete, attributable performance samples")
    return records, totals, warnings, matched_launches
