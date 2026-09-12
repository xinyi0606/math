# Q3 Robustness and Sensitivity Report

## 1. Summary

- **Computed evidence**：固定 $\alpha=0.99$ 后，全年紧急购电量相对 M1 下降 17.50%，每日紧急量 CVaR95 下降 0.97%；全年总费用、综合费用 CVaR95 和最坏日费用分别上升 3.58%、2.17% 和 1.83%。
- **AI-suggested stability reading**：按 learning 模式暂不公开，等待建模者先填写稳定性理由。
- **Verdict status**：PENDING，由 `methods/Q3/decisions/robustness-checker_modeler_decision.md` 记录。
- **参数执行状态**：建模者已明确选择 0.99，round2 已据此运行；参数理由与稳定性置信度尚未完成门禁记录。

## 2. Claims Under Test

| # | 待检验结论 | 重要性 |
|---|---|---|
| 1 | 0.99 相比 0.90 能降低 Q3 的紧急购电风险 | 高 |
| 2 | 0.99 相比 0.975 的额外保险成本可控 | 高 |
| 3 | M3 相比 M1 具有尾部风险优势 | 高 |
| 4 | 参数变更不会破坏储能与信息边界约束 | 高 |

## 3. Baseline Comparison

| 指标 | M1 | M3（0.99） | M3 相对变化 |
|---|---:|---:|---:|
| 全年总费用（元） | 16,865,879.73 | 17,469,451.07 | +3.58% |
| 全年紧急购电量（kWh） | 1,163,542.65 | 959,911.02 | -17.50% |
| 每日紧急量 CVaR95（kWh） | 10,442.15 | 10,341.24 | -0.97% |
| 综合费用 CVaR95（元） | 85,016.78 | 86,859.00 | +2.17% |
| 最坏日费用（元） | 116,003.75 | 118,129.80 | +1.83% |

## 4. Completed Checks

1. **PASS-01 参数生效**：round2 指标文件与运行摘要均记录 `reserve_alpha=0.99`。
2. **PASS-02 敏感性重算**：0.80、0.90、0.95、0.975、0.99 五档均重新执行；0.95 被 0.975 支配，0.975 与 0.99 构成费用—风险前沿。
3. **PASS-03 round 改善**：0.99 相对 0.90 将总费用降低 158,324.91 元，同时将紧急购电量降低 226,380.48 kWh。
4. **PASS-04 基线比较**：0.99 相对 M1 将全年紧急购电量降低 17.50%，但总费用增加 3.58%，正反证据均已保留。
5. **PASS-05 尾部指标**：同时计算每日紧急量 CVaR95、综合费用 CVaR95 和最坏日费用，没有用全年累计量替代全部尾部风险。
6. **PASS-06 物理可行性**：年末 SOC 为 6000 kWh，同时充放电次数为 0，平衡和 SOC 残差均低于 $2\times10^{-11}$ kWh。
7. **PASS-07 下游传播**：Q4-3 已继承 0.99 重算；M3 的未来价格泄漏次数保持为 0。

## 5. Supported and Fragile Findings

| 类型 | 结论 | 证据边界 |
|---|---|---|
| 支持 | 0.99 明显降低全年累计紧急购电依赖 | 相对 M1 -17.50%，相对 round1 -226,380.48 kWh |
| 支持 | 0.99 相比 0.975 继续降低紧急购电 | 少 60,836.20 kWh，额外费用 12,901.15 元 |
| 脆弱 | “M3全面降低尾部风险” | 紧急量 CVaR95 仅改善 0.97%，综合费用 CVaR95 与最坏日费用反而上升 |
| 脆弱 | “0.99具有盲测统计保证” | 上传报告明确属于回溯式验证，且其引用的原始嵌套验证文件未上传 |

## 6. Conclusion Boundaries

0.99 适用于把“减少高价紧急购电依赖和提升供电安全冗余”置于“最低期望费用”之前的建模口径。论文不得把它表述为最低费用参数，也不得宣称它在全部尾部费用指标上优于 M1。当前结论只覆盖 2025 年数据与既定储能、价格和结算参数；多年份、效率、时间标签及终端价值扰动仍未完成。

## 7. Figure Placement

`results/Q3/experiments/round2/figures/q3_method_comparison.png` 为 Type 2 方法比较图，可用于建模诊断或方法选择说明；在完成300 dpi和中文排版前不作为正式论文图。

## 8. Generated Artifacts

- `robustness/Q3/reserve_alpha_sensitivity.csv`
- `robustness/Q3/baseline_comparison.csv`
- `robustness/Q3/round_comparison.csv`
- `robustness/Q3/uploaded_q3_robustness_report.md`
- `methods/Q3/decisions/robustness-checker_modeler_decision.md`

## 9. Handoff

稳定性置信度仍为 PENDING。建模者需用自己的理由填写决定文件并至少引用本报告中的一个具体数值；在此之前不生成 `frozen_numbers.json`，不进入论文材料包。
