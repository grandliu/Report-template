# Triton 算子评测报告

Status: not_run

本报告按逻辑输入统计覆盖率，性能取设备 Task Duration 采样中位数。

## 1. Experiment Setup / 评测配置

### Metadata / 元信息

| Item | Value |
|---|---|
| framework | OpenTile Reporting 0.1.0 |
| date | 2026-10-27T20:10:02.094638+08:00 |
| evaluation_scope | testcases |
| benchmark | OpenTile kernel input suite |
| profiler | msprof |
| run_id | N/A |
| git_commit | N/A |
| correctness_target | testcases/ |
| benchmark_target | offline performance.json |
| environment_source | not provided |
| data_kind | offline imported / 离线导入 |

### Environment / 运行环境

| Item | Value |
|---|---|
| captured_at | N/A |
| hostname | N/A |
| npu | N/A |
| cpu | N/A |
| cann | N/A |
| driver | N/A |
| pytorch | N/A |
| pytorch_npu | N/A |
| triton | N/A |
| opentile_converter | N/A |
| otrt_jit | N/A |
| opentile_as | N/A |
| python | N/A |
| os | N/A |
| container | N/A |

### Report Host / 报告生成环境

| Item | Value |
|---|---|
| captured_at | 2026-10-27T20:10:02.094638+08:00 |
| hostname | lhw |
| npu | N/A |
| cpu | AMD64 |
| cann | N/A |
| driver | N/A |
| pytorch | 2.8.0 |
| pytorch_npu | N/A |
| triton | N/A |
| opentile_converter | N/A |
| otrt_jit | N/A |
| opentile_as | N/A |
| python | 3.11.7 |
| os | Windows-10-10.0.26200-SP0 |
| container | N/A |

## 2. Results Overview / 结果总览

| Pass Rate | Tested / Total Operators | Tested / Total Cases | Failed Cases |
|---:|---:|---:|---:|
| N/A | 0/51 | 0/455 | 0 |

## 3. Operator Analysis / 算子分析

