from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from report.__main__ import main
from report.analyzer import analyze
from report.catalog import build_catalog
from report.collector import collect
from report.runner import RunOptions, execute, _process
from report.profiler import extract, command


FAKE_TRITON = '''
class JITFunction:
    def __init__(self, fn): self.fn = fn
    def __getitem__(self, grid):
        return lambda *a, **kw: self.run(*a, **kw)
    def run(self, *a, **kw):
        self.fn(*a, **kw)
        return CompiledKernel(self)
class CompiledKernel:
    def __init__(self, fn):
        self.fn = fn
        self.asm = {"cceir": "// CPU integration fixture only\\nvoid fixture() {}"}
    def __getitem__(self, grid):
        return lambda *a, **kw: None
class ASTSource:
    def __init__(self, fn): self.fn = fn
def jit(fn): return JITFunction(fn)
def compile(src): return CompiledKernel(src.fn)
'''

FAKE_PROFILER = '''
import csv, json, os, pathlib, subprocess, sys
args = sys.argv[1:]
assert args.pop(0) == "op"
output = None
while args and args[0].startswith("--"):
    option = args.pop(0)
    if option.startswith("--output="): output = pathlib.Path(option.split("=", 1)[1])
result = subprocess.run(args, check=False)
config = json.loads(pathlib.Path(os.environ["REPORT_TASK_CONFIG"]).read_text(encoding="utf-8"))
launches = pathlib.Path(config["task_dir"]) / "launches.jsonl"
output.mkdir(parents=True)
with (output / "OpBasicInfo_20260101.csv").open("w", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["Op Name", "Task Duration(us)"])
    if launches.exists():
        for line in launches.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            duration = (2 if row["iteration"] == 0 else 4) if row["kernel_name"] == "stage_a" else 3
            writer.writerow([row["kernel_name"], duration])
sys.exit(result.returncode)
'''

TEST_SOURCE = '''
import pytest
import triton
from triton import ASTSource
@triton.jit
def stage_a(n): pass
@triton.jit
def stage_b(n): pass
@triton.jit
def compiled_only(n): pass
@pytest.mark.parametrize(("n", "use_g"), [(1, False), (2, True), (3, True)])
def test_pipeline(n, use_g):
    assert n != 3, "intentional accuracy failure"
    stage_a[(1,)](n)
    stage_a[(1,)](n)
    if use_g:
        stage_b[(1,)](n)
    binary = triton.compile(ASTSource(fn=compiled_only))
    binary[(1,)](n)
'''


