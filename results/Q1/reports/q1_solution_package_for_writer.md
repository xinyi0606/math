# Q1 论文写作材料包

> **状态**：可供写作的未冻结材料包；依据 `planning/workflow_override.md` 继续生成。数值来自 round1 指标，未完成额外敏感性。

## 0. 快速引用

- **任务**：在给定单日负荷、光伏预测和分时电价下制定储能购电计划。
- **方法**：Q1-M2 连续线性规划；选择理由见 `methods/Q1/q1_decision_log.md` 的 `Q1-D01`。
- **主结果**：购电费用 35,126.95 元，较无储能基线节省 26.90%。
- **写作置信表述**：仅限“给定单日预测与题设约束”。

## 1. 可写模型内容

将 10 分钟功率转化为电量，最小化 $\sum_t p_tg_t$；给出供需平衡、SOC 转移、功率上下界与首末 SOC=6000 kWh。强调不售电和后验充放电互斥审计。详式见 `methods/Q1/q1_final_method_explanation.md`。

## 2. 可写结果内容

| 内容 | 证据 | 写作状态 |
|---|---|---|
| 储能降低单日购电费用 26.90% | `metrics/metrics.json`、`q1_schedule.csv` | 可直接写 |
| 调度满足物理边界 | 平衡残差 $1.14\times10^{-13}$ kWh、终端误差 $6.37\times10^{-12}$ kWh | 可直接写 |
| 连续 LP 的数值核验 | DP 50 kWh 网格差距 0.79% | 可直接写 |
| 时间标签和效率外推 | 未完成敏感性 | 仅作局限性 |

## 3. 图表与表格

| 文件 | 建议位置 | 用途 | 状态 |
|---|---|---|---|
| `results/Q1/experiments/round1/figures/q1_dispatch.png` | 结果分析 | 展示购电与 SOC 的时序调度 | 需适配论文中文标注 |
| `results/Q1/experiments/round1/tables/q1_dp_grid_convergence.csv` | 方法验证表 | 展示 DP 网格收敛 | 可用 |
| `output/result1.xlsx` | 附件交付 | 官方格式结果 | 可用 |

## 4. 结论与避免的表述

可结论：在题设单日输入下，LP 调度实现 26.90% 购电费用节省。避免：长期收益、含电池寿命成本的最优性、未经测试的时间标签鲁棒性。

## 5. 交叉引用

- 方法：`methods/Q1/q1_final_method_explanation.md`
- 结果：`results/Q1/reports/q1_final_result_analysis.md`
- 数据与符号：`planning/model_assumptions.md`、`planning/symbol_table.md`

