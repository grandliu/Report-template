# Triton 算子评测报告

本目录包含独立的评测与报告模块。离线扫描、分析、渲染只依赖 Python 3.10+ 标准库；`run` 自动执行入口需要测试环境中的 pytest、Torch/Triton、NPU、CANN 及 msprof。全部新增代码、配置、输入示例及报告都在 `report/` 内，原测试源码不修改；只有 `run` 会在子进程中导入并执行测试。

## 快速使用

从 `OpentileTest_code_repo/` 根目录运行：

```bash
# 自动评测入口：只需指定算子总目录和输出目录
python -m report run --testcases ./testcases --output ./report/outputs/latest

# 可选：选择设备、实际测试 Python 和 profiler 路径
python -m report run --testcases ./testcases --output ./report/outputs/latest \
  --device 0 --python /path/to/python --msprof /path/to/msprof --warmup 1 --iterations 3

# 源码 AST 扫描：算子、kernel 名、识别依据、分类及展开后的逻辑用例
python -m report scan

# 无任何运行结果，生成全量算子清单与零覆盖报告
python -m report generate --output report/outputs/empty

# 生成明确标为 DEMO 的模拟 XML、JSON、日志、源码及 CCEIR 占位示例并导出报告
python -m report demo

# 真正的离线入口：从一个结果目录收集信息
python -m report generate --input report/examples/demo_input --output report/outputs/imported

# 只读取统一数据快照，不扫描源码、不采集环境、不运行测试
python -m report render report/outputs/demo/run.json --output report/outputs/rerendered

# 在实际测试机器上采集环境快照，再随结果目录一起带回来
python -m report env --output report/outputs/environment.json

# 本机就是测试机器时，显式允许以本机探测信息作为测试环境
python -m report generate --input report/examples/demo_input --local-test-environment

# 离线验证框架
python -m unittest discover -s report/tests -v
```

可选浏览器验证（需 Node.js 和本机 Chrome，不影响框架运行）：

```powershell
node report/tests/browser_check.cjs 'C:\Program Files\Google\Chrome\Application\chrome.exe' report/outputs/demo/report.html report/outputs/visual-qa
```

此检查使用独立的无头浏览器，验证算子跳转、代码与 CCEIR 弹窗、移动端页面溢出，并在 `report/outputs/visual-qa/` 保存截图。

Windows 如 `python` 不在 PATH，可使用本机现有解释器：

```powershell
& 'D:\app\anacode\python.exe' -m report demo
```

默认产物：`report/outputs/catalog.json`、`report/outputs/empty/{run.json,report.md,report.html}`、`report/outputs/demo/{run.json,report.md,report.html}`。HTML 完全离线，无 CDN、外部脚本或模板引擎依赖。`generate` 成功导出时退出码为 0；`run` 完整通过返回 0，失败、跳过、无数据或性能不完整返回 1；格式/路径等致命错误返回 2。

HTML 使用原 TileOPs `tileops/reporting/report_template.html` 的基础样式和版式：深色顶栏、居中标题、白纸页面、双栏配置、KPI 横栏与表格。内容按本项目的分类、覆盖数、task duration 和代码查看需求调整。

## 架构和边界

```text
testcases 源码 → source / catalog ─────────────────┐
                                                │
已有 XML / JSON / logs / CCEIR → collector ───────┼→ analyzer → run.json → render → HTML / Markdown
                                                │
environment.json / 本机显式探测 → setup_info ──────┘

自动入口：run --testcases DIR → runner → 全量正确性 → 通过的 pytest item 做 msprof 采集
                                         └→ 自动生成上述结果目录 → collector → analyzer → render
```

