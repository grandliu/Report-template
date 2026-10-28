"""Explicitly synthetic artifacts demonstrating the collector contract."""
from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET


def create_demo(catalog, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    operators = {op["operator_id"]: op for op in catalog["operators"]}
    selected = [("17_test_gelu", 0, "passed"), ("21_softcap_fwd_kernel", 0, "passed"),
                ("21_softcap_fwd_kernel", 1, "failed"), ("27_softcap_bwd_kernel", 0, "passed"),
                ("46_test_rmsnorm", 0, "passed"), ("46_test_rmsnorm", 1, "skipped")]
    accuracy, performance = [], []
    suite = ET.Element("testsuite", name="synthetic-open-tile", tests=str(len(selected)), failures="1", errors="0", skipped="1")
    for index, (op_id, case_index, status) in enumerate(selected):
        op = operators[op_id]
        case = op["cases"][case_index]
        accuracy.append({"operator_id": op_id, "case_id": case["case_id"], "status": status,
                         "mode": "normal", "message": "synthetic demonstration"})
        test = ET.SubElement(suite, "testcase", name=f"synthetic_{index}", classname=op_id)
        properties = ET.SubElement(test, "properties")
        for name, value in (("operator_id", op_id), ("case_id", case["case_id"])):
            ET.SubElement(properties, "property", name=name, value=value)
        if status == "failed":
            ET.SubElement(test, "failure", message="Synthetic accuracy failure")
        elif status == "skipped":
            ET.SubElement(test, "skipped", message="Synthetic unavailable configuration")
        if status != "passed":
            continue
        for kernel_index, kernel in enumerate(op["kernels"]):
            relative = Path("artifacts") / f"input-{index}" / kernel["kernel_name"]
            target = directory / relative
            target.mkdir(parents=True, exist_ok=True)
            (target / "kernel.py").write_text(kernel["source"] + "\n", encoding="utf-8")
            # This placeholder is deliberately not presented as compiler-generated CCEIR.
            (target / "kernel.cceir").write_text(f"// DEMO ONLY: synthetic CCEIR placeholder; not compiled, not executable\n// kernel: {kernel['kernel_name']}\n// shape: {case['shape']}\nmodule {{\n  // Real CCEIR from the test toolchain belongs here.\n}}\n", encoding="utf-8")
            center = 3.5 + index * 2 + kernel_index
            performance.append({"operator_id": op_id, "case_id": case["case_id"], "mode": "normal",
                "kernel_name": kernel["kernel_name"], "task_duration_us": [center + 0.2, center, center - 0.1],
                "unit": "us", "kernel_source": (relative / "kernel.py").as_posix(),
                "cceir": (relative / "kernel.cceir").as_posix()})
    files = {"run_info.json": {"run_id": "synthetic-demo", "demo": True, "scope": "testcases", "profiler": "synthetic task duration"},
             "case_results.json": {"schema_version": 1, "records": accuracy},
             "performance.json": {"schema_version": 1, "records": performance},
             "environment.json": {"npu": "DEMO NPU (not measured)", "cann": "DEMO", "driver": "DEMO", "os": "DEMO test host"}}
    for name, payload in files.items():
        (directory / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ET.ElementTree(suite).write(directory / "correctness.xml", encoding="utf-8", xml_declaration=True)
    (directory / "logs").mkdir(exist_ok=True)
    (directory / "logs" / "correctness.log").write_text("DEMO ONLY: synthetic correctness artifacts. No NPU tests were executed.\n", encoding="utf-8")
    (directory / "logs" / "performance.log").write_text("DEMO ONLY: task durations are illustrative numbers, not measurements.\n", encoding="utf-8")
    return directory
