"""Child-process plugin: collect pytest identity and synchronized target launches.

Loaded only by ``report run``. It never imports Torch/Triton itself: tests retain
control over backend initialization and pytest.importorskip behavior.
"""
from __future__ import annotations

import functools
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import pytest

from .execution import json_value, match_cases, reconcile_items

_config = None
_current = None
_iteration = None
_depth = 0
_sequence = 0
_patched = []
_phase = "accuracy"


def _emit(filename, value):
    with (Path(_config["task_dir"]) / filename).open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")


def pytest_configure(config):
    global _config, _phase
    _config = json.loads(Path(os.environ["REPORT_TASK_CONFIG"]).read_text(encoding="utf-8"))
    _phase = _config["phase"]
    sys.path.insert(0, _config["operator_dir"])


def pytest_collection_modifyitems(session, config, items):
    inventory = []
    root = Path(_config["root"])
    for item in items:
        test = Path(item.path).resolve().relative_to(root).as_posix() + "::" + item.originalname
        callspec = getattr(item, "callspec", None)
        inventory.append({"nodeid": item.nodeid, "test": test,
                          "params": json_value(callspec.params) if callspec else {},
                          "label": callspec.id if callspec else None})
    reconcile_items(_config["operator"], inventory)
    allowed = set(_config.get("selected_nodeids", []))
    for item, row in zip(items, inventory):
        item._report_identity = row
        # Explicit repository adapter: enable optional benchmark tests during
        # both accuracy and profiling, without overriding unrelated skip marks.
        enabled = _config["operator"].get("execution", {}).get("enable_skipif_reasons", [])
        item.own_markers[:] = [mark for mark in item.own_markers
                              if not (mark.name == "skipif" and mark.kwargs.get("reason") in enabled)]
        item.user_properties.extend([("operator_id", _config["operator"]["operator_id"]),
                                     ("nodeid", item.nodeid)])
        if len(row["case_ids"]) == 1:
            item.user_properties.append(("case_id", row["case_ids"][0]))
    if _phase == "performance":
        retained = [item for item in items if item.nodeid in allowed]
        deselected = [item for item in items if item.nodeid not in allowed]
        config.hook.pytest_deselected(items=deselected)
        items[:] = retained
    (Path(_config["task_dir"]) / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    global _current
    _current = item._report_identity
    yield
    _current = None


def pytest_runtest_logreport(report):
    _emit("items.jsonl", {"nodeid": report.nodeid, "when": report.when,
                          "outcome": report.outcome, "xfail": hasattr(report, "wasxfail"),
                          "message": str(report.longrepr) if report.failed or report.skipped else None})


def pytest_collectreport(report):
    if report.failed or report.skipped:
        _emit("collection.jsonl", {"nodeid": report.nodeid, "outcome": report.outcome,
                                   "message": str(report.longrepr)})


def _sync():
    torch = sys.modules.get("torch")
    npu = getattr(torch, "npu", None) if torch else None
    if npu is not None:
        npu.synchronize()


def _identity(obj):
    """Resolve the original source function, not a generated binary display name."""
    seen = set()
    pending = [obj]
    known = {k["kernel_name"] for k in _config["operator"]["kernels"]}
    while pending:
        value = pending.pop(0)
        if value is None or id(value) in seen:
            continue
        seen.add(id(value))
        name = getattr(value, "__name__", None)
        if name in known:
            return name
        name = getattr(value, "name", None)
        if isinstance(name, str) and name in known:
            return name
        for attr in ("fn", "src"):
            child = getattr(value, attr, None)
            if child is not None:
                pending.append(child)
    return None


def _case_context(args, kwargs):
    params = {}
    # Driver loops commonly keep shape/dtype/profile in their Python locals.
    frame = sys._getframe(1)
    root = Path(_config["operator_dir"])
    while frame:
        try:
            inside = Path(frame.f_code.co_filename).resolve().is_relative_to(root)
        except (ValueError, OSError):
            inside = False
        if inside:
            for key, value in frame.f_locals.items():
                normalized = json_value(value)
                if not isinstance(normalized, dict) or "unresolved_type" not in normalized:
                    params[key] = normalized
        frame = frame.f_back
    params.update(_current["params"])
    shape, dtype = None, None
    for value in [*args, *kwargs.values()]:
        if hasattr(value, "shape") and hasattr(value, "dtype"):
            try:
                shape = list(value.shape)
                dtype = str(value.dtype).removeprefix("torch.")
                params.setdefault("shape", shape)
                params.setdefault("dtype", dtype)
                break
            except (TypeError, ValueError):
                pass
    matches = match_cases(_config["operator"], _current["test"], params, _current.get("label"))
    return matches[0]["case_id"] if len(matches) == 1 else None, shape, dtype


def _artifact(obj):
    asm = getattr(obj, "asm", None)
    if not isinstance(asm, dict):
        return None
    for kind in ("cceir", "cce", "cce_ir"):
        text = asm.get(kind)
        if isinstance(text, str) and text:
            name = "compiled-" + hashlib.sha256(text.encode()).hexdigest()[:20] + "." + kind
            relative = "artifacts/" + name
            target = Path(_config["task_dir"]) / relative
            target.parent.mkdir(exist_ok=True)
            target.write_text(text, encoding="utf-8")
            return relative
    return None


def _launch(original, obj, args, kwargs):
    global _depth, _sequence
    if _current is None or _iteration is None or _depth or kwargs.get("warmup", False):
        return original(*args, **kwargs)
    kernel = _identity(obj)
    if kernel is None:
        return original(*args, **kwargs)
    cid, shape, dtype = _case_context(args, kwargs)
    _depth += 1
    try:
        _sync()
        start = time.time_ns() / 1000
        result = original(*args, **kwargs)
        _sync()
        end = time.time_ns() / 1000
        artifact = _artifact(result) or _artifact(obj)
        _sequence += 1
        _emit("launches.jsonl", {"nodeid": _current["nodeid"], "case_id": cid,
              "kernel_name": kernel, "iteration": _iteration, "invocation": _sequence,
              "start_us": start, "end_us": end, "shape": shape, "dtype": dtype,
              "cceir": artifact})
        return result
    finally:
        _depth -= 1


def _install_hooks():
    """Patch standard Triton host launch interfaces after test-module imports."""
    classes = set()
    for name, module in list(sys.modules.items()):
        if name.startswith("triton.") and module is not None:
            for attr in ("JITFunction", "CompiledKernel"):
                cls = getattr(module, attr, None)
                if isinstance(cls, type):
                    classes.add(cls)
    for cls in classes:
        method = "run" if cls.__name__ == "JITFunction" else "__getitem__"
        original = getattr(cls, method, None)
        if original is None or getattr(original, "_report_hook", False):
            continue
        if method == "run":
            def factory(fn):
                @functools.wraps(fn)
                def run(self, *args, **kwargs):
                    return _launch(functools.partial(fn, self), self, args, kwargs)
                return run
        else:
            def factory(fn):
                @functools.wraps(fn)
                def getitem(self, grid):
                    launcher = fn(self, grid)
                    @functools.wraps(launcher)
                    def invoke(*args, **kwargs):
                        return _launch(launcher, self, args, kwargs)
                    return invoke
                return getitem
        wrapper = factory(original)
        wrapper._report_hook = True
        setattr(cls, method, wrapper)
        _patched.append((cls, method, original))
    return len(_patched)


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    global _iteration
    if _phase != "performance":
        return None
    import inspect
    if inspect.iscoroutinefunction(pyfuncitem.obj):
        pytest.fail("report performance adapter does not support async tests")
    if not _install_hooks():
        pytest.fail("No supported Triton JITFunction/CompiledKernel launch interface found")
    kwargs = {name: pyfuncitem.funcargs[name] for name in pyfuncitem._fixtureinfo.argnames}
    try:
        for warmup in range(_config["warmup"]):
            _iteration = -warmup - 1
            pyfuncitem.obj(**kwargs)
        _sync()
        for iteration in range(_config["iterations"]):
            _iteration = iteration
            pyfuncitem.obj(**kwargs)
            _sync()
    finally:
        _iteration = None
    return True


def pytest_unconfigure(config):
    for cls, method, original in reversed(_patched):
        setattr(cls, method, original)
    _patched.clear()
