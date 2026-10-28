"""Source-derived operator/kernel catalog and auditable logical input inventory."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from .source import StaticValues, Unresolved, bind, dotted, read_module, scan_kernels

ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path(__file__).with_name("operator_catalog.json")
CATEGORIES = {
    "elementwise": "Elementwise / 逐元素",
    "reduction": "Reduction / 规约",
    "normalization": "Normalization / 归一化",
    "matmul": "Matmul / 矩阵乘",
    "attention": "Attention / 注意力",
    "convolution": "Convolution / 卷积",
    "sampling": "Sampling / 采样",
    "data_movement": "Data Movement / 数据搬运与索引",
    "scan_recurrence": "Scan & Recurrence / 扫描与递推",
    "linear_algebra": "Linear Algebra / 线性代数",
    "other": "Other / 未分类",
}


def case_id(operator_id, test, params):
    text = json.dumps([operator_id, test, params], sort_keys=True, ensure_ascii=True)
    return f"{operator_id}:{hashlib.sha256(text.encode()).hexdigest()[:16]}"


def make_case(operator_id, test, params, label=None):
    dtype = params.get("dtype", params.get("dtype_name"))
    aliases = {"f16": "float16", "fp16": "float16", "bf16": "bfloat16", "f32": "float32", "fp32": "float32"}
    dtype = aliases.get(dtype, dtype) if isinstance(dtype, str) else dtype
    shape = params.get("shape", params.get("input_shape"))
    if shape is None:
        shape = {k: v for k, v in params.items() if "shape" in k.lower() or k in {"B", "T", "H", "HV", "K", "V", "M", "N", "m", "n", "k", "batch_size", "vocab_size", "sl", "hs"}}
    return {"case_id": case_id(operator_id, test, params), "test": test, "params": params,
            "shape": shape or None, "dtype": dtype, "label": label}


def discover_directories(root, testcases_dir=None):
    result = []
    def visit(parent):
        for path in sorted(parent.iterdir()):
            if not path.is_dir() or path.name.startswith((".", "__")):
                continue
            if any(path.glob("*.py")):
                result.append(path)
            else:
                visit(path)
    visit(testcases_dir or root / "testcases")
    return result


def _parameter_rows(function, env, values):
    rows = [({}, None)]
    for deco in function.decorator_list:
        if not isinstance(deco, ast.Call) or not dotted(deco.func).endswith("parametrize"):
            continue
        names = values.value(deco.args[0], env)
        names = [x.strip() for x in names.split(",")] if isinstance(names, str) else names
        items = values.value(deco.args[1], env)
        expanded = []
        for item in items:
            label = item.get("id") if isinstance(item, dict) and "__param__" in item else None
            vals = item["__param__"] if isinstance(item, dict) and "__param__" in item else ([item] if len(names) == 1 else item)
            if len(vals) != len(names):
                raise Unresolved("parametrize arity")
            for prev, old_label in rows:
                expanded.append(({**prev, **dict(zip(names, vals))}, label or old_label))
        rows = expanded
    return rows


def _input_loops(statements, env, values):
    """Only expand driver-level shape/dtype loops, never arithmetic loops inside kernels."""
    output = [({}, env)]
    for stmt in statements:
        if isinstance(stmt, ast.For):
            names = [n.id for n in ast.walk(stmt.target) if isinstance(n, ast.Name)]
            if not any("shape" in n.lower() or "dtype" in n.lower() for n in names):
                continue
            expanded = []
            for params, scope in output:
                for item in values.value(stmt.iter, scope):
                    local = dict(scope)
                    bind(stmt.target, item, local)
                    additions = {n: local[n] for n in names}
                    for inner, _ in _input_loops(stmt.body, local, values):
                        expanded.append(({**params, **additions, **inner}, local))
            output = expanded
    return output


def build_catalog(root=ROOT, config_path=CONFIG, testcases_dir=None):
    root = Path(root).resolve()
    testcases_dir = Path(testcases_dir).resolve() if testcases_dir is not None else root / "testcases"
    if not testcases_dir.is_dir():
        raise ValueError(f"testcases directory does not exist: {testcases_dir}")
    configuration = json.loads(Path(config_path).read_text(encoding="utf-8")) if Path(config_path).exists() else {}
    settings = configuration.get("operators", {})
    values = StaticValues()
    operators, warnings = [], []
    for directory in discover_directories(root, testcases_dir):
        operator_id = directory.relative_to(testcases_dir).as_posix()
        config = settings.get(operator_id, {})
        kernels, modules = scan_kernels(directory, root)
        if config.get("entry_kernels"):
            for kernel in kernels:
                if kernel["kernel_name"] in config["entry_kernels"]:
                    kernel["role"] = "entry"
                    kernel["evidence"].append({"kind": "reviewed_override", "reason": config.get("kernel_note", "indirect launch")})
        entries = [k for k in kernels if k["role"] == "entry"]
        entry_file = directory / f"{directory.name}.py"
        if not entry_file.exists():
            entry_file = next((p for p, _, tree in modules if any(isinstance(n, ast.FunctionDef) and n.name.startswith("test") for n in tree.body)), None)
        tests, cases, issues = [], [], []
        for path, _, tree in modules:
            if not any(isinstance(n, ast.FunctionDef) and n.name.startswith("test") for n in tree.body):
                continue
            imported = {}
            module_constants = {p.stem: values.globals(t) for p, _, t in modules}
            for statement in tree.body:
                if isinstance(statement, ast.ImportFrom) and statement.module in module_constants:
                    for alias in statement.names:
                        if alias.name in module_constants[statement.module]:
                            imported[alias.asname or alias.name] = module_constants[statement.module][alias.name]
            env = values.globals(tree, imported)
            for fn in tree.body:
                if not isinstance(fn, ast.FunctionDef) or not fn.name.startswith("test"):
                    continue
                test = f"{path.relative_to(root).as_posix()}::{fn.name}"
                tests.append(test)
                try:
                    for params, label in _parameter_rows(fn, env, values):
                        # Constant tensor inputs in a single test can supply metadata.
                        params = dict(params)
                        for node in ast.walk(fn):
                            if isinstance(node, ast.Call) and dotted(node.func) in {"torch.rand", "torch.randn", "torch.empty"}:
                                try:
                                    if "shape" not in params and node.args:
                                        shape = values.value(node.args[0], {**env, **params})
                                        if isinstance(shape, list):
                                            params["shape"] = shape
                                    if "dtype" not in params:
                                        dtype_node = next((k.value for k in node.keywords if k.arg == "dtype"), None)
                                        if dtype_node:
                                            params["dtype"] = values.value(dtype_node, {**env, **params})
                                except (Unresolved, TypeError, ValueError, KeyError, IndexError):
                                    pass
                        for inner, _ in _input_loops(fn.body, {**env, **params}, values):
                            cases.append(make_case(operator_id, test, {**params, **inner}, label))
                except (Unresolved, TypeError, ValueError, KeyError, IndexError) as exc:
                    issues.append(f"{test}: {exc}")
        if "case_plan" in config:
            cases, issues = [], []
            plan = config["case_plan"]
            tree = next(tree for path, _, tree in modules if path == entry_file)
            env = values.globals(tree)
            for group in plan:
                test = f"{entry_file.relative_to(root).as_posix()}::{group['test']}"
                fixed = dict(group.get("fixed", {}))
                fixed.update({k: values.value(ast.parse(v, mode="eval").body, env) for k, v in group.get("fixed_expressions", {}).items()})
                rows = [fixed]
                for axis in group.get("axes", []):
                    items = values.value(ast.parse(axis["expression"], mode="eval").body, env)
                    expanded = []
                    names = axis["names"]
                    for item in items:
                        if isinstance(item, dict) and "__param__" in item:
                            item = item["__param__"]
                        vals = [item] if len(names) == 1 else item
                        for row in rows:
                            expanded.append({**row, **(item if axis.get("merge") else dict(zip(names, vals)))})
                    rows = expanded
                cases.extend(make_case(operator_id, test, row) for row in rows)
        unique = {}
        for case in cases:
            if case["case_id"] in unique:
                unique[case["case_id"]]["source_occurrences"] += 1
            else:
                case["source_occurrences"] = 1
                unique[case["case_id"]] = case
        cases = list(unique.values())
        # Never pretend a dynamically unresolved inventory is an exact denominator.
        complete = bool(tests) and not issues and not config.get("inventory_unresolved")
        issues.extend(config.get("inventory_unresolved", []))
        category = config.get("category", "other")
        names = list(dict.fromkeys(k["display_name"] for k in entries))
        name = " / ".join(names) if names else "待识别 kernel"
        operator = {"operator_id": operator_id, "directory": directory.relative_to(root).as_posix(),
                    "name": name, "category": category, "category_label": CATEGORIES.get(category, category),
                    "kernels": entries, "jit_helpers": [k for k in kernels if k["role"] != "entry"],
                    "tests": tests, "cases": cases, "inventory_complete": complete, "inventory_issues": issues}
        operator["execution"] = config.get("execution", {})
        operator["inventory_note"] = config.get("inventory_note")
        if not entries:
            warnings.append(f"{operator_id}: no launch target resolved; inspect catalog evidence")
        if issues:
            warnings.extend(issues)
        operators.append(operator)
    order = list(CATEGORIES)
    operators.sort(key=lambda op: (order.index(op["category"]) if op["category"] in order else 999, op["operator_id"]))
    counts = {}
    for op in operators:
        counts[op["category"]] = counts.get(op["category"], 0) + 1
        op["category_index"] = counts[op["category"]]
    return {"schema_version": 1, "root": str(root), "testcases_dir": str(testcases_dir), "operator_count": len(operators),
            "known_case_count": sum(len(op["cases"]) for op in operators),
            "inventory_complete": all(op["inventory_complete"] for op in operators),
            "categories": CATEGORIES, "operators": operators, "warnings": warnings}


if __name__ == "__main__":
    print(json.dumps(build_catalog(), ensure_ascii=False, indent=2))