| 序号 | 大类 | 算子名称 | 正确性 | Task Duration 范围 (μs) | 代码 |
|---:|---|---|---|---:|---|
| 1 | Elementwise / 逐元素 | [silu / silu_bwd](#op-e0845c388ba1bb9c) | 未测试 | N/A | [DSL / CCE](report.html#op-e0845c388ba1bb9c-code) |
| 2 | Elementwise / 逐元素 | [rope](#op-c87ec5a742311641) | 未测试 | N/A | [DSL / CCE](report.html#op-c87ec5a742311641-code) |
| 3 | Elementwise / 逐元素 | [gelu](#op-796eb1e2b7089a66) | 未测试 | N/A | [DSL / CCE](report.html#op-796eb1e2b7089a66-code) |
| 4 | Elementwise / 逐元素 | [silu](#op-6631871b4414c0b0) | 未测试 | N/A | [DSL / CCE](report.html#op-6631871b4414c0b0-code) |
| 5 | Elementwise / 逐元素 | [swiglu](#op-35a0b7c1c0c10ba9) | 未测试 | N/A | [DSL / CCE](report.html#op-35a0b7c1c0c10ba9-code) |
| 6 | Elementwise / 逐元素 | [softcap](#op-f189c9151aa4b47b) | 未测试 | N/A | [DSL / CCE](report.html#op-f189c9151aa4b47b-code) |
| 7 | Elementwise / 逐元素 | [softcap / softcap_bwd](#op-01941b93dcb50fcc) | 未测试 | N/A | [DSL / CCE](report.html#op-01941b93dcb50fcc-code) |
| 8 | Elementwise / 逐元素 | [rope](#op-379968826b5ed4ed) | 未测试 | N/A | [DSL / CCE](report.html#op-379968826b5ed4ed-code) |
| 9 | Reduction / 规约 | [cross_entropy_prime](#op-57c83e0e486d9616) | 未测试 | N/A | [DSL / CCE](report.html#op-57c83e0e486d9616-code) |
| 10 | Reduction / 规约 | [fused_matmul_bwd_b](#op-dbbed760adbb67e9) | 未测试 | N/A | [DSL / CCE](report.html#op-dbbed760adbb67e9-code) |
| 11 | Normalization / 归一化 | [layer_norm_gated / layer_norm_gated_bwd / reduce_norm_parameter_grads](#op-d88cfef14827f7d4) | 未测试 | N/A | [DSL / CCE](report.html#op-d88cfef14827f7d4-code) |
| 12 | Normalization / 归一化 | [fused_add_rmsnorm](#op-553ca41a6e878646) | 未测试 | N/A | [DSL / CCE](report.html#op-553ca41a6e878646-code) |
| 13 | Normalization / 归一化 | [fused_add_layernorm](#op-3d8bd24818527086) | 未测试 | N/A | [DSL / CCE](report.html#op-3d8bd24818527086-code) |
| 14 | Normalization / 归一化 | [layer_norm_gated_bwd](#op-8569551f47f25978) | 未测试 | N/A | [DSL / CCE](report.html#op-8569551f47f25978-code) |
| 15 | Normalization / 归一化 | [rmsnorm / rmsnorm_bwd](#op-469e0212f3fb7d34) | 未测试 | N/A | [DSL / CCE](report.html#op-469e0212f3fb7d34-code) |
| 16 | Normalization / 归一化 | [rmsnorm](#op-143412770d150eab) | 未测试 | N/A | [DSL / CCE](report.html#op-143412770d150eab-code) |
| 17 | Normalization / 归一化 | [layernorm](#op-510399c54ed20ddf) | 未测试 | N/A | [DSL / CCE](report.html#op-510399c54ed20ddf-code) |
| 18 | Matmul / 矩阵乘 | [fused_matmul_bwd_w](#op-7b185467d67ae095) | 未测试 | N/A | [DSL / CCE](report.html#op-7b185467d67ae095-code) |
| 19 | Matmul / 矩阵乘 | [fused_matmul_bwd_x](#op-2e8269a6d5fd3fb8) | 未测试 | N/A | [DSL / CCE](report.html#op-2e8269a6d5fd3fb8-code) |
| 20 | Matmul / 矩阵乘 | [group_gemm_split_m](#op-70bb0849c2843cce) | 未测试 | N/A | [DSL / CCE](report.html#op-70bb0849c2843cce-code) |
| 21 | Attention / 注意力 | [da_u](#op-8282f271c3c2b6f0) | 未测试 | N/A | [DSL / CCE](report.html#op-8282f271c3c2b6f0-code) |
| 22 | Attention / 注意力 | [chunk_o](#op-149e9e4445c8057f) | 未测试 | N/A | [DSL / CCE](report.html#op-149e9e4445c8057f-code) |
| 23 | Attention / 注意力 | [chunk_bwd_dv_local](#op-73287c5b442b70fe) | 未测试 | N/A | [DSL / CCE](report.html#op-73287c5b442b70fe-code) |
| 24 | Attention / 注意力 | [paged_decode](#op-adcd528cb7b14783) | 未测试 | N/A | [DSL / CCE](report.html#op-adcd528cb7b14783-code) |
| 25 | Attention / 注意力 | [chunk_bwd_dqkwg](#op-4a3da92d4e37c872) | 未测试 | N/A | [DSL / CCE](report.html#op-4a3da92d4e37c872-code) |
| 26 | Attention / 注意力 | [attn_fp8](#op-f017e91d04c22f6a) | 未测试 | N/A | [DSL / CCE](report.html#op-f017e91d04c22f6a-code) |
| 27 | Attention / 注意力 | [chunk_scaled_dot_kkt](#op-9d376fa332e302b1) | 未测试 | N/A | [DSL / CCE](report.html#op-9d376fa332e302b1-code) |
| 28 | Attention / 注意力 | [chunk_scaled_dot_kkt](#op-11e76c12903fbfbc) | 未测试 | N/A | [DSL / CCE](report.html#op-11e76c12903fbfbc-code) |
| 29 | Attention / 注意力 | [sdpa](#op-2ed16ae986cc3e9a) | 未测试 | N/A | [DSL / CCE](report.html#op-2ed16ae986cc3e9a-code) |
| 30 | Attention / 注意力 | [fwd_kernel / bwd_preprocess / bwd_preprocess_ifmn / bwd_qkv](#op-2e1e8e2962571dd9) | 未测试 | N/A | [DSL / CCE](report.html#op-2e1e8e2962571dd9-code) |
| 31 | Convolution / 卷积 | [causal_conv1d](#op-acf8ffa6e2ea2881) | 未测试 | N/A | [DSL / CCE](report.html#op-acf8ffa6e2ea2881-code) |
| 32 | Convolution / 卷积 | [causal_conv1d_update_bdt](#op-67494a963fde9a13) | 未测试 | N/A | [DSL / CCE](report.html#op-67494a963fde9a13-code) |
| 33 | Convolution / 卷积 | [causal_conv1d_bwd](#op-e6997bfc2ab75bea) | 未测试 | N/A | [DSL / CCE](report.html#op-e6997bfc2ab75bea-code) |
| 34 | Sampling / 采样 | [top_p_filter](#op-4c090f6b73961379) | 未测试 | N/A | [DSL / CCE](report.html#op-4c090f6b73961379-code) |
| 35 | Sampling / 采样 | [reject_sampler](#op-99c6c06763d5d346) | 未测试 | N/A | [DSL / CCE](report.html#op-99c6c06763d5d346-code) |
| 36 | Sampling / 采样 | [join_prob_reject_sampler](#op-9c2e179f2cace378) | 未测试 | N/A | [DSL / CCE](report.html#op-9c2e179f2cace378-code) |
| 37 | Sampling / 采样 | [fused_penalty_temp](#op-719c96c6175f95f1) | 未测试 | N/A | [DSL / CCE](report.html#op-719c96c6175f95f1-code) |
| 38 | Sampling / 采样 | [top_p_sample](#op-d63556d709ea2433) | 未测试 | N/A | [DSL / CCE](report.html#op-d63556d709ea2433-code) |
| 39 | Data Movement / 数据搬运与索引 | [binned_copy](#op-aa347c79592808a5) | 未测试 | N/A | [DSL / CCE](report.html#op-aa347c79592808a5-code) |
| 40 | Data Movement / 数据搬运与索引 | [binned_copy / binned_copy_wgrad](#op-5579bf8df5a9197d) | 未测试 | N/A | [DSL / CCE](report.html#op-5579bf8df5a9197d-code) |
| 41 | Data Movement / 数据搬运与索引 | [store_label_cache](#op-8a9523e315aa1358) | 未测试 | N/A | [DSL / CCE](report.html#op-8a9523e315aa1358-code) |
| 42 | Data Movement / 数据搬运与索引 | [padded_copy_gather](#op-09c247256b3ff7b2) | 未测试 | N/A | [DSL / CCE](report.html#op-09c247256b3ff7b2-code) |
| 43 | Data Movement / 数据搬运与索引 | [padded_copy_wgrad](#op-aff9c16cc019d776) | 未测试 | N/A | [DSL / CCE](report.html#op-aff9c16cc019d776-code) |
| 44 | Data Movement / 数据搬运与索引 | [store_paged_kv_cache](#op-30c3770bd8fec0e0) | 未测试 | N/A | [DSL / CCE](report.html#op-30c3770bd8fec0e0-code) |
| 45 | Scan &amp; Recurrence / 扫描与递推 | [chunk_gated_delta_rule_bwd_dhu_blockdim64_npu](#op-8f39336c093a5606) | 未测试 | N/A | [DSL / CCE](report.html#op-8f39336c093a5606-code) |
| 46 | Scan &amp; Recurrence / 扫描与递推 | [fused_sigmoid_gating_delta_rule_update](#op-6b4ee8aebcc7b77d) | 未测试 | N/A | [DSL / CCE](report.html#op-6b4ee8aebcc7b77d-code) |
| 47 | Scan &amp; Recurrence / 扫描与递推 | [prepare_wy_repr_bwd_k_npu / prepare_wy_repr_bwd_v_npu / prepare_wy_repr_bwd_da_mask_npu / prepare_wy_repr_bwd_da_dot1_npu / prepare_wy_repr_bwd_da_dot2_npu / prepare_wy_repr_bwd_da_gate_npu / prepare_wy_repr_bwd_finalize_k_npu / prepare_wy_repr_bwd_finalize_a2_npu / prepare_wy_repr_bwd_finalize_dg_npu](#op-9548adbae98a71ec) | 未测试 | N/A | [DSL / CCE](report.html#op-9548adbae98a71ec-code) |
| 48 | Scan &amp; Recurrence / 扫描与递推 | [chunk_gated_delta_rule_h_k128_blockdim128](#op-363e314b22a07110) | 未测试 | N/A | [DSL / CCE](report.html#op-363e314b22a07110-code) |
| 49 | Scan &amp; Recurrence / 扫描与递推 | [chunk_local_cumsum_scalar / chunk_local_cumsum_vector](#op-d6f80eee2108109c) | 未测试 | N/A | [DSL / CCE](report.html#op-d6f80eee2108109c-code) |
| 50 | Scan &amp; Recurrence / 扫描与递推 | [recompute_w_u](#op-c9044689e684eaf1) | 未测试 | N/A | [DSL / CCE](report.html#op-c9044689e684eaf1-code) |
| 51 | Linear Algebra / 线性代数 | [solve_tril_16x16](#op-7fba9421c7fe0216) | 未测试 | N/A | [DSL / CCE](report.html#op-7fba9421c7fe0216-code) |

## 4. Operator Details / 算子明细

源码与 CCEIR 在 HTML 的算子分析表中统一查看，支持代码版本选择与复制；完整快照保存在 run.json。

<a id="op-e0845c388ba1bb9c"></a>

### silu / silu_bwd

ID: `03__silu_forward_backward_diff`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _silu_fwd_kernel | [128, 128] | float32 | 未测试 | N/A |
| _silu_bwd_kernel | [128, 128] | float32 | 未测试 | N/A |
| _silu_fwd_kernel | [999, 9999] | float32 | 未测试 | N/A |
| _silu_bwd_kernel | [999, 9999] | float32 | 未测试 | N/A |
| _silu_fwd_kernel | [1024, 10240] | float32 | 未测试 | N/A |
| _silu_bwd_kernel | [1024, 10240] | float32 | 未测试 | N/A |
| _silu_fwd_kernel | [128, 128] | float16 | 未测试 | N/A |
| _silu_bwd_kernel | [128, 128] | float16 | 未测试 | N/A |
| _silu_fwd_kernel | [999, 9999] | float16 | 未测试 | N/A |
| _silu_bwd_kernel | [999, 9999] | float16 | 未测试 | N/A |
| _silu_fwd_kernel | [1024, 10240] | float16 | 未测试 | N/A |
| _silu_bwd_kernel | [1024, 10240] | float16 | 未测试 | N/A |
| _silu_fwd_kernel | [128, 128] | bfloat16 | 未测试 | N/A |
| _silu_bwd_kernel | [128, 128] | bfloat16 | 未测试 | N/A |
| _silu_fwd_kernel | [999, 9999] | bfloat16 | 未测试 | N/A |
| _silu_bwd_kernel | [999, 9999] | bfloat16 | 未测试 | N/A |
| _silu_fwd_kernel | [1024, 10240] | bfloat16 | 未测试 | N/A |
| _silu_bwd_kernel | [1024, 10240] | bfloat16 | 未测试 | N/A |

<a id="op-c87ec5a742311641"></a>

### rope

ID: `14_rope_kernel`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| rope_kernel | N/A | N/A | 未测试 | N/A |

<a id="op-796eb1e2b7089a66"></a>

### gelu

ID: `17_test_gelu`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _gelu_fwd_kernel | [128, 128] | bfloat16 | 未测试 | N/A |

<a id="op-6631871b4414c0b0"></a>

### silu

ID: `18_test_silu`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _silu_fwd_kernel | [128, 128] | bfloat16 | 未测试 | N/A |

<a id="op-35a0b7c1c0c10ba9"></a>

### swiglu

ID: `19_test_swiglu`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _swiglu_fwd_kernel | [256, 128] | bfloat16 | 未测试 | N/A |

<a id="op-f189c9151aa4b47b"></a>

### softcap

ID: `21_softcap_fwd_kernel`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| softcap_fwd_kernel | [1024, 1024] | N/A | 未测试 | N/A |
| softcap_fwd_kernel | [1048613] | N/A | 未测试 | N/A |

<a id="op-01941b93dcb50fcc"></a>

### softcap / softcap_bwd

ID: `27_softcap_bwd_kernel`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _softcap_fwd_kernel | [128, 128] | float32 | 未测试 | N/A |
| _softcap_bwd_kernel | [128, 128] | float32 | 未测试 | N/A |
| _softcap_fwd_kernel | [999, 9999] | float32 | 未测试 | N/A |
| _softcap_bwd_kernel | [999, 9999] | float32 | 未测试 | N/A |
| _softcap_fwd_kernel | [1024, 10240] | float32 | 未测试 | N/A |
| _softcap_bwd_kernel | [1024, 10240] | float32 | 未测试 | N/A |
| _softcap_fwd_kernel | [128, 128] | float16 | 未测试 | N/A |
| _softcap_bwd_kernel | [128, 128] | float16 | 未测试 | N/A |
| _softcap_fwd_kernel | [999, 9999] | float16 | 未测试 | N/A |
| _softcap_bwd_kernel | [999, 9999] | float16 | 未测试 | N/A |
| _softcap_fwd_kernel | [1024, 10240] | float16 | 未测试 | N/A |
| _softcap_bwd_kernel | [1024, 10240] | float16 | 未测试 | N/A |
| _softcap_fwd_kernel | [128, 128] | bfloat16 | 未测试 | N/A |
| _softcap_bwd_kernel | [128, 128] | bfloat16 | 未测试 | N/A |
| _softcap_fwd_kernel | [999, 9999] | bfloat16 | 未测试 | N/A |
| _softcap_bwd_kernel | [999, 9999] | bfloat16 | 未测试 | N/A |
| _softcap_fwd_kernel | [1024, 10240] | bfloat16 | 未测试 | N/A |
| _softcap_bwd_kernel | [1024, 10240] | bfloat16 | 未测试 | N/A |

<a id="op-379968826b5ed4ed"></a>

### rope

ID: `48_test_pos_emb`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| rope_kernel | [1, 124, 8, 128] | float16 | 未测试 | N/A |
| rope_kernel | [1, 124, 2, 88] | float16 | 未测试 | N/A |
| rope_kernel | [1, 124, 8, 128] | bfloat16 | 未测试 | N/A |
| rope_kernel | [1, 124, 2, 88] | bfloat16 | 未测试 | N/A |

<a id="op-57c83e0e486d9616"></a>

### cross_entropy_prime

ID: `05__fused_ce_forward_backward_diff`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _cross_entropy_prime_kernel | [2048, 4096] | float32 | 未测试 | N/A |

<a id="op-dbbed760adbb67e9"></a>

### fused_matmul_bwd_b

ID: `37_fused_matmul_bwd_b_kernel`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| fused_matmul_bwd_b_kernel | [256, 1024] | float16 | 未测试 | N/A |

<a id="op-d88cfef14827f7d4"></a>

### layer_norm_gated / layer_norm_gated_bwd / reduce_norm_parameter_grads

ID: `32_layer_norm_gated_fwd`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| layer_norm_gated_fwd_kernel | N/A | float32 | 未测试 | N/A |
| layer_norm_gated_bwd_kernel | N/A | float32 | 未测试 | N/A |
| reduce_norm_parameter_grads_kernel | N/A | float32 | 未测试 | N/A |
| layer_norm_gated_fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| layer_norm_gated_bwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| reduce_norm_parameter_grads_kernel | N/A | bfloat16 | 未测试 | N/A |
| layer_norm_gated_fwd_kernel | N/A | float16 | 未测试 | N/A |
| layer_norm_gated_bwd_kernel | N/A | float16 | 未测试 | N/A |
| reduce_norm_parameter_grads_kernel | N/A | float16 | 未测试 | N/A |

<a id="op-553ca41a6e878646"></a>

### fused_add_rmsnorm

ID: `33_test_residual_add_rmsnorm`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _fused_add_rmsnorm_fwd_kernel | [32, 1024] | bfloat16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [64, 8192] | bfloat16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [2, 256] | bfloat16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [57, 7338] | bfloat16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [67, 7338] | bfloat16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [7762, 18778] | bfloat16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [32, 1024] | float32 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [64, 8192] | float32 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [2, 256] | float32 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [57, 7338] | float32 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [67, 7338] | float32 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [7762, 18778] | float32 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [32, 1024] | float16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [64, 8192] | float16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [2, 256] | float16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [57, 7338] | float16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [67, 7338] | float16 | 未测试 | N/A |
| _fused_add_rmsnorm_fwd_kernel | [7762, 18778] | float16 | 未测试 | N/A |

<a id="op-3d8bd24818527086"></a>

### fused_add_layernorm

ID: `34_test_residual_add_layernorm`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _fused_add_layernorm_fwd_kernel | [32, 1024] | bfloat16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [64, 8192] | bfloat16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [2, 256] | bfloat16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [57, 7338] | bfloat16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [67, 7338] | bfloat16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [7762, 18778] | bfloat16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [32, 1024] | float32 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [64, 8192] | float32 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [2, 256] | float32 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [57, 7338] | float32 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [67, 7338] | float32 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [7762, 18778] | float32 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [32, 1024] | float16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [64, 8192] | float16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [2, 256] | float16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [57, 7338] | float16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [67, 7338] | float16 | 未测试 | N/A |
| _fused_add_layernorm_fwd_kernel | [7762, 18778] | float16 | 未测试 | N/A |

<a id="op-8569551f47f25978"></a>

### layer_norm_gated_bwd

ID: `43_layer_norm_gated_bwd`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| layer_norm_gated_bwd_kernel | N/A | float32 | 未测试 | N/A |
| layer_norm_gated_bwd_kernel | N/A | float32 | 未测试 | N/A |

<a id="op-469e0212f3fb7d34"></a>

### rmsnorm / rmsnorm_bwd

ID: `45__rmsnorm_forward_backward_diff`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| rmsnorm_fwd_kernel | [32, 1024] | float32 | 未测试 | N/A |
| rmsnorm_bwd_kernel | [32, 1024] | float32 | 未测试 | N/A |
| rmsnorm_fwd_kernel | [77, 489] | float32 | 未测试 | N/A |
| rmsnorm_bwd_kernel | [77, 489] | float32 | 未测试 | N/A |
| rmsnorm_fwd_kernel | [32, 1024] | bfloat16 | 未测试 | N/A |
| rmsnorm_bwd_kernel | [32, 1024] | bfloat16 | 未测试 | N/A |
| rmsnorm_fwd_kernel | [77, 489] | bfloat16 | 未测试 | N/A |
| rmsnorm_bwd_kernel | [77, 489] | bfloat16 | 未测试 | N/A |

<a id="op-143412770d150eab"></a>

### rmsnorm

ID: `46_test_rmsnorm`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| rmsnorm_kernel | [2, 256] | float16 | 未测试 | N/A |
| rmsnorm_kernel | [57, 7338] | float16 | 未测试 | N/A |
| rmsnorm_kernel | [2, 256] | bfloat16 | 未测试 | N/A |
| rmsnorm_kernel | [57, 7338] | bfloat16 | 未测试 | N/A |

<a id="op-510399c54ed20ddf"></a>

### layernorm

ID: `47_test_layernorm`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| layernorm_kernel | [2, 256] | float16 | 未测试 | N/A |
| layernorm_kernel | [57, 7338] | float16 | 未测试 | N/A |
| layernorm_kernel | [2, 256] | bfloat16 | 未测试 | N/A |
| layernorm_kernel | [57, 7338] | bfloat16 | 未测试 | N/A |

<a id="op-7b185467d67ae095"></a>

### fused_matmul_bwd_w

ID: `22_fused_matmul_bwd_w_kernel`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| fused_matmul_bwd_w_kernel | [256, 512] | float16 | 未测试 | N/A |
| fused_matmul_bwd_w_kernel | [128, 128] | float16 | 未测试 | N/A |
| fused_matmul_bwd_w_kernel | [384, 1024] | float16 | 未测试 | N/A |

<a id="op-2e8269a6d5fd3fb8"></a>

### fused_matmul_bwd_x

ID: `38_fused_matmul_bwd_x_kernel`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| fused_matmul_bwd_x_kernel | [256, 512, 1024] | float16 | 未测试 | N/A |
| fused_matmul_bwd_x_kernel | [512, 1024, 2048] | float16 | 未测试 | N/A |
| fused_matmul_bwd_x_kernel | [256, 512, 1024] | bfloat16 | 未测试 | N/A |
| fused_matmul_bwd_x_kernel | [512, 1024, 2048] | bfloat16 | 未测试 | N/A |

<a id="op-70bb0849c2843cce"></a>

### group_gemm_split_m

ID: `extra_tests/gmm`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| group_gemm_split_m_kernel | {&quot;N&quot;: 768, &quot;K&quot;: 1024} | float16 | 未测试 | N/A |
| group_gemm_split_m_kernel | {&quot;N&quot;: 768, &quot;K&quot;: 1024} | float16 | 未测试 | N/A |
| group_gemm_split_m_kernel | {&quot;N&quot;: 768, &quot;K&quot;: 1024} | float16 | 未测试 | N/A |
| group_gemm_split_m_kernel | {&quot;N&quot;: 768, &quot;K&quot;: 1024} | float16 | 未测试 | N/A |
| group_gemm_split_m_kernel | {&quot;N&quot;: 768, &quot;K&quot;: 1024} | float16 | 未测试 | N/A |
| group_gemm_split_m_kernel | {&quot;N&quot;: 768, &quot;K&quot;: 1024} | float16 | 未测试 | N/A |

<a id="op-8282f271c3c2b6f0"></a>

### da_u

ID: `07_diffusion_attention`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| kernel_da_fwd_u | N/A | N/A | 未测试 | N/A |
| kernel_da_fwd_u | N/A | N/A | 未测试 | N/A |

<a id="op-149e9e4445c8057f"></a>

### chunk_o

ID: `08_chunk_fwd_o`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| chunk_fwd_kernel_o | {&quot;T&quot;: 128} | N/A | 未测试 | N/A |
| chunk_fwd_kernel_o | {&quot;T&quot;: 65} | N/A | 未测试 | N/A |

<a id="op-73287c5b442b70fe"></a>

### chunk_bwd_dv_local

ID: `09_chunk_bwd_dv_local`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| chunk_bwd_kernel_dv_local | [1, 128, 2, 128] | bfloat16 | 未测试 | N/A |
| chunk_bwd_kernel_dv_local | [1, 65, 2, 88] | bfloat16 | 未测试 | N/A |

<a id="op-adcd528cb7b14783"></a>

### paged_decode

ID: `20_test_paged_decode_gqa`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| paged_decode_kernel | N/A | N/A | 未测试 | N/A |

<a id="op-4a3da92d4e37c872"></a>

### chunk_bwd_dqkwg

ID: `26_chunk_bwd_dqkwg`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| chunk_bwd_kernel_dqkwg | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2, &quot;K&quot;: 64, &quot;V&quot;: 64} | bfloat16 | 未测试 | N/A |

<a id="op-f017e91d04c22f6a"></a>

### attn_fp8

ID: `39_FA_FP8`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _attn_fwd_fp8 | [128, 8, 1024, 64] | float8_e4m3fn | 未测试 | N/A |

<a id="op-9d376fa332e302b1"></a>

### chunk_scaled_dot_kkt

ID: `41_chunk_scaled_dot_kkt_fwd_no_gate`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| chunk_scaled_dot_kkt_fwd_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 31, &quot;H&quot;: 1, &quot;HV&quot;: 1} | bfloat16 | 未测试 | N/A |
| chunk_scaled_dot_kkt_fwd_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 32, &quot;H&quot;: 1, &quot;HV&quot;: 1} | bfloat16 | 未测试 | N/A |
| chunk_scaled_dot_kkt_fwd_kernel | {&quot;B&quot;: 2, &quot;T&quot;: 31, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |

<a id="op-11e76c12903fbfbc"></a>

### chunk_scaled_dot_kkt

ID: `42_chunk_scaled_dot_kkt_fwd_gated`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| chunk_scaled_dot_kkt_fwd_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 32, &quot;H&quot;: 2, &quot;HV&quot;: 4} | bfloat16 | 未测试 | N/A |

<a id="op-2ed16ae986cc3e9a"></a>

### sdpa

ID: `44_sdpa`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| sdpa_kernel | N/A | N/A | 未测试 | N/A |

<a id="op-2e1e8e2962571dd9"></a>

### fwd_kernel / bwd_preprocess / bwd_preprocess_ifmn / bwd_qkv

ID: `extra_tests/fa`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |
| fwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess | N/A | bfloat16 | 未测试 | N/A |
| bwd_preprocess_ifmn | N/A | bfloat16 | 未测试 | N/A |
| bwd_qkv_kernel | N/A | bfloat16 | 未测试 | N/A |

<a id="op-acf8ffa6e2ea2881"></a>

### causal_conv1d

ID: `04__c_conv_varlen`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| causal_conv1d_fwd_kernel | {&quot;N&quot;: 4, &quot;T&quot;: 500} | float16 | 未测试 | N/A |
| causal_conv1d_fwd_kernel | {&quot;N&quot;: 3, &quot;T&quot;: 1024} | float16 | 未测试 | N/A |
| causal_conv1d_fwd_kernel | {&quot;N&quot;: 4, &quot;T&quot;: 500} | float16 | 未测试 | N/A |
| causal_conv1d_fwd_kernel | {&quot;N&quot;: 4, &quot;T&quot;: 1024} | float16 | 未测试 | N/A |
| causal_conv1d_fwd_kernel | {&quot;N&quot;: 5, &quot;T&quot;: 8192} | float32 | 未测试 | N/A |
| causal_conv1d_fwd_kernel | {&quot;N&quot;: 3, &quot;T&quot;: 7666} | float32 | 未测试 | N/A |
| causal_conv1d_fwd_kernel | {&quot;N&quot;: 5, &quot;T&quot;: 12291} | bfloat16 | 未测试 | N/A |
| causal_conv1d_fwd_kernel | {&quot;N&quot;: 5, &quot;T&quot;: 12291} | bfloat16 | 未测试 | N/A |
| causal_conv1d_fwd_kernel | {&quot;N&quot;: 6, &quot;T&quot;: 11357} | bfloat16 | 未测试 | N/A |
| causal_conv1d_fwd_kernel | {&quot;N&quot;: 9, &quot;T&quot;: 10287} | bfloat16 | 未测试 | N/A |

<a id="op-67494a963fde9a13"></a>

### causal_conv1d_update_bdt

ID: `06_ttest_causal_conv1d_update_state`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| causal_conv1d_update_kernel_bdt_fwd | {&quot;B&quot;: 1, &quot;T&quot;: 12291} | float16 | 未测试 | N/A |
| causal_conv1d_update_kernel_bdt_fwd | {&quot;B&quot;: 1, &quot;T&quot;: 5000} | float16 | 未测试 | N/A |
| causal_conv1d_update_kernel_bdt_fwd | {&quot;B&quot;: 2, &quot;T&quot;: 64} | float16 | 未测试 | N/A |
| causal_conv1d_update_kernel_bdt_fwd | {&quot;B&quot;: 2, &quot;T&quot;: 128} | float16 | 未测试 | N/A |
| causal_conv1d_update_kernel_bdt_fwd | {&quot;B&quot;: 2, &quot;T&quot;: 64} | float16 | 未测试 | N/A |
| causal_conv1d_update_kernel_bdt_fwd | {&quot;B&quot;: 3, &quot;T&quot;: 1446} | float16 | 未测试 | N/A |
| causal_conv1d_update_kernel_bdt_fwd | {&quot;B&quot;: 1, &quot;T&quot;: 32} | float16 | 未测试 | N/A |

<a id="op-e6997bfc2ab75bea"></a>

### causal_conv1d_bwd

ID: `29_causal_conv1d_bwd_kernel`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| causal_conv1d_bwd_kernel | N/A | float32 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | float32 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | float32 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | float32 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | bfloat16 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | float16 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | float16 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | float16 | 未测试 | N/A |
| causal_conv1d_bwd_kernel | N/A | float16 | 未测试 | N/A |

<a id="op-4c090f6b73961379"></a>

### top_p_filter

ID: `10_test_topp_filter`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _top_p_filter_kernel | [20, 151936] | float32 | 未测试 | N/A |

<a id="op-99c6c06763d5d346"></a>

### reject_sampler

ID: `11_test_reject_sampling`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _reject_sampler_kernel | [15, 4, 155136] | float32 | 未测试 | N/A |

<a id="op-9c2e179f2cace378"></a>

### join_prob_reject_sampler

ID: `12_test_magic_reject_sampling`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _join_prob_reject_sampler_kernel | [15, 5, 155136] | float32 | 未测试 | N/A |

<a id="op-719c96c6175f95f1"></a>

### fused_penalty_temp

ID: `28__apply_penalties_temp`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _fused_penalty_temp_kernel | [1, 1024] | float32 | 未测试 | N/A |
| _fused_penalty_temp_kernel | [2, 1024] | float32 | 未测试 | N/A |
| _fused_penalty_temp_kernel | [1, 1025] | float32 | 未测试 | N/A |
| _fused_penalty_temp_kernel | [2, 1025] | float32 | 未测试 | N/A |

<a id="op-d63556d709ea2433"></a>

### top_p_sample

ID: `49__topp_sampling`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _top_p_sample_kernel | [1, 32000] | float16 | 未测试 | N/A |
| _top_p_sample_kernel | [1, 32000] | bfloat16 | 未测试 | N/A |
| _top_p_sample_kernel | [1, 32000] | float32 | 未测试 | N/A |
| _top_p_sample_kernel | [2, 32000] | float16 | 未测试 | N/A |
| _top_p_sample_kernel | [2, 32000] | bfloat16 | 未测试 | N/A |
| _top_p_sample_kernel | [2, 32000] | float32 | 未测试 | N/A |
| _top_p_sample_kernel | [8, 65024] | float16 | 未测试 | N/A |
| _top_p_sample_kernel | [8, 65024] | bfloat16 | 未测试 | N/A |
| _top_p_sample_kernel | [8, 65024] | float32 | 未测试 | N/A |
| _top_p_sample_kernel | [16, 32000] | float16 | 未测试 | N/A |
| _top_p_sample_kernel | [16, 32000] | bfloat16 | 未测试 | N/A |
| _top_p_sample_kernel | [16, 32000] | float32 | 未测试 | N/A |
| _top_p_sample_kernel | [32, 32000] | float16 | 未测试 | N/A |
| _top_p_sample_kernel | [32, 32000] | bfloat16 | 未测试 | N/A |
| _top_p_sample_kernel | [32, 32000] | float32 | 未测试 | N/A |
| _top_p_sample_kernel | [128, 32000] | float16 | 未测试 | N/A |
| _top_p_sample_kernel | [128, 32000] | bfloat16 | 未测试 | N/A |
| _top_p_sample_kernel | [128, 32000] | float32 | 未测试 | N/A |
| _top_p_sample_kernel | [512, 32000] | float16 | 未测试 | N/A |
| _top_p_sample_kernel | [512, 32000] | bfloat16 | 未测试 | N/A |
| _top_p_sample_kernel | [512, 32000] | float32 | 未测试 | N/A |
| _top_p_sample_kernel | [1024, 151936] | float16 | 未测试 | N/A |
| _top_p_sample_kernel | [1024, 151936] | bfloat16 | 未测试 | N/A |
| _top_p_sample_kernel | [1024, 151936] | float32 | 未测试 | N/A |
| _top_p_sample_kernel | [16, 92544] | float16 | 未测试 | N/A |
| _top_p_sample_kernel | [16, 92544] | bfloat16 | 未测试 | N/A |
| _top_p_sample_kernel | [16, 92544] | float32 | 未测试 | N/A |

<a id="op-aa347c79592808a5"></a>

### binned_copy

ID: `01__binned_copy`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _binned_copy | [4, 2] | N/A | 未测试 | N/A |
| _binned_copy | [4, 64] | N/A | 未测试 | N/A |
| _binned_copy | [4, 256] | N/A | 未测试 | N/A |
| _binned_copy | [4, 2] | N/A | 未测试 | N/A |
| _binned_copy | [4, 2] | N/A | 未测试 | N/A |
| _binned_copy | [4, 512] | N/A | 未测试 | N/A |

<a id="op-5579bf8df5a9197d"></a>

### binned_copy / binned_copy_wgrad

ID: `02__binned_copy_wgrad`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _binned_copy | [8, 96] | N/A | 未测试 | N/A |
| _binned_copy_wgrad | [8, 96] | N/A | 未测试 | N/A |
| _binned_copy | [16, 64] | N/A | 未测试 | N/A |
| _binned_copy_wgrad | [16, 64] | N/A | 未测试 | N/A |
| _binned_copy | [32, 64] | N/A | 未测试 | N/A |
| _binned_copy_wgrad | [32, 64] | N/A | 未测试 | N/A |
| _binned_copy | [1024, 1536] | N/A | 未测试 | N/A |
| _binned_copy_wgrad | [1024, 1536] | N/A | 未测试 | N/A |
| _binned_copy | [1024, 1536] | N/A | 未测试 | N/A |
| _binned_copy_wgrad | [1024, 1536] | N/A | 未测试 | N/A |
| _binned_copy | [1024, 1536] | N/A | 未测试 | N/A |
| _binned_copy_wgrad | [1024, 1536] | N/A | 未测试 | N/A |
| _binned_copy | [1024, 1536] | N/A | 未测试 | N/A |
| _binned_copy_wgrad | [1024, 1536] | N/A | 未测试 | N/A |
| _binned_copy | [16384, 1] | N/A | 未测试 | N/A |
| _binned_copy_wgrad | [16384, 1] | N/A | 未测试 | N/A |
| _binned_copy | [16384, 768] | N/A | 未测试 | N/A |
| _binned_copy_wgrad | [16384, 768] | N/A | 未测试 | N/A |

<a id="op-8a9523e315aa1358"></a>

### store_label_cache

ID: `13_test_store_lowrank`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _store_label_cache_kernel | {&quot;label_cache_shape&quot;: [256, 1, 512, 128], &quot;key_lr_shape&quot;: [1, 128]} | bfloat16 | 未测试 | N/A |

<a id="op-09c247256b3ff7b2"></a>

### padded_copy_gather

ID: `15__padded_copy`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1024} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 4, &quot;hs&quot;: 2} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1024} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 4, &quot;hs&quot;: 2} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1024} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 4, &quot;hs&quot;: 2} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1024} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 4, &quot;hs&quot;: 2} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1024} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 4, &quot;hs&quot;: 2} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_gather | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |

<a id="op-aff9c16cc019d776"></a>

### padded_copy_wgrad

ID: `16__padded_copy_wgrad`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1024} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 4, &quot;hs&quot;: 2} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1024} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 4, &quot;hs&quot;: 2} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1024} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 4, &quot;hs&quot;: 2} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1024} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 4, &quot;hs&quot;: 2} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1024} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 4, &quot;hs&quot;: 2} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 768} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 16384, &quot;hs&quot;: 1} | N/A | 未测试 | N/A |
| _padded_copy_wgrad | {&quot;sl&quot;: 1024, &quot;hs&quot;: 1536} | N/A | 未测试 | N/A |

<a id="op-30c3770bd8fec0e0"></a>

### store_paged_kv_cache

ID: `23_test_store_paged_kv`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _store_paged_kv_cache_kernel | [85, 100, 1] | float32 | 未测试 | N/A |

<a id="op-8f39336c093a5606"></a>

### chunk_gated_delta_rule_bwd_dhu_blockdim64_npu

ID: `25_chunk_gated_delta_rule_bwd_dhu`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| chunk_gated_delta_rule_bwd_kernel_dhu_blockdim64_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2, &quot;K&quot;: 64, &quot;V&quot;: 64} | bfloat16 | 未测试 | N/A |

<a id="op-6b4ee8aebcc7b77d"></a>

### fused_sigmoid_gating_delta_rule_update

ID: `30_fused_sigmoid_gating_delta_rule_update_kernel`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| fused_sigmoid_gating_delta_rule_update_kernel | N/A | N/A | 未测试 | N/A |
| fused_sigmoid_gating_delta_rule_update_kernel | N/A | N/A | 未测试 | N/A |
| fused_sigmoid_gating_delta_rule_update_kernel | N/A | N/A | 未测试 | N/A |
| fused_sigmoid_gating_delta_rule_update_kernel | N/A | N/A | 未测试 | N/A |
| fused_sigmoid_gating_delta_rule_update_kernel | N/A | N/A | 未测试 | N/A |
| fused_sigmoid_gating_delta_rule_update_kernel | N/A | N/A | 未测试 | N/A |
| fused_sigmoid_gating_delta_rule_update_kernel | N/A | N/A | 未测试 | N/A |
| fused_sigmoid_gating_delta_rule_update_kernel | N/A | N/A | 未测试 | N/A |

<a id="op-9548adbae98a71ec"></a>

### prepare_wy_repr_bwd_k_npu / prepare_wy_repr_bwd_v_npu / prepare_wy_repr_bwd_da_mask_npu / prepare_wy_repr_bwd_da_dot1_npu / prepare_wy_repr_bwd_da_dot2_npu / prepare_wy_repr_bwd_da_gate_npu / prepare_wy_repr_bwd_finalize_k_npu / prepare_wy_repr_bwd_finalize_a2_npu / prepare_wy_repr_bwd_finalize_dg_npu

ID: `31_prepare_wy_repr_bwd`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| prepare_wy_repr_bwd_k_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_v_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_mask_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_dot1_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_dot2_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_gate_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_k_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_a2_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_dg_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_k_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 4} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_v_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 4} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_mask_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 4} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_dot1_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 4} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_dot2_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 4} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_gate_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 4} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_k_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 4} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_a2_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 4} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_dg_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 4} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_k_npu | {&quot;B&quot;: 1, &quot;T&quot;: 256, &quot;H&quot;: 4, &quot;HV&quot;: 4} | float16 | 未测试 | N/A |
| prepare_wy_repr_bwd_v_npu | {&quot;B&quot;: 1, &quot;T&quot;: 256, &quot;H&quot;: 4, &quot;HV&quot;: 4} | float16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_mask_npu | {&quot;B&quot;: 1, &quot;T&quot;: 256, &quot;H&quot;: 4, &quot;HV&quot;: 4} | float16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_dot1_npu | {&quot;B&quot;: 1, &quot;T&quot;: 256, &quot;H&quot;: 4, &quot;HV&quot;: 4} | float16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_dot2_npu | {&quot;B&quot;: 1, &quot;T&quot;: 256, &quot;H&quot;: 4, &quot;HV&quot;: 4} | float16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_gate_npu | {&quot;B&quot;: 1, &quot;T&quot;: 256, &quot;H&quot;: 4, &quot;HV&quot;: 4} | float16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_k_npu | {&quot;B&quot;: 1, &quot;T&quot;: 256, &quot;H&quot;: 4, &quot;HV&quot;: 4} | float16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_a2_npu | {&quot;B&quot;: 1, &quot;T&quot;: 256, &quot;H&quot;: 4, &quot;HV&quot;: 4} | float16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_dg_npu | {&quot;B&quot;: 1, &quot;T&quot;: 256, &quot;H&quot;: 4, &quot;HV&quot;: 4} | float16 | 未测试 | N/A |
| prepare_wy_repr_bwd_k_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_v_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_mask_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_dot1_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_dot2_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_da_gate_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_k_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_a2_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |
| prepare_wy_repr_bwd_finalize_dg_npu | {&quot;B&quot;: 2, &quot;T&quot;: 128, &quot;H&quot;: 2, &quot;HV&quot;: 2} | bfloat16 | 未测试 | N/A |

<a id="op-363e314b22a07110"></a>

### chunk_gated_delta_rule_h_k128_blockdim128

ID: `36_chunk_gated_delta_rule_fwd_h`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| chunk_gated_delta_rule_fwd_kernel_h_k128_blockdim128 | {&quot;B&quot;: 1, &quot;T&quot;: 1024, &quot;H&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | N/A | 未测试 | N/A |
| chunk_gated_delta_rule_fwd_kernel_h_k128_blockdim128 | {&quot;B&quot;: 4, &quot;T&quot;: 1024, &quot;H&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | N/A | 未测试 | N/A |
| chunk_gated_delta_rule_fwd_kernel_h_k128_blockdim128 | {&quot;B&quot;: 16, &quot;T&quot;: 1024, &quot;H&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | N/A | 未测试 | N/A |
| chunk_gated_delta_rule_fwd_kernel_h_k128_blockdim128 | {&quot;B&quot;: 1, &quot;T&quot;: 8192, &quot;H&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | N/A | 未测试 | N/A |
| chunk_gated_delta_rule_fwd_kernel_h_k128_blockdim128 | {&quot;B&quot;: 4, &quot;T&quot;: 8192, &quot;H&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | N/A | 未测试 | N/A |
| chunk_gated_delta_rule_fwd_kernel_h_k128_blockdim128 | {&quot;B&quot;: 16, &quot;T&quot;: 8192, &quot;H&quot;: 8, &quot;K&quot;: 128, &quot;V&quot;: 128} | N/A | 未测试 | N/A |
| chunk_gated_delta_rule_fwd_kernel_h_k128_blockdim128 | {&quot;B&quot;: 16, &quot;T&quot;: 131072, &quot;H&quot;: 2, &quot;K&quot;: 128, &quot;V&quot;: 128} | N/A | 未测试 | N/A |
| chunk_gated_delta_rule_fwd_kernel_h_k128_blockdim128 | {&quot;B&quot;: 1, &quot;T&quot;: 16384, &quot;H&quot;: 4, &quot;K&quot;: 128, &quot;V&quot;: 128} | N/A | 未测试 | N/A |

<a id="op-d6f80eee2108109c"></a>

### chunk_local_cumsum_scalar / chunk_local_cumsum_vector

ID: `40_chunk_local_cumsum`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| chunk_local_cumsum_scalar_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 63, &quot;H&quot;: 1} | float32 | 未测试 | N/A |
| chunk_local_cumsum_vector_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 63, &quot;H&quot;: 1} | float32 | 未测试 | N/A |
| chunk_local_cumsum_scalar_kernel | {&quot;B&quot;: 2, &quot;T&quot;: 500, &quot;H&quot;: 4} | float32 | 未测试 | N/A |
| chunk_local_cumsum_vector_kernel | {&quot;B&quot;: 2, &quot;T&quot;: 500, &quot;H&quot;: 4} | float32 | 未测试 | N/A |
| chunk_local_cumsum_scalar_kernel | {&quot;B&quot;: 2, &quot;T&quot;: 1000, &quot;H&quot;: 5} | float32 | 未测试 | N/A |
| chunk_local_cumsum_vector_kernel | {&quot;B&quot;: 2, &quot;T&quot;: 1000, &quot;H&quot;: 5} | float32 | 未测试 | N/A |
| chunk_local_cumsum_scalar_kernel | {&quot;B&quot;: 3, &quot;T&quot;: 1024, &quot;H&quot;: 6} | float32 | 未测试 | N/A |
| chunk_local_cumsum_vector_kernel | {&quot;B&quot;: 3, &quot;T&quot;: 1024, &quot;H&quot;: 6} | float32 | 未测试 | N/A |
| chunk_local_cumsum_scalar_kernel | {&quot;B&quot;: 4, &quot;T&quot;: 2048, &quot;H&quot;: 8} | float32 | 未测试 | N/A |
| chunk_local_cumsum_vector_kernel | {&quot;B&quot;: 4, &quot;T&quot;: 2048, &quot;H&quot;: 8} | float32 | 未测试 | N/A |

<a id="op-c9044689e684eaf1"></a>

### recompute_w_u

ID: `50_recompute_w_u_fwd`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 1024, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 4, &quot;T&quot;: 1024, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 16, &quot;T&quot;: 1024, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 8192, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 4, &quot;T&quot;: 8192, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 16384, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 1024, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 4, &quot;T&quot;: 1024, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 16, &quot;T&quot;: 1024, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 8192, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 4, &quot;T&quot;: 8192, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |
| recompute_w_u_fwd_kernel | {&quot;B&quot;: 1, &quot;T&quot;: 16384, &quot;H&quot;: 32, &quot;HV&quot;: 32, &quot;K&quot;: 128, &quot;V&quot;: 128} | bfloat16 | 未测试 | N/A |

<a id="op-7fba9421c7fe0216"></a>

### solve_tril_16x16

ID: `24_solve_tril`

| kernel_name | Shape | DType | 精度是否通过 | Latency (μs) |
|---|---|---|---|---:|
| _solve_tril_16x16_kernel | [1, 63, 1, 16] | float32 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [1, 64, 1, 32] | float32 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [1, 64, 1, 64] | float32 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [2, 500, 4, 32] | float32 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [2, 1000, 5, 64] | float32 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [3, 1024, 6, 64] | float32 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [1, 63, 1, 16] | float16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [1, 64, 1, 32] | float16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [1, 64, 1, 64] | float16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [2, 500, 4, 32] | float16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [2, 1000, 5, 64] | float16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [3, 1024, 6, 64] | float16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [1, 63, 1, 16] | bfloat16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [1, 64, 1, 32] | bfloat16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [1, 64, 1, 64] | bfloat16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [2, 500, 4, 32] | bfloat16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [2, 1000, 5, 64] | bfloat16 | 未测试 | N/A |
| _solve_tril_16x16_kernel | [3, 1024, 6, 64] | bfloat16 | 未测试 | N/A |
