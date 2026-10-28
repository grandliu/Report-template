"""Read Python syntax without importing Torch, Triton, or executing test code."""
from __future__ import annotations

import ast
import itertools
import operator
from pathlib import Path


class Unresolved(ValueError):
    pass


def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{dotted(node.value)}.{node.attr}".strip(".")
    if isinstance(node, ast.Call):
        return dotted(node.func)
    return ""


def bind(target, value, env):
    if isinstance(target, ast.Name):
        env[target.id] = value
    elif isinstance(target, (ast.Tuple, ast.List)):
        if len(target.elts) != len(value):
            raise Unresolved("assignment arity")
        for child, item in zip(target.elts, value):
            bind(child, item, env)


class StaticValues:
    """Small allowlisted interpreter for literal parameter definitions, never eval()."""

    def value(self, node, env):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in env:
                raise Unresolved(node.id)
            return env[node.id]
        if isinstance(node, ast.Attribute):
            name = dotted(node)
            if name.startswith(("torch.", "tl.")):
                return name.split(".")[-1]
            raise Unresolved(name)
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return [self.value(x, env) for x in node.elts]
        if isinstance(node, ast.Dict):
            result = {}
            for key, val in zip(node.keys, node.values):
                if key is None:
                    result.update(self.value(val, env))
                else:
                    result[self.value(key, env)] = self.value(val, env)
            return result
        if isinstance(node, ast.Subscript):
            return self.value(node.value, env)[self.value(node.slice, env)]
        if isinstance(node, ast.Slice):
            return slice(*(self.value(v, env) if v else None for v in (node.lower, node.upper, node.step)))
        if isinstance(node, ast.UnaryOp):
            fn = {ast.USub: operator.neg, ast.UAdd: operator.pos, ast.Not: operator.not_}.get(type(node.op))
            if fn:
                return fn(self.value(node.operand, env))
        if isinstance(node, ast.BinOp):
            fn = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                  ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
                  ast.Pow: operator.pow, ast.Mod: operator.mod}.get(type(node.op))
            if fn:
                return fn(self.value(node.left, env), self.value(node.right, env))
        if isinstance(node, ast.Compare):
            left = self.value(node.left, env)
            for op, right_node in zip(node.ops, node.comparators):
                right = self.value(right_node, env)
                fn = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
                      ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
                      ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b}.get(type(op))
                if not fn or not fn(left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.BoolOp):
            vals = [self.value(x, env) for x in node.values]
            return all(vals) if isinstance(node.op, ast.And) else any(vals)
        if isinstance(node, ast.IfExp):
            return self.value(node.body if self.value(node.test, env) else node.orelse, env)
        if isinstance(node, (ast.ListComp, ast.GeneratorExp, ast.SetComp)):
            def expand(index, scope):
                if index == len(node.generators):
                    yield self.value(node.elt, scope)
                    return
                gen = node.generators[index]
                for item in self.value(gen.iter, scope):
                    local = dict(scope)
                    bind(gen.target, item, local)
                    if all(self.value(test, local) for test in gen.ifs):
                        yield from expand(index + 1, local)
            return list(expand(0, env))
        if isinstance(node, ast.JoinedStr):
            return "".join(str(self.value(x.value, env)) if isinstance(x, ast.FormattedValue)
                           else str(x.value) for x in node.values)
        if isinstance(node, ast.Call):
            name = dotted(node.func)
            # Environment-sensitive definitions are not silently evaluated on the report host.
            if name == "pytest.param":
                args = []
                for arg in node.args:
                    if isinstance(arg, ast.Starred):
                        args.extend(self.value(arg.value, env))
                    else:
                        args.append(self.value(arg, env))
                return {"__param__": args,
                        "id": next((self.value(k.value, env) for k in node.keywords if k.arg == "id"), None)}
            if name == "dict":
                result = dict(self.value(node.args[0], env)) if node.args else {}
                result.update({k.arg: self.value(k.value, env) for k in node.keywords if k.arg})
                return result
            if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
                fmt = self.value(node.func.value, env)
                if not isinstance(fmt, str):
                    raise Unresolved("non-string format")
                args = []
                for arg in node.args:
                    args.extend(self.value(arg.value, env)) if isinstance(arg, ast.Starred) else args.append(self.value(arg, env))
                return fmt.format(*args)
            if name in {"range", "list", "tuple", "dict", "len", "int", "float", "str", "bool", "min", "max", "sorted"}:
                funcs = {"range": range, "list": list, "tuple": list, "dict": dict, "len": len,
                         "int": int, "float": float, "str": str, "bool": bool,
                         "min": min, "max": max, "sorted": sorted}
                result = funcs[name](*(self.value(x, env) for x in node.args))
                return list(result) if isinstance(result, range) else result
            if name in {"product", "itertools.product"}:
                return list(itertools.product(*(self.value(x, env) for x in node.args)))
        raise Unresolved(ast.unparse(node))

    def globals(self, tree, initial=None):
        env = dict(initial or {})
        # Several passes support constants referring to later static definitions.
        for _ in range(3):
            for node in tree.body:
                if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
                    try:
                        val = self.value(node.value, env)
                        for target in node.targets if isinstance(node, ast.Assign) else [node.target]:
                            bind(target, val, env)
                    except (Unresolved, TypeError, ValueError, KeyError, IndexError, ZeroDivisionError):
                        pass
        return env