- `source.py`：AST 识别 `@triton.jit`（包括导入别名）、`kernel[grid](...)`、`kernel.run(...)`、`ASTSource(fn=...)` 以及部分通用 launch 包装器的参数。区分实际入口与只有装饰器的辅助函数；每个 kernel 保留源码文件、行号、函数源码和调用证据。
- `catalog.py`：发现实际算子目录、加载人工复核的分类/特殊输入展开规则，构建稳定 `case_id`。
- `collector.py`：解析规范化结果目录。JUnit 提供测试结论；JSON 补足 shape、dtype 和逐 kernel 采样；日志完整保留用于追溯。
- `setup_info.py`：保存测试机环境与报告生成机环境，探测过程不导入 Torch、不初始化 NPU。
- `analyzer.py`：以 `operator_id + case_id + mode + kernel_name` 关联数据，计算去重覆盖数、正确性和性能范围。
- `render.py`：同一 `run` 数据生成三个格式。代码和日志 HTML 转义；运行快照内嵌源码及 CCEIR，后续无需原输入目录即可重新渲染。
- `highlight.py`：离线生成 Python / C/C++ 语法高亮，保留原始代码文本供复制。
- `report_interactions.js`：内嵌至最终 HTML，提供分类折叠、正确性表头筛选、代码版本切换与复制，不需要外部脚本或网络。
- `runner.py`：按算子启动隔离的 pytest 子进程，全部正确性结束后只对通过的 item 串行采集性能，管理超时、设备及产物。
- `pytest_plugin.py`：采集真实 pytest 身份和结果，包装标准 Triton `JITFunction.run` 与 `CompiledKernel[grid]` 启动接口，记录实际执行的 kernel、轮次、launch、输入归属以及可用 CCEIR。
- `execution.py`：静态用例与运行时 pytest 参数的匹配、补充。
- `profiler.py`：构造 msprof 命令，读取 `OpBasicInfo*.csv` / `op_summary*.csv` 并关联到实际 launch，转换为内部性能记录。

本次不接入仓库已有 `regression.py`，也不修改其并行调度、性能基线、自动更新或现有测试行为。现有 regression 结果需先转换为下面的输入协议，不能把其 `summary.json/perf.json` 直接冒充本框架输入。

## 自动执行的行为与产物

用户无需手动准备 XML、JSON、日志或环境快照。`--testcases` 接受任意名称的算子父目录，并支持 `extra_tests` 等嵌套容器。每个含 Python 文件的算子目录是一个统计单位；发现各文件顶层 `test*` 函数，使用 pytest 实际展开参数。测试类或自定义非 pytest 执行入口不在当前通用适配范围。

`run` 依次执行环境采集、所有算子的正确性阶段、通过用例的性能阶段、收集分析和报告导出。失败/错误/跳过的 pytest item 不进入性能阶段，其他通过 item 继续执行。一个 pytest 函数内循环多个 shape 时，通过可关联整个静态用例组；失败时保留未归属失败，不猜测失败 shape，整个包裹测试不进入性能阶段。性能运行时从调用栈的 shape/dtype/profile 等局部参数关联具体逻辑输入，无法唯一关联则保留诊断，不生成猜测性能。

使用当前已配置好的编译器和运行环境，不安装或替换工具链。若父目录包含本仓库格式的 `suite.json`，自动采用每个算子登记的第一种编译配置（例如 outline），保存于 `invocation.json`。`operator_catalog.json` 内的 `execution.env` 可提供显式覆盖。FA 适配会展开全部 shape 的 tile sweep，并只解除配置中精确列出的“仅在性能阶段启用” skipif，原有依赖检查和 xfail 保留。外部 FA 数据文件仍需在运行环境可用。

`--device` 是物理卡号，测试进程通过 `ASCEND_RT_VISIBLE_DEVICES` 仅看到该卡，使用逻辑设备 0。性能阶段串行；默认每个 pytest 函数先完整预热 1 次，再完整采样 3 次，调用该函数时复用本 item 的 fixtures，因此依赖单次消耗型 fixture、异步函数或自定义启动对象的测试需要专用适配。`--timeout` 默认每算子每阶段 1800 秒，超时终止对应进程树并继续其他算子。

