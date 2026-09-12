# Q4 论文写作材料包

> **状态**：可供写作的未冻结材料包；Q4-3 继承 $\alpha=0.99$。

## 0. 快速引用

- **任务**：在滚动获知的波动电价下重新优化微电网计划与日内调整。
- **方法**：Q4-M3 历史价格情景最坏费用鲁棒 LP；选择依据 `Q4-D01`。
- **主结果（Q4-3）**：总费用 18,405,519.64 元，紧急购电 966,930.38 kWh，未来价格泄漏次数 0。
- **oracle 距离**：相对 M2 完全信息 oracle 的机会损失约 0.82%。

## 1. 可写模型内容

仅从决策时刻前的历史真实日构建 7 条价格情景，并以情景最坏费用为目标；Q4-3 在新光伏预测到达后复用 Q3 的冻结前缀、分位裕度和调整结算。M2 使用未来真实价格，仅作为性能上界。

## 2. 可写结果内容

| 内容 | 证据 | 写作状态 |
|---|---|---|
| M3 无未来价格泄漏 | `metrics.json` 中 leakage=0 | 可直接写 |
| M3 接近 oracle | 机会损失 149,161.64 元（0.82%） | 可直接写 |
| 相对 round1 的改善 | 费用 -194,932.28 元、紧急购电 -228,878.36 kWh | 可直接写 |
| 情景集覆盖全部未来价格风险 | 仅历史情景 | 不可写 |

## 3. 图表与表格

| 文件 | 建议位置 | 用途 | 状态 |
|---|---|---|---|
| `results/Q4/experiments/round2/figures/q4_price_policy_comparison.png` | 结果对比 | Q4-2/Q4-3 滚动费用轨迹 | 需 300 dpi 重绘 |
| `results/Q4/experiments/round2/tables/q4_3_daily_metrics.csv` | 附录 | 逐日方法对比 | 可用 |
| `output/result4-2.xlsx`、`output/result4-3.xlsx` | 附件交付 | 官方格式结果 | 可用 |

## 4. 结论与避免的表述

可结论：M3 在不前视未来电价的条件下获得接近 oracle 的成本。避免：把 oracle 当作可实施策略，或声称历史情景已覆盖所有价格极端。

## 5. 交叉引用

- 方法：`methods/Q4/q4_final_method_explanation.md`
- 结果：`results/Q4/reports/q4_final_result_analysis.md`
- 上游：`results/Q3/reports/q3_final_result_analysis.md`

