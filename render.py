"""Render the canonical snapshot without touching test source or probing hardware."""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

from .highlight import cpp_html, python_html

TEMPLATE = Path(__file__).with_name("report_template.html")
LABELS = {"passed": "PASS", "failed": "FAIL", "error": "ERROR", "skipped": "SKIP", "not_run": "未测试", "partial": "PARTIAL"}


def esc(value):
    if value is None or value == "":
        return "N/A"
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    return html.escape(str(value))


def fmt(value):
    return f"{value:.4f}" if isinstance(value, (int, float)) else "N/A"


def rate(value):
    return f"{value:.1%}" if value is not None else "N/A"


def anchor(operator_id):
    return "op-" + hashlib.sha256(operator_id.encode()).hexdigest()[:16]


def correctness(summary):
    return f"{rate(summary['pass_rate'])} ({summary['passed']}/{summary['correctness_cases']})" if summary["correctness_cases"] else "未测试"


def duration_range(summary):
    bounds = summary.get("task_duration_range_us")
    return f"{fmt(bounds['min'])} – {fmt(bounds['max'])}" if bounds else "N/A"


def kv_table(fields):
    labels = {"framework": "Framework", "date": "Date", "evaluation_scope": "Evaluation Scope",
        "benchmark": "Benchmark", "profiler": "Profiler", "run_id": "Run ID", "git_commit": "Git Commit",
        "correctness_target": "Correctness Target", "benchmark_target": "Benchmark Target",
        "environment_source": "Environment Source", "data_kind": "Data Kind", "captured_at": "Captured At",
        "hostname": "Hostname", "npu": "NPU", "cpu": "CPU", "cann": "CANN", "driver": "Driver",
        "pytorch": "PyTorch", "pytorch_npu": "PyTorch NPU", "triton": "Triton",
        "opentile_converter": "OpenTile Converter", "opentile_as": "OpenTile AS", "otrt_jit": "OTRT JIT",
        "python": "Python", "os": "OS", "container": "Container"}
    return "<table class='kv'><tbody>" + "".join(f"<tr><td class='kv-k'>{esc(labels.get(k, k))}</td><td>{esc(v)}</td></tr>" for k, v in fields.items()) + "</tbody></table>"


def correctness_status(summary):
    if not summary["correctness_cases"]:
        return "not_run"
    if summary["failed"]:
        return "failed"
    if summary["passed"] == summary["correctness_cases"]:
        return "passed"
    return "partial" if summary["passed"] else "skipped"


GROUP_COLORS = [
    ("#315e88", "#eef3f9"), ("#78619b", "#f3eff8"), ("#26776d", "#edf6f3"),
    ("#99672e", "#faf3e9"), ("#466b99", "#edf3fa"), ("#9b5567", "#f9eff2"),
    ("#777b35", "#f4f5e9"), ("#5a727e", "#eff4f6"), ("#8a626f", "#f6eff3"),
    ("#6e6a9c", "#f1f0f8"), ("#65736a", "#f0f4f1"),
]


def operator_code_view(op):
    """One code viewer per operator; identical text shares a single highlighted block."""
    dialog_id = anchor(op["operator_id"]) + "-code"
    kernels = {}
    for row in op["details"]:
        kinds = kernels.setdefault(row["kernel_name"], {"kernel_source": {}, "cceir": {}})
        for kind in kinds:
            artifact = row.get(kind)
            if not artifact:
                continue
            content = artifact["content"]
            variant = kinds[kind].setdefault(content, {"artifact": artifact, "inputs": set(), "example": row})
            variant["inputs"].add(row["case_id"])
            if artifact.get("origin") != "catalog source snapshot":
                variant["artifact"] = artifact
    sections = []
    for kernel_index, (name, kinds) in enumerate(kernels.items()):
        blocks = []
        for kind, title, language, highlighter in (
            ("kernel_source", "DSL", "Python", python_html), ("cceir", "CCE / CCEIR", "C / C++", cpp_html)
        ):
            variants = list(kinds[kind].values())
            group_id = f"{dialog_id}-{kernel_index}-{kind}"
            if not variants:
                blocks.append(f"<h5>{title} · {language}</h5><p class='muted'>未提供</p>")
                continue
            options, panes = [], []
            for index, variant in enumerate(variants):
                row, artifact = variant["example"], variant["artifact"]
                code_id = f"{group_id}-{index}"
                options.append(f"<option value='{index}'>版本 {index + 1} · {esc(row['shape'])} · {esc(row['dtype'])}</option>")
                origin = artifact.get("origin", "input artifact / 本轮产物")
                panes.append(f"<div class='code-variant-pane' data-variant-group='{group_id}' data-variant='{index}'{' hidden' if index else ''}>"
                    f"<p class='muted'>{esc(artifact.get('path'))} · {esc(origin)} · {len(variant['inputs'])} 个输入共用</p>"
                    "<div class='code-panel'><div class='code-toolbar'>"
                    f"<span>{title} · {language}</span><button type='button' class='copy-code' data-copyid='{code_id}' aria-label='复制 {title} 代码'>复制</button></div>"
                    f"<pre><code id='{code_id}' class='language-{'python' if kind == 'kernel_source' else 'cpp'}'>{highlighter(artifact['content'])}</code></pre></div></div>")
            selector = f"<label class='variant-label'>代码版本 <select class='code-variant' data-group='{group_id}'>{''.join(options)}</select></label>" if len(variants) > 1 else ""
            blocks.append(f"<div class='code-language-block'><h5>{title} · {language}</h5>{selector}{''.join(panes)}</div>")
        sections.append(f"<section class='kernel-code-group'><h4><code>{esc(name)}</code></h4>{''.join(blocks)}</section>")
    return (f"<dialog class='code-view' id='{dialog_id}'><header class='code-header'><strong>{esc(op['name'])} · DSL / CCE</strong>"
            "<button type='button' class='close-dialog' aria-label='关闭代码'>关闭 ×</button></header>"
            "<div class='code-body'><p class='note'>相同代码已合并；存在不同代码时可切换版本。</p>"
            + ("".join(sections) or "<p class='muted'>未提供 kernel 代码</p>") + "</div></dialog>")


