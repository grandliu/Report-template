"""Collect environment without importing accelerators; preserve the test-host boundary."""
from __future__ import annotations

import importlib.metadata
import os
import platform
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _command(args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=5, check=False)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _package(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _version(paths):
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = re.search(r"(?:version|Version|package_version)\s*[:=]\s*([^\s]+)", text)
        if match:
            return match.group(1)
    return None


def probe_environment():
    cann_root = Path(os.environ.get("ASCEND_HOME_PATH", "/usr/local/Ascend/ascend-toolkit/latest"))
    return {"captured_at": datetime.now().astimezone().isoformat(), "hostname": platform.node(),
            "npu": _command(["npu-smi", "info"]), "cpu": platform.machine(),
            "cann": _version([cann_root / "version.cfg", cann_root / "version.info", *sorted(cann_root.glob("*/ascend_toolkit_install.info"))]),
            "driver": _version([Path("/usr/local/Ascend/driver/version.info")]),
            "pytorch": _package("torch"), "pytorch_npu": _package("torch-npu"),
            "triton": _package("triton"), "opentile_converter": _package("opentile-converter"),
            "otrt_jit": _package("otrt-jit"), "opentile_as": _command(["opentileas", "--version"]),
            "python": sys.version.split()[0], "os": platform.platform(),
            "container": os.environ.get("container") or ("docker" if Path("/.dockerenv").exists() else None)}


def collect_setup_info(metadata, test_environment=None, local_test_environment=False):
    local = probe_environment()
    # Only an explicit opt-in declares the report machine to be the test machine.
    target = test_environment if test_environment is not None else local if local_test_environment else {}
    return {"metadata": {"framework": "OpenTile Reporting 0.1.0", "date": metadata.get("generated_at"),
                "evaluation_scope": metadata.get("scope", "testcases"),
                "benchmark": "OpenTile kernel input suite", "profiler": metadata.get("profiler", "msprof"),
                "run_id": metadata.get("run_id"), "git_commit": metadata.get("git_commit"),
                "correctness_target": metadata.get("correctness_target", "testcases/"),
                "benchmark_target": metadata.get("benchmark_target", "offline performance.json"),
                "environment_source": "input environment.json" if test_environment is not None else "local probe (explicit)" if local_test_environment else "not provided",
                "data_kind": "DEMO / 模拟数据" if metadata.get("demo") else "automatic / 自动执行" if metadata.get("execution") == "automatic" else "offline imported / 离线导入"},
            "environment": {key: target.get(key) for key in local}, "report_host": local}
