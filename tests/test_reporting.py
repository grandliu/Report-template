from __future__ import annotations

from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest
import html
import re

from report.analyzer import analyze
from report.catalog import build_catalog
from report.collector import collect
from report.demo import create_demo
from report.render import anchor, render_html, write_reports
from report.runner import run_stages
from report.source import display_name, scan_kernels
from report.highlight import python_html, cpp_html
from report.render import operator_code_view
from report.setup_info import collect_setup_info
from unittest.mock import patch


class ReportTests(unittest.TestCase):
    maxDiff = 1500
    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()
        cls.ops = {op["operator_id"]: op for op in cls.catalog["operators"]}

    def run_data(self, collected=None):
        return analyze(self.catalog, collected or collect(), {"metadata": {}, "environment": {}, "report_host": {}})

    def test_source_kernels_and_unique_inventory(self):
        self.assertEqual(self.catalog["operator_count"], 51)
        self.assertTrue(self.catalog["inventory_complete"], self.catalog["warnings"])
        self.assertEqual([k["kernel_name"] for k in self.ops["17_test_gelu"]["kernels"]], ["_gelu_fwd_kernel"])
        self.assertEqual(self.ops["17_test_gelu"]["jit_helpers"][0]["kernel_name"], "gelu_tanh_approx")
        self.assertEqual(len(self.ops["27_softcap_bwd_kernel"]["cases"]), 9)
        self.assertEqual(len(self.ops["04__c_conv_varlen"]["cases"]), 10)
        self.assertEqual(len(self.ops["06_ttest_causal_conv1d_update_state"]["cases"]), 7)
        self.assertEqual(len(self.ops["extra_tests/fa"]["cases"]), 114)
        ids = [c["case_id"] for op in self.catalog["operators"] for c in op["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(display_name("_gelu_fwd_kernel"), "gelu")
        self.assertEqual(display_name("fused_matmul_bwd_w_kernel"), "fused_matmul_bwd_w")
        self.assertTrue(all(op["category"] != "other" for op in self.catalog["operators"]))

    def test_discovery_uses_launches_aliases_and_not_folder_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "misleading_name"
            source.mkdir()
            (source / "arbitrary.py").write_text("from triton import jit as decorate\nfrom triton.compiler import ASTSource as Source\n@decorate\ndef helper(x): return x\n@decorate\ndef actual_entry(x): return helper(x)\ns = Source(fn=actual_entry)\n", encoding="utf-8")
            kernels, _ = scan_kernels(source, root)
            self.assertEqual([k["kernel_name"] for k in kernels if k["role"] == "entry"], ["actual_entry"])

    def test_empty_report_has_full_inventory_without_fake_pass(self):
        run = self.run_data()
        self.assertEqual(run["status"], "not_run")
        self.assertEqual(run["summary"]["tested_cases"], 0)
        self.assertIsNone(run["summary"]["pass_rate"])
        page = render_html(run)
        self.assertIn("0/51", page)
        self.assertTrue(f"0/{self.catalog['known_case_count']}" in page, "empty report should expose the full input denominator")
        self.assertNotIn("{{TITLE}}", page)
        for op in run["operators"]:
            self.assertIn(f"id='{anchor(op['operator_id'])}'", page)

    def test_demo_collects_accuracy_performance_logs_and_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = collect(create_demo(self.catalog, tmp))
            run = self.run_data(data)
            self.assertEqual(run["summary"]["tested_operators"], 4)
            self.assertEqual(run["summary"]["tested_cases"], 6)
            self.assertEqual(run["summary"]["passed_cases"], 4)
            self.assertEqual(run["summary"]["failed_cases"], 1)
            self.assertEqual(run["summary"]["skipped_cases"], 1)
            self.assertEqual(run["status"], "failed")
            gelu = next(op for op in run["operators"] if op["operator_id"] == "17_test_gelu")
            self.assertEqual(gelu["details"][0]["latency_us"], 3.5)
            self.assertIn("DEMO ONLY", gelu["details"][0]["cceir"]["content"])
            self.assertEqual(len(run["logs"]), 2)
            out = Path(tmp) / "out"
            write_reports(run, out)
            snapshot = json.loads((out / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(render_html(run), render_html(snapshot))

    def test_duplicate_modes_and_kernels_do_not_inflate_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = collect(create_demo(self.catalog, tmp))
            row = deepcopy(data["performance"][0])
            row["mode"] = "outline"
            data["performance"].append(row)
            acc = deepcopy(data["correctness"][-6])
            acc.update(case_id=row["case_id"], operator_id=row["operator_id"], status="passed", mode="outline")
            data["correctness"].append(acc)
            run = self.run_data(data)
            self.assertEqual(run["summary"]["tested_cases"], 6)

    def test_kernel_specific_failure_is_not_overwritten(self):
        op = self.ops["27_softcap_bwd_kernel"]
        cid = op["cases"][0]["case_id"]
        data = collect()
        data["correctness"] = [{"operator_id": op["operator_id"], "case_id": cid,
            "kernel_name": kernel["kernel_name"], "status": status, "source": "case_results.json"}
            for kernel, status in zip(op["kernels"], ["failed", "passed"])]
        run = self.run_data(data)
        details = next(o for o in run["operators"] if o["operator_id"] == op["operator_id"])["details"]
        self.assertEqual([r["accuracy"] for r in details[:2]], ["failed", "passed"])
        self.assertEqual(run["summary"]["failed_cases"], 1)

    def test_failed_bundle_is_not_falsely_expanded_to_all_shapes(self):
        data = collect()
        op = self.ops["27_softcap_bwd_kernel"]
        data["correctness"] = [{"nodeid": op["tests"][0], "status": "failed", "source": "correctness.xml"}]
        run = self.run_data(data)
        self.assertEqual(run["summary"]["tested_cases"], 0)
        self.assertEqual(run["summary"]["failed_cases"], 1)
        self.assertTrue(any("per-input outcomes required" in w for w in run["warnings"]))

    def test_passed_bundle_expands_inputs_once(self):
        data = collect()
        op = self.ops["27_softcap_bwd_kernel"]
        data["correctness"] = [{"nodeid": op["tests"][0], "status": "passed", "source": "correctness.xml"}]
        run = self.run_data(data)
        self.assertEqual(run["summary"]["tested_cases"], 9)
        self.assertEqual(run["status"], "partial")

    def test_bad_samples_missing_artifacts_and_bad_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_demo(self.catalog, root)
            p = root / "performance.json"
            raw = json.loads(p.read_text())
            raw["records"][0]["task_duration_us"] = [-1, float("nan")]
            raw["records"][1]["cceir"] = "missing.cceir"
            p.write_text(json.dumps(raw))
            (root / "correctness.xml").write_text("<broken>")
            data = collect(root)
            self.assertTrue(any("invalid task_duration" in w for w in data["warnings"]))
            self.assertTrue(any("missing.cceir" in w for w in data["warnings"]))
            self.assertEqual(data["unassigned_errors"], 1)

    def test_html_escapes_code_and_template_tokens_are_inert(self):
        run = self.run_data()
        row = run["operators"][0]["details"][0]
        row["cceir"] = {"path": "test.cceir", "content": "</code><script>alert(1)</script>{{TITLE}}"}
        page = render_html(run)
        self.assertTrue("&lt;script&gt;" in page and "{{TITLE}}" in page)
        self.assertNotIn("<script>alert(1)</script>", page)

    def test_highlighting_preserves_copyable_source(self):
        samples = [
            (python_html, '@triton.jit\ndef test(x):\n    # 中文 <tag>\n    return "<&>" + str(1.25)\n'),
            (python_html, 'def truncated(:\n  "unterminated'),
            (cpp_html, '#include <cstdint>\n// 中文\n__aicore__ void test(float *p) { p[0] = 1.25f; }\n'),
            (cpp_html, '</code><script>alert(1)</script>{{TITLE}}'),
        ]
        for highlighter, source in samples:
            rendered = highlighter(source)
            self.assertEqual(html.unescape(re.sub(r"<[^>]*>", "", rendered)), source)
            self.assertTrue('class="syntax-' in rendered)

    def test_operator_code_deduplicates_shapes_and_retains_different_versions(self):
        run = self.run_data()
        op = next(o for o in run["operators"] if o["operator_id"] == "27_softcap_bwd_kernel")
        viewer = operator_code_view(op)
        self.assertEqual(viewer.count("class='language-python'"), 2)
        self.assertEqual(viewer.count("class='code-view'"), 1)
        op["details"][0]["cceir"] = {"path": "first.cce", "content": "void test() { return; }"}
        op["details"][2]["cceir"] = {"path": "second.cce", "content": "void test() { int x = 1; }"}
        viewer = operator_code_view(op)
        self.assertTrue("class='code-variant'" in viewer)
        self.assertEqual(viewer.count("class='language-cpp'"), 2)

    def test_runner_enforces_gate(self):
        calls = []
        def accuracy(**kwargs):
            calls.append("accuracy")
            return {"status": "failed"}
        def performance(**kwargs):
            calls.append("performance")
            return {"status": "passed"}
        result = run_stages(catalog={}, output_dir="unused", correctness_runner=accuracy, performance_runner=performance)
        self.assertEqual(calls, ["accuracy"])
        self.assertEqual(result["performance"]["status"], "skipped")
        def passed(**kwargs):
            return {"status": "passed"}
        run_stages(catalog={}, output_dir="unused", correctness_runner=passed, performance_runner=performance)
        self.assertEqual(calls, ["accuracy", "performance"])

    def test_target_environment_is_not_filled_from_report_host(self):
        with patch("report.setup_info.probe_environment", return_value={"cann": "HOST-CANN", "os": "HOST"}):
            setup = collect_setup_info({}, {"os": "TEST"})
            self.assertIsNone(setup["environment"]["cann"])
            self.assertEqual(setup["environment"]["os"], "TEST")
            self.assertEqual(setup["report_host"]["cann"], "HOST-CANN")

    def test_unknown_inputs_are_diagnostics_not_coverage(self):
        data = collect()
        data["correctness"] = [{"case_id": "unregistered", "status": "passed", "source": "case_results.json"}]
        run = self.run_data(data)
        self.assertEqual(run["summary"]["tested_cases"], 0)
        self.assertTrue(any("unknown case_id" in w for w in run["warnings"]))

    def test_generated_html_has_unique_ids_and_valid_internal_links(self):
        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.ids, self.hrefs = [], []
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if "id" in attrs:
                    self.ids.append(attrs["id"])
                if attrs.get("href", "").startswith("#"):
                    self.hrefs.append(attrs["href"][1:])
        parser = Links()
        parser.feed(render_html(self.run_data()))
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertTrue(set(parser.hrefs).issubset(parser.ids))


if __name__ == "__main__":
    unittest.main()