def detail_filter_menu(dialog_id):
    options = "".join(f"<label><input type='checkbox' name='detail-accuracy' value='{status}' checked>{label}<span data-detail-count='{status}'></span></label>"
        for status, label in (("passed", "通过"), ("failed", "失败"), ("error", "错误"), ("skipped", "已跳过"), ("not_run", "未测试")))
    return (f"<div class='filter-menu detail-filter-menu' id='{dialog_id}-accuracy-filter' popover aria-label='明细精度筛选'>"
        "<form class='detail-filter-form'><h4>精度是否通过</h4>"
        "<div class='filter-shortcuts'><button type='button' data-detail-action='passed'>仅显示通过</button><button type='button' data-detail-action='clear'>清除筛选</button></div>"
        "<label class='filter-all'><input type='checkbox' data-detail-select-all checked>全选</label>" + options +
        "<div class='filter-actions'><button type='button' data-detail-action='cancel'>取消</button><button type='submit'>确定</button></div></form></div>")


def render_html(run):
    summary = run["summary"]
    setup = run["setup"]
    setup_blocks = "<div class='setup-block'><h4>Metadata / 元信息</h4>" + kv_table(setup["metadata"]) + "</div>"
    setup_blocks += "<div class='setup-block'><h4>Environment / 运行环境</h4>" + kv_table({k: v for k, v in setup["environment"].items() if k != "tilelang"}) + "</div>"
    setup_blocks += "<details class='host setup-block'><summary>Report Host / 报告生成环境</summary>" + kv_table({k: v for k, v in setup.get("report_host", {}).items() if k != "tilelang"}) + "</details>"
    groups, sections, code_views = {}, [], []
    for operator_index, op in enumerate(run["operators"], 1):
        target = anchor(op["operator_id"])
        category = op["category"]
        group = groups.setdefault(category, {"label": op["category_label"], "rows": []})
        status = correctness_status(op["summary"])
        score_class = "score-high" if status == "passed" else "score-low" if status == "failed" else "score-mid" if status == "partial" else ""
        group["rows"].append(f"<tr class='operator-row' data-correctness='{status}' data-row-number='{operator_index}'><td class='number'>{operator_index}</td>"
            f"<td><span class='category-tag'>{esc(op['category_label'])}</span></td><td class='col-name'><a class='case-link' href='#{target}' data-detailid='{target}' aria-haspopup='dialog' aria-controls='{target}'>{esc(op['name'])}</a></td>"
            f"<td class='score-cell {score_class}'>{correctness(op['summary'])}</td><td class='number'>{duration_range(op['summary'])}</td>"
            f"<td><button type='button' class='code-trigger' data-codeid='{target}-code'>DSL / CCE</button></td></tr>")
        code_views.append(operator_code_view(op))
        rows = []
        for row in op["details"]:
            status = row["accuracy"]
            score_class = "score-high" if status == "passed" else "score-low" if status in {"failed", "error"} else ""
            rows.append(f"<tr class='detail-row' data-accuracy='{status}'><td><code>{esc(row['kernel_name'])}</code></td><td>{esc(row['shape'])}</td><td>{esc(row['dtype'])}</td><td class='score-cell {score_class}'>{LABELS.get(status, esc(status))}</td><td class='number'>{fmt(row['latency_us'])}</td></tr>")
        accuracy_header = f"<button type='button' class='filter-trigger detail-filter-trigger' aria-label='筛选明细精度' aria-expanded='false' aria-controls='{target}-accuracy-filter'>精度是否通过<svg viewBox='0 0 16 16' aria-hidden='true'><path d='M1 2h14L10 8v5l-4 2V8z'/></svg><span class='filter-mark' hidden></span></button>"
        table = "<div class='table-wrap'><table class='detail-table'><caption>Per-input kernel results / 输入配置明细</caption><thead><tr><th>kernel_name</th><th>Shape</th><th>DType</th><th>" + accuracy_header + "</th><th>Latency (us)</th></tr></thead><tbody>" + "".join(rows) + f"<tr class='detail-empty'{' hidden' if rows else ''}><td colspan='5' class='empty'>没有符合筛选条件的明细</td></tr></tbody></table></div>"
        sections.append(f"<dialog class='operator-details-view code-view' id='{target}' aria-labelledby='{target}-title'>"
            f"<header class='code-header'><strong id='{target}-title'>{esc(op['name'])} · 算子明细</strong>"
            "<button type='button' class='close-dialog' aria-label='关闭算子明细' autofocus>关闭 ×</button></header>"
            f"<div class='code-body'><p class='detail-category'>{esc(op['category_label'])}</p>"
            f"<p class='note'>ID: {esc(op['operator_id'])} · {op['summary']['tested_cases']}/{op['summary']['total_cases']} inputs · 正确性 {correctness(op['summary'])}</p>"
            f"{table}<p class='note' data-detail-filter-status aria-live='polite'>筛选匹配 {len(rows)} / {len(rows)} 条明细</p></div>{detail_filter_menu(target)}</dialog>")
    analysis_groups, category_options = [], []
    for group_index, (category, group) in enumerate(groups.items()):
        color, background = GROUP_COLORS[group_index % len(GROUP_COLORS)]
        group_id = "category-" + hashlib.sha256(category.encode()).hexdigest()[:12]
        analysis_groups.append(f"<tbody class='analysis-group' id='{group_id}' data-category='{esc(category)}' style='--group-color:{color};--group-bg:{background}'>"
            f"<tr class='category-heading'><th colspan='6' scope='rowgroup'><button type='button' class='category-toggle' aria-expanded='true' aria-controls='{group_id}'>"
            f"<span class='group-caret' aria-hidden='true'>▾</span> {esc(group['label'])} <span class='category-count'>{len(group['rows'])} 个算子</span></button></th></tr>"
            + "".join(group["rows"]) + "</tbody>")
        category_options.append(f"<label><input type='checkbox' name='category' value='{esc(category)}' checked>"
            f"<span style='color:{color}'>{esc(group['label'])}</span><span data-category-count='{esc(category)}'>{len(group['rows'])}</span></label>")
    diagnostics = ""
    if run.get("warnings"):
        diagnostics += "<section class='section'><details class='diagnostics callout warning'><summary>Diagnostics / 诊断信息</summary><ul>" + "".join(f"<li>{esc(w)}</li>" for w in run["warnings"]) + "</ul></details></section>"
    if run.get("logs"):
        diagnostics += "<section class='section'><details class='diagnostics'><summary>Logs / 原始日志</summary>" + "".join(f"<details><summary>{esc(log['path'])}</summary><pre>{html.escape(log['content'])}</pre></details>" for log in run["logs"]) + "</details></section>"
    total = summary["total_cases"]
    values = {"TITLE": "Triton 算子评测报告", "STATUS": esc(run["status"].upper()),
        "STATUS_CLASS": esc(run["status"]), "SCOPE": esc(run["metadata"].get("scope", "testcases")),
        "PERFORMANCE_ROWS": str(summary["performance_rows"]), "PROFILER": esc(setup["metadata"].get("profiler")),
        "DATE": esc(run["metadata"].get("generated_at")),
        "ABSTRACT": f"覆盖 {summary['total_operators']} 个算子的源码输入清单；本轮已有 {summary['tested_operators']} 个算子、{summary['tested_cases']} 条输入结果，{summary['performance_rows']} 条 kernel 性能记录。性能使用设备 Task Duration 的采样中位数，范围为各输入与 kernel 中位数的最小值至最大值。",
        "DEMO": "<div class='section demo-section'><div class='callout warning'>DEMO / 模拟数据：仅用于验证报告框架，不代表真实硬件测量。</div></div>" if run["metadata"].get("demo") else "",
        "SETUP": setup_blocks, "PASS_RATE": rate(summary["pass_rate"]),
        "PASS_COUNT": f"{summary['passed_cases']} / {summary['correctness_cases']} cases",
        "OPERATORS": f"{summary['tested_operators']}/{summary['total_operators']}",
        "CASES": f"{summary['tested_cases']}/{total if total is not None else 'N/A'}",
        "FAILED": str(summary["failed_cases"]), "ANALYSIS": "".join(analysis_groups), "CODE_VIEWS": "".join(code_views),
        "CATEGORY_OPTIONS": "".join(category_options),
        "DETAIL_VIEWS": "".join(sections), "DIAGNOSTICS": diagnostics,
        "INTERACTIONS": Path(__file__).with_name("report_interactions.js").read_text(encoding="utf-8"),
        "INVENTORY_NOTE": "全量输入清单已展开；重复运行与多次 launch 不增加覆盖数。" if summary["inventory_complete"] else f"输入清单尚未完整解析，已知 {summary['known_cases']} 条；总分母暂记 N/A，详见诊断。"}
    template = TEMPLATE.read_text(encoding="utf-8")
    # Single-pass replacement prevents artifact text from becoming template instructions.
    import re
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: values.get(m[1], m[0]), template)


