"""Run from the repository root: python -m report --help."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .analyzer import analyze
from .catalog import CONFIG, ROOT, build_catalog
from .collector import collect
from .render import write_reports
from .setup_info import collect_setup_info, probe_environment

HOME = Path(__file__).resolve().parent


def main(argv=None):
    parser = argparse.ArgumentParser(description="Triton evaluation runner and offline reports.")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="identify kernels and enumerate input configurations from Python AST")
    scan.add_argument("--root", type=Path, default=ROOT)
    scan.add_argument("--catalog-config", type=Path, default=CONFIG)
    scan.add_argument("--output", type=Path, default=HOME / "outputs" / "catalog.json")
    generate = sub.add_parser("generate", help="collect an offline result directory; omit input for an empty report")
    generate.add_argument("--root", type=Path, default=ROOT)
    generate.add_argument("--catalog-config", type=Path, default=CONFIG)
    generate.add_argument("--input", type=Path)
    generate.add_argument("--output", type=Path, default=HOME / "outputs" / "latest")
    generate.add_argument("--local-test-environment", action="store_true", help="explicitly use this machine as test-host environment")
    render = sub.add_parser("render", help="render a saved run.json without scanning sources or probing environment")
    render.add_argument("run_json", type=Path)
    render.add_argument("--output", type=Path)
    env = sub.add_parser("env", help="capture an environment.json on the actual test host")
    env.add_argument("--output", type=Path, default=HOME / "outputs" / "environment.json")
    demo = sub.add_parser("demo", help="create synthetic input artifacts and render an explicitly labeled demo")
    demo.add_argument("--output", type=Path, default=HOME / "outputs" / "demo")
    execute_parser = sub.add_parser("run", help="run correctness, profile passed tests, and generate reports")
    execute_parser.add_argument("--testcases", type=Path, required=True, help="operator parent directory")
    execute_parser.add_argument("--output", type=Path, default=HOME / "outputs" / "latest")
    execute_parser.add_argument("--catalog-config", type=Path, default=CONFIG)
    execute_parser.add_argument("--python", default=sys.executable, help="test environment Python executable")
    execute_parser.add_argument("--msprof", default="msprof", help="msprof executable path")
    execute_parser.add_argument("--profiler", choices=("op", "system"), default="op")
    execute_parser.add_argument("--device", type=int, default=0, help="physical NPU index exposed as logical device 0 to tests")
    execute_parser.add_argument("--warmup", type=int, default=1)
    execute_parser.add_argument("--iterations", type=int, default=3)
    execute_parser.add_argument("--timeout", type=float, default=1800, help="timeout seconds per operator and stage")
    execute_parser.add_argument("--launch-count", type=int, default=5000, help="msprof op collection limit, including warmup launches")
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            from .runner import RunOptions, execute
            if args.device < 0 or args.warmup < 0 or args.iterations < 1 or not 0 < args.timeout < float("inf") or not 1 <= args.launch_count <= 5000:
                raise ValueError("device/warmup must be nonnegative; iterations/timeout positive; launch-count in 1..5000")
            directory = args.testcases.resolve()
            catalog = build_catalog(directory.parent, args.catalog_config, testcases_dir=directory)
            if not catalog["operators"]:
                raise ValueError(f"no operator directories found in {directory}")
            output = args.output.resolve()
            if output.is_relative_to(directory):
                raise ValueError("output must be outside the testcases directory")
            options = RunOptions(args.python, args.msprof, args.profiler, args.device,
                                 args.warmup, args.iterations, args.timeout, args.launch_count)
            bundle, execution = execute(catalog=catalog, output_dir=output, options=options)
            collected = collect(bundle)
            setup = collect_setup_info(collected["metadata"], collected["environment"])
            run = analyze(catalog, collected, setup)
            run["execution"] = execution
            run["raw_directory"] = str(bundle)
            paths = write_reports(run, output)
            print(f"status={run['status']} -> {paths['html']}")
            return 0 if run["status"] == "passed" else 1
        if args.command == "env":
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(probe_environment(), ensure_ascii=False, indent=2), encoding="utf-8")
            print(args.output)
            return 0
        if args.command == "render":
            run = json.loads(args.run_json.read_text(encoding="utf-8-sig"))
            if run.get("schema_version") != 1:
                raise ValueError("unsupported run.json schema_version")
            output = args.output or args.run_json.parent
        else:
            if args.command == "demo":
                from .demo import create_demo
                catalog = build_catalog()
                source = create_demo(catalog, HOME / "examples" / "demo_input")
                collected = collect(source)
                local = False
            else:
                snapshot = args.input / "catalog.json" if args.command == "generate" and args.input else None
                if snapshot is not None and snapshot.is_file():
                    catalog = json.loads(snapshot.read_text(encoding="utf-8-sig"))
                    if catalog.get("schema_version") != 1:
                        raise ValueError("unsupported catalog snapshot schema_version")
                else:
                    catalog = build_catalog(args.root, args.catalog_config)
                if args.command == "scan":
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
                    print(f"operators={catalog['operator_count']} known_cases={catalog['known_case_count']} inventory_complete={catalog['inventory_complete']} -> {args.output}")
                    return 0
                collected = collect(args.input)
                local = args.local_test_environment
            collected["metadata"].setdefault("generated_at", datetime.now().astimezone().isoformat())
            setup = collect_setup_info(collected["metadata"], collected["environment"], local)
            run = analyze(catalog, collected, setup)
            output = args.output
        paths = write_reports(run, output)
        print(f"status={run['status']} operators={run['summary']['tested_operators']}/{run['summary']['total_operators']} cases={run['summary']['tested_cases']}/{run['summary']['total_cases']}")
        print(paths["html"])
        return 0  # Generating a failed evaluation report is still a successful export.
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"report: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