def read_module(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    return text, ast.parse(text, filename=str(path))


def display_name(kernel_name):
    name = "_".join(x for x in kernel_name.strip("_").split("_") if x not in {"fwd", "kernel"})
    # A generic function called fwd_kernel has no recoverable semantic name.
    return name or kernel_name.strip("_")


def scan_kernels(directory: Path, root: Path):
    """Identify host launch targets, ASTSource targets, and JIT-only helpers separately."""
    modules, candidates, evidence, assignments = [], {}, {}, {}
    for path in sorted(directory.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        text, tree = read_module(path)
        modules.append((path, text, tree))
        aliases = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for item in node.names:
                    aliases[item.asname or item.name] = item.name
            elif isinstance(node, ast.ImportFrom):
                for item in node.names:
                    aliases[item.asname or item.name] = f"{node.module or ''}.{item.name}"
        def resolve(name):
            head, _, tail = name.partition(".")
            return aliases.get(head, head) + ("." + tail if tail else "")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                decorators = [resolve(dotted(x)) for x in node.decorator_list]
                if any(x.endswith(".jit") or x == "jit" for x in decorators):
                    start = min([node.lineno, *(x.lineno for x in node.decorator_list)])
                    key = (str(path), node.name)
                    candidates[key] = {"kernel_name": node.name, "display_name": display_name(node.name),
                        "file": path.relative_to(root).as_posix(), "line": start, "end_line": node.end_lineno,
                        "source": "\n".join(text.splitlines()[start - 1:node.end_lineno]),
                        "decorators": decorators, "evidence": []}
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and isinstance(node.value, ast.Name):
                        assignments[target.id] = node.value.id
            if isinstance(node, ast.Call):
                target, kind = None, None
                if isinstance(node.func, ast.Subscript):
                    target, kind = dotted(node.func.value), "launch_subscript"
                elif resolve(dotted(node.func)).endswith("ASTSource"):
                    target = next((dotted(k.value) for k in node.keywords if k.arg == "fn"), None)
                    if not target and node.args:
                        target = dotted(node.args[0])
                    kind = "ASTSource"
                elif dotted(node.func).endswith(".run"):
                    target, kind = dotted(node.func.value), "launch_run"
                # Generic launch wrappers used by several operators.
                if not target:
                    for keyword in node.keywords:
                        if keyword.arg in {"kernel", "fn"} and isinstance(keyword.value, ast.Name):
                            target, kind = keyword.value.id, "kernel_argument"
                    if "launch" in dotted(node.func).lower() and node.args and isinstance(node.args[0], ast.Name):
                        target, kind = node.args[0].id, "launcher_argument"
                if target:
                    resolved = resolve(target).split(".")[-1]
                    resolved = assignments.get(resolved, resolved)
                    evidence.setdefault(resolved, []).append({"kind": kind, "file": path.relative_to(root).as_posix(), "line": node.lineno})
    for record in candidates.values():
        record["evidence"] = evidence.get(record["kernel_name"], [])
        record["role"] = "entry" if record["evidence"] else "jit_helper_or_unresolved"
    records = list(candidates.values())
    return records, modules