默认通过 `msprof op --aic-metrics=BasicInfo` 读取 Task Duration，显式设置所有目标 kernel 和 `--launch-count=5000`，而不是只采第一项；预热同样占用该采集上限。另可用 `--profiler system` 选择系统级 msprof 和 `op_summary` 数据路径。命令及字段依据 [Ascend msOpProf 命令文档](https://github.com/Ascend/msopprof/blob/master/docs/en/user_guide/msopprof_user_guide.md) 与 [OpBasicInfo 字段说明](https://github.com/Ascend/msopprof/blob/master/docs/en/user_guide/msopprof_performance_data.md#opbasicinfo-basic-operator-information)。不同 CANN 版本的可用能力以实际安装为准；不支持的命令会记录错误，不会伪造采样。

有 Task Start Time 的 CSV 按同步 launch 窗口归属；无时间戳的 msOpProf CSV 只有在某 kernel 的实际 launch 数与 CSV 任务数严格一致时，才按自然排序后的采集顺序归属，包含并剔除预热轮次。数量不符、采集上限截断、未知符号、无法关联 shape 或丢失轮次均产生诊断。优先取原始函数名，生成符号的前缀匹配也必须唯一。

同一用例每轮中的同名 kernel 多次 launch 先相加，再对完整轮次取中位数；每个用例只列出实际观测到的 kernel，未执行的条件分支不要求有性能结果。全部目标 kernel 的每轮合计另外保存在 `operators[].device_totals`，表示已识别目标 kernel 的设备任务耗时合计，不包含未识别的框架操作，不等于算子端到端 latency。原始每次 launch 与匹配 CSV 行保存在 `matched_launches.json`。同步启动会改变原有调度并发关系，当前口径用于逐 kernel 设备耗时分析。

标准 Triton 编译对象提供 `asm.cceir/cce/cce_ir` 时自动保存并关联；否则报告显示未提供。未识别的自定义后端启动接口会使性能不完整，并保留原始日志，需扩展启动适配器。本机目前没有 NPU，已使用真正的 pytest 子进程和模拟 Triton/msprof 产物验证流程，尚未在实际 Ascend 环境验证全部算子。

```text
output/
├── report.html
├── report.md
├── run.json
└── raw/<本次唯一 run_id>/
    ├── run_info.json / environment.json
    ├── catalog.json / execution.json
    ├── case_results.json / performance.json
    └── tasks/<算子标识>/
        ├── accuracy/       配置、JUnit XML、逐 item 结果和日志
        └── performance/    同上，另含 msprof/、launches.jsonl、matched_launches.json、artifacts/
```

同一个输出目录再次运行会创建新的 raw 子目录，不混合历史采样；顶层报告更新为本轮结果。`python -m report render output/run.json` 可重新渲染，无需测试机和原始产物。下面的输入协议仍供离线导入/转换器使用，属于内部结果格式。

## 算子和输入清单

当前实际目录数为 **51**：49 个编号目录，以及 `extra_tests/fa`、`extra_tests/gmm`。`extra_tests` 是容器，不计作一个算子；`84tests_kernels/`、`84tests_origin/` 不在本次范围。

分类分为逐元素、规约、归一化、矩阵乘、注意力、卷积、采样、数据搬运与索引、扫描与递推、线性代数。分类配置在 `operator_catalog.json`，新目录会自动发现，未配置分类时放入 Other。

**kernel 名由源码发现，不从目录名生成。** 显示名去掉独立的 `fwd` 和 `kernel` 标记，保留 `bwd`、`w` 等有语义的部分，例如：

```text
_gelu_fwd_kernel          → gelu
_softcap_bwd_kernel       → softcap_bwd
fused_matmul_bwd_w_kernel → fused_matmul_bwd_w
```

同目录多个 kernel 会在第三部分的同一算子行列出多个显示名，第四部分分 kernel 展示；目录 ID 始终保留，因此同名函数、相同显示名不会合并目录。若函数本身只有泛称 `fwd_kernel`，无法从函数名恢复语义，保留原名。动态反射启动或无法静态追踪的 kernel 可配置 `entry_kernels` 和 `kernel_note`，识别证据会标为 `reviewed_override`，不会伪装为自动识别。

逻辑输入按测试函数 + shape/dtype/必要参数区分，不同 tile 参数也是不同输入。pytest 参数化、可静态展开的 shape/dtype 驱动循环由脚本展开；间接驱动（例如卷积 profiles）使用配置中明确的源码表达式。固定诊断用例以实际 pytest 入口为准，而不是把 `main()` 支持的全部可选参数当作默认运行输入。

当前展开 473 条源码记录，完全相同的测试函数和参数去重后为 **455 条逻辑输入**；原始重复次数保存在 `source_occurrences`。FA 的全量清单包含 6 个基本精度输入和两个方向各 6×9 个可选 tile 配置，共 114 条，运行其中一部分时只增加对应覆盖数。契约/校验测试也作为独立测试场景保留，可能没有张量 shape。

无法静态确定的参数不会执行源码推断，会写入 `inventory_issues`。这时报告保留已知清单，但总用例分母显示 `N/A`，而不会使用错误的数字。某些运行时随机长度、张量 shape 或 dtype 无法从源码确定，明细先显示 `N/A`；输入 JSON 可提供真实 `shape` / `dtype` 覆盖显示。

`case_id` 来源于算子 ID、测试函数和参数的稳定 SHA256 摘要。先运行 `scan`，执行器/日志转换器使用生成的清单 ID，避免依赖 pytest 自动生成的字符串标签。

## 输入目录协议 v1

```text
input_run/
├── run_info.json           可选：run_id、generated_at、scope、profiler、git_commit、demo
├── environment.json        可选：真实测试机环境快照
├── correctness.xml         可选：pytest JUnit XML
├── case_results.json       可选：逐逻辑输入正确性结果
├── performance.json        可选：逐输入 × kernel × mode 的设备时间采样
├── logs/*.log              可选，递归收集
└── artifacts/...           可选：kernel.py / kernel.cceir
```

没有结果文件时可以生成零覆盖报告。非法 JSON/XML、缺失的代码文件、无法关联的 kernel/输入会进入诊断；没有正确性结果不会被当作通过，没有性能不会填 0。

`case_results.json`：

```json
{
  "schema_version": 1,
  "records": [
    {
      "operator_id": "17_test_gelu",
      "case_id": "请使用 catalog.json 中的实际 case_id",
      "mode": "normal",
      "status": "passed",
      "shape": [128, 128],
      "dtype": "bfloat16",
      "message": null
    }
  ]
}
```

`status` 取 `passed / failed / error / skipped / not_run`。省略 `kernel_name` 表示所属输入的整体正确性；提供 `kernel_name` 可分别记录内部 kernel 的结果。相同输入与模式的结构化结果优先于 JUnit；不同 kernel 的失败不会被另一个 kernel 的通过覆盖。

JUnit 可通过 `properties` 提供 `operator_id`、`case_id`、`mode`、`kernel_name`、`nodeid`。缺少这些字段时仅在测试路径、函数和参数标签可唯一确定时映射。未参数化的包裹测试全部通过时可以关联其静态展开的所有输入，标注 `accuracy_scope=enclosing_test`；包裹测试失败时不能把所有 shape 全判失败，也不能假装知道失败的具体输入，保留未归属失败并请求逐输入结果。

`performance.json`：

```json
{
  "schema_version": 1,
  "records": [
    {
      "operator_id": "17_test_gelu",
      "case_id": "请使用 catalog.json 中的实际 case_id",
      "mode": "normal",
      "kernel_name": "_gelu_fwd_kernel",
      "task_duration_us": [3.4, 3.5, 3.7],
      "unit": "us",
      "kernel_source": "artifacts/gelu/kernel.py",
      "cceir": "artifacts/gelu/kernel.cceir"
    }
  ]
}
```

时间必须是正且有限的设备侧 `Task Duration(us)`，不是 pytest wall time。kernel 必须匹配该算子已识别的入口。同一输入、mode、kernel 的多条采样合并后取中位数。源码和 CCEIR 路径相对于输入目录；每个 shape/配置分别指定，不能按 kernel 名随意挑一个 CCEIR。缺少 kernel 产物时回退到 catalog 的源码快照并标明来源；CCEIR 从不生成或猜测，缺失显示“未提供”。DEMO 文件内的 CCEIR 仅是带标识的占位文本。

`environment.json` 直接使用 `python -m report env` 的输出，字段包括 `npu/cpu/cann/driver/pytorch/pytorch_npu/triton/opentile_converter/opentile_as/otrt_jit/python/os/container`。不再采集或展示 TileLang；旧快照重新渲染也会隐藏该配置项。输入快照优先，缺少的字段不从报告生成机补填。仅在指定 `--local-test-environment` 且没有输入环境快照时，使用本机探测结果。报告生成机信息独立保存在 `setup.report_host`。元信息与环境面板外框等高，各自按内容自然排列，不为凑行数添加占位字段。

## 统计及报告规则

- 算子数：本轮有结果的实际目录数 / 全量目录数。
- 总用例：本轮有正确性或性能结果的去重逻辑输入数 / 全量逻辑输入数；SKIP 表示已尝试并有结果，计入分子。`not_run` 不计入。
- 正确性通过率：通过逻辑输入数 / 有正确性结论的逻辑输入数，分母包含 SKIP；没有正确性结果显示 `N/A`。
- 同一输入的 normal/outline 等模式不重复增加覆盖数；任一模式失败则该输入按失败统计。每个模式的明细分别保留。
- HTML 和 Markdown 不展示执行模式列，代码版本选择中也不显示 mode；底层输入协议与 run.json 保留该字段以区分原始记录。
- 失败用例：failed + error 的逻辑输入，另加无法归属到具体输入的 JUnit 失败/集合错误；未归属部分单独记录在 `unassigned_failures`，不伪造 shape 归属。
- 第三部分 Task Duration 范围：第四部分各输入 × kernel × mode 的采样中位数的最小值至最大值，不是跨 shape 平均值。
- 算子分析列为全局行号、大类、算子名、正确性、Task Duration 范围、DSL / CCE。序号在筛选和折叠时保留原值；目录 ID 只在算子详情中显示。
- 分类使用不同颜色标识，默认全部展开，点击分类行折叠或展开；正确性全部通过的算子标绿，存在失败标红，部分通过标为黄色。
- 正确性表头的漏斗按钮提供类似 Excel 的复选筛选，可一键“仅显示通过”，也可选择失败、部分通过、跳过和未测试。筛选仅影响分析表视图，汇总统计保持原始数据。
- 大列表头同样支持复选筛选、全选与清除，可单选或组合多个大类；与正确性筛选取交集，筛选项计数反映另一列的当前筛选条件，分类折叠状态和全局行号保留。
- DSL 与 CCE 代码按算子统一展示，同一 kernel 的相同代码去重，确有代码差异时保留版本选择。DSL 使用 Python 高亮，CCE/CCEIR 使用 C/C++ 高亮；每个代码块右上角有复制按钮。复制保留原始文本与空白，不包含高亮标签；本地文件打开时有兼容复制方式。
- 明细按 kernel_name、shape、dtype、精度、latency 排列，不再逐 shape 重复放置代码入口。完整参数、case ID、原始采样仍保存在 run.json。
- 点击算子名称直接弹出对应的输入明细表，包含目录 ID、kernel_name、shape、dtype、精度与 latency；不再在 HTML 页面下方重复列出所有算子的明细。支持关闭按钮、Esc 和点击空白遮罩关闭，保留分析表的滚动位置与筛选状态。明细表较长时在弹窗内滚动，小屏幕可横向查看表格；URL 中的算子锚点仍可直接打开对应明细。Markdown 保留完整明细表。
- 明细弹窗的“精度是否通过”表头支持通过、失败、错误、跳过、未测试的多选筛选、全选、仅显示通过和清除。每个算子的明细筛选独立保存，不影响分析表筛选或其他算子。
- 运行状态：有正确性失败为 `failed`；没有测量为 `not_run`；本轮输入的正确性通过且对应所有已列明 kernel 均有性能结果才为 `passed`，其余为 `partial`。全量未覆盖输入本身不使“本轮”失败。
- 离线导入了未通过精度门禁的性能时保留可追溯数据，但写入诊断并禁止标为成功。未来真实 runner 从执行阶段阻止此情况。

`run.json` 是统一快照：`metadata/setup/summary/operators/details/logs/warnings/policy`。重新渲染不读取 testcases 或原始 CCEIR，也不会探测环境。