class ExecutionTests(unittest.TestCase):
    def fixture(self, tmp, source=TEST_SOURCE):
        root = Path(tmp)
        directory = root / "operators" / "nested" / "pipeline"
        directory.mkdir(parents=True)
        (directory / "arbitrary_test.py").write_text(source, encoding="utf-8")
        package = root / "packages" / "triton"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text(FAKE_TRITON, encoding="utf-8")
        (package / "runtime.py").write_text("from . import JITFunction\n", encoding="utf-8")
        # The hook locates actual classes exported by triton submodules.
        with (package / "__init__.py").open("a") as stream:
            stream.write("\nfrom . import runtime\n")
        (package / "compiler.py").write_text("from . import CompiledKernel\n", encoding="utf-8")
        with (package / "__init__.py").open("a") as stream:
            stream.write("from . import compiler\n")
        msprof = root / "msprof_fixture.py"
        msprof.write_text(FAKE_PROFILER, encoding="utf-8")
        catalog = build_catalog(root, root / "absent.json", testcases_dir=root / "operators")
        return root, catalog, msprof

    def test_real_pytest_children_gate_branches_launches_and_compiled_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, catalog, msprof = self.fixture(tmp)
            env = {"PYTHONPATH": str(root / "packages"), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
            with patch.dict(os.environ, env):
                bundle, execution = execute(catalog=catalog, output_dir=root / "output",
                    options=RunOptions(msprof=str(msprof), warmup=1, iterations=2, timeout=60))
            raw = collect(bundle)
            self.assertEqual(execution["correctness"]["status"], "failed", raw["warnings"])
            self.assertEqual(execution["performance"]["status"], "passed", raw["warnings"])
            run = analyze(catalog, raw, {"metadata": {}, "environment": {}, "report_host": {}})
            self.assertEqual(run["status"], "failed")
            self.assertEqual(run["summary"]["tested_cases"], 3)
            op = run["operators"][0]
            cid = next(c["case_id"] for c in op["cases"] if c["params"]["n"] == 1)
            rows = [r for r in op["details"] if r["case_id"] == cid]
            self.assertEqual({r["kernel_name"] for r in rows}, {"stage_a", "compiled_only"})
            a = next(r for r in rows if r["kernel_name"] == "stage_a")
            self.assertEqual(a["task_duration_us"], [4, 8])
            self.assertEqual(a["latency_us"], 6)
            self.assertIn("CPU integration fixture", a["cceir"]["content"])
            self.assertEqual(next(t for t in op["device_totals"] if t["case_id"] == cid)["task_duration_us"], [7, 11])
            failed_id = next(c["case_id"] for c in op["cases"] if c["params"]["n"] == 3)
            self.assertFalse(any(r["case_id"] == failed_id for r in raw["performance"]))
            self.assertTrue((bundle / "environment.json").is_file())
            self.assertTrue(raw["logs"])

    def test_cli_runs_with_only_source_directory_and_optional_tool_paths(self):
        source = TEST_SOURCE.replace('assert n != 3, "intentional accuracy failure"', 'assert n > 0')
        with tempfile.TemporaryDirectory() as tmp:
            root, _, msprof = self.fixture(tmp, source)
            (root / "suite.json").write_text(json.dumps({"extra_tests": [{
                "path": "operators/nested/pipeline/arbitrary_test.py", "modes": ["outline"]}]}))
            with patch.dict(os.environ, {"PYTHONPATH": str(root / "packages"), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}):
                rc = main(["run", "--testcases", str(root / "operators"), "--output", str(root / "output"),
                           "--msprof", str(msprof), "--warmup", "0", "--iterations", "2", "--timeout", "60"])
            snapshot = json.loads((root / "output" / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(rc, 0, snapshot["warnings"])
            self.assertEqual(snapshot["status"], "passed", snapshot["warnings"])
            self.assertTrue((root / "output" / "report.html").is_file())
            self.assertTrue((root / "output" / "report.md").is_file())
            task_dir = Path(snapshot["execution"]["correctness"]["tasks"][0]["task_dir"])
            invocation = json.loads((task_dir / "invocation.json").read_text(encoding="utf-8"))
            self.assertEqual(invocation["environment"]["ENABLE_VF_OUTLINE"], "1")
            imported = root / "imported"
            self.assertEqual(main(["generate", "--input", snapshot["raw_directory"], "--output", str(imported)]), 0)
            rerun = json.loads((imported / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(rerun["summary"], snapshot["summary"])

    def test_missing_profiler_exports_partial_report_instead_of_fake_times(self):
        source = TEST_SOURCE.replace('assert n != 3, "intentional accuracy failure"', 'assert n > 0')
        with tempfile.TemporaryDirectory() as tmp:
            root, _, _ = self.fixture(tmp, source)
            with patch.dict(os.environ, {"PYTHONPATH": str(root / "packages"), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}):
                rc = main(["run", "--testcases", str(root / "operators"), "--output", str(root / "output"),
                           "--msprof", str(root / "missing-msprof"), "--timeout", "60"])
            self.assertEqual(rc, 1)
            snapshot = json.loads((root / "output" / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["status"], "partial")
            self.assertEqual(snapshot["summary"]["performance_rows"], 0)
            self.assertTrue(snapshot["warnings"])

    def test_driver_loops_are_attributed_to_individual_shapes(self):
        source = '''
import triton
@triton.jit
def stage_a(n): pass
def test_shapes():
    for dtype_name in ("f16", "f32"):
        for shape in ((16,), (32,)):
            stage_a[(1,)](shape[0])
'''
        with tempfile.TemporaryDirectory() as tmp:
            root, catalog, msprof = self.fixture(tmp, source)
            self.assertEqual(len(catalog["operators"][0]["cases"]), 4)
            with patch.dict(os.environ, {"PYTHONPATH": str(root / "packages"), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}):
                bundle, execution = execute(catalog=catalog, output_dir=root / "output",
                    options=RunOptions(msprof=str(msprof), warmup=1, iterations=2, timeout=60))
            data = collect(bundle)
            self.assertEqual(execution["performance"]["status"], "passed", data["warnings"])
            self.assertEqual(len(data["performance"]), 4)
            self.assertTrue(all(r["task_duration_us"] == [2, 4] for r in data["performance"]))

    def test_module_skip_is_not_reported_as_collection_failure(self):
        source = 'import pytest\npytest.skip("no NPU fixture", allow_module_level=True)\ndef test_skipped(): pass\n'
        with tempfile.TemporaryDirectory() as tmp:
            root, catalog, _ = self.fixture(tmp, source)
            with patch.dict(os.environ, {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}):
                bundle, _ = execute(catalog=catalog, output_dir=root / "output", options=RunOptions(timeout=60))
            data = collect(bundle)
            self.assertEqual([r["status"] for r in data["correctness"]], ["skipped"])
            self.assertEqual(data["performance"], [])

    def test_explicit_optional_sweep_adapter_preserves_other_skip_marks(self):
        source = '''
import pytest
@pytest.mark.skipif(True, reason="optional sweep")
def test_enabled(): pass
@pytest.mark.skipif(True, reason="missing hardware")
def test_still_skipped(): pass
'''
        with tempfile.TemporaryDirectory() as tmp:
            root, catalog, _ = self.fixture(tmp, source)
            catalog["operators"][0]["execution"] = {"enable_skipif_reasons": ["optional sweep"]}
            from report.runner import run_correctness
            with patch.dict(os.environ, {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}):
                run_correctness(catalog=catalog, output_dir=root / "output", options=RunOptions(timeout=60))
            records = collect(root / "output")["correctness"]
            self.assertEqual([r["status"] for r in records], ["passed", "skipped"])

    def test_collection_failure_is_preserved_in_report(self):
        source = 'raise RuntimeError("broken collection fixture")\ndef test_unreachable(): pass\n'
        with tempfile.TemporaryDirectory() as tmp:
            root, catalog, _ = self.fixture(tmp, source)
            with patch.dict(os.environ, {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}):
                bundle, _ = execute(catalog=catalog, output_dir=root / "output", options=RunOptions(timeout=60))
            run = analyze(catalog, collect(bundle), {"metadata": {}, "environment": {}, "report_host": {}})
            self.assertEqual(run["status"], "failed")
            self.assertEqual(run["summary"]["unassigned_failures"], 1)

    def test_timestamp_free_mismatched_counts_never_become_latency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "msprof").mkdir()
            launch = {"case_id": "c", "kernel_name": "k", "iteration": 0, "invocation": 1}
            (root / "launches.jsonl").write_text(json.dumps(launch))
            (root / "msprof" / "OpBasicInfo.csv").write_text("Op Name,Task Duration(us)\nk,2\nk,3\n")
            records, _, warnings, _ = extract(root, {"operator_id": "o", "kernels": [{"kernel_name": "k"}]}, iterations=1)
            self.assertFalse(records)
            self.assertTrue(any("cannot attribute safely" in w for w in warnings))

    def test_timestamp_adapter_sums_tasks_and_rejects_incomplete_iterations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "msprof").mkdir()
            launches = [{"case_id": "c", "kernel_name": "k", "iteration": i,
                         "invocation": i + 1, "start_us": 100 + i * 100, "end_us": 190 + i * 100} for i in range(2)]
            (root / "launches.jsonl").write_text("\n".join(json.dumps(r) for r in launches))
            with (root / "msprof" / "op_summary_1.csv").open("w", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["Op Name", "Task Duration(us)", "Task Start Time(us)"])
                writer.writerows([["k", 2, 110], ["k", 3, 120], ["reference", 100, 130], ["k", 7, 210]])
            op = {"operator_id": "op", "kernels": [{"kernel_name": "k"}]}
            records, totals, warnings, _ = extract(root, op, iterations=2)
            self.assertEqual(records[0]["task_duration_us"], [5, 7])
            self.assertFalse(warnings)
            self.assertEqual(totals[0]["task_duration_us"], [5, 7])
            self.assertEqual(extract(root, op, iterations=3)[0], [])

    def test_command_collects_all_target_kernels_and_timeout_is_recorded(self):
        argv = command("msprof", ["python", "test.py"], "out", ["a", "b"])
        self.assertEqual(argv[:2], ["msprof", "op"])
        self.assertIn("--kernel-name=a|b", argv)
        self.assertIn("--launch-count=5000", argv)
        with tempfile.TemporaryDirectory() as tmp:
            result = _process([sys.executable, "-c", "import time; time.sleep(10)"], cwd=tmp,
                              env=dict(os.environ), log=Path(tmp) / "process.log", timeout=.1)
            self.assertIn("timeout", result["error"])


if __name__ == "__main__":
    unittest.main()