def _md(value):
    if value is None:
        return "N/A"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    return html.escape(str(value)).replace("|", "&#124;").replace("\n", "<br>")


def render_markdown(run):
    s = run["summary"]
    lines = ["# Triton 算子评测报告", "", f"Status: {run['status']}", ""]
    if run["metadata"].get("demo"):
        lines += ["> DEMO / 模拟数据，不代表真实硬件测量。", ""]
    lines += ["本报告按逻辑输入统计覆盖率，性能取设备 Task Duration 采样中位数。", "", "## 1. Experiment Setup / 评测配置", ""]
    for key, title in (("metadata", "Metadata / 元信息"), ("environment", "Environment / 运行环境"), ("report_host", "Report Host / 报告生成环境")):
        lines += [f"### {title}", "", "| Item | Value |", "|---|---|"]
        lines += [f"| {_md(k)} | {_md(v)} |" for k, v in run["setup"].get(key, {}).items() if k != "tilelang" or key == "metadata"]
        lines.append("")
    lines += ["## 2. Results Overview / 结果总览", "", "| Pass Rate | Tested / Total Operators | Tested / Total Cases | Failed Cases |", "|---:|---:|---:|---:|",
              f"| {rate(s['pass_rate'])} | {s['tested_operators']}/{s['total_operators']} | {s['tested_cases']}/{s['total_cases'] if s['total_cases'] is not None else 'N/A'} | {s['failed_cases']} |", "",
              "## 3. Operator Analysis / 算子分析", "", "| 序号 | 大类 | 算子名称 | 正确性 | Task Duration 范围 (μs) | 代码 |", "|---:|---|---|---|---:|---|"]
    for index, op in enumerate(run["operators"], 1):
        lines.append(f"| {index} | {_md(op['category_label'])} | [{_md(op['name'])}](#{anchor(op['operator_id'])}) | {correctness(op['summary'])} | {duration_range(op['summary'])} | [DSL / CCE](report.html#{anchor(op['operator_id'])}-code) |")
    lines += ["", "## 4. Operator Details / 算子明细", "", "源码与 CCEIR 在 HTML 的算子分析表中统一查看，支持代码版本选择与复制；完整快照保存在 run.json。", ""]
    for op in run["operators"]:
        lines += [f'<a id="{anchor(op["operator_id"])}"></a>', "", f"### {_md(op['name'])}", "", f"ID: `{op['operator_id']}`", "", "| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |", "|---|---|---|---|---:|"]
        for row in op["details"]:
            lines.append(f"| {_md(row['kernel_name'])} | {_md(row['shape'])} | {_md(row['dtype'])} | {LABELS.get(row['accuracy'], row['accuracy'])} | {fmt(row['latency_us'])} |")
        lines.append("")
    if run["warnings"]:
        lines += ["## Diagnostics / 诊断信息", "", *[f"- {_md(w)}" for w in run["warnings"]], ""]
    return "\n".join(lines)


def write_reports(run, output_dir):
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = {"json": root / "run.json", "markdown": root / "report.md", "html": root / "report.html"}
    paths["json"].write_text(json.dumps(run, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    paths["markdown"].write_text(render_markdown(run), encoding="utf-8")
    paths["html"].write_text(render_html(run), encoding="utf-8")
    return paths
