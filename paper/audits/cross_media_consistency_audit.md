# Cross-Media Consistency Audit Report

> **Status**: NOT_RUN（G6）/ INCREMENTAL_CHECK_PASSED_WITH_WARNINGS
> **Date**: 2026-09-12
> **Scope**: Q3、Q4 round2参数、代码、结果、工作簿、稳健性工件与进度文档
> **Source-of-truth tier**: `results/Q3/experiments/round2/metrics/metrics.json`、`results/Q4/experiments/round2/metrics/metrics.json`；尚无冻结数字

## Pass Items

1. ✅ 参数 `RESERVE_ALPHA=0.99` 在 `src/common/config.py:30`、Q3 round2指标、Q4 round2指标和 `planning/symbol_table.md:68` 中一致。
2. ✅ Q3和Q4运行摘要均记录round编号2及0.99参数；运行入口把轮次传给独立的 `experiments/round2/` 目录，没有覆盖round1。
3. ✅ Q3报告中的总费用17,469,451.07元、紧急购电959,911.02 kWh与round2 JSON/CSV在报告精度内一致。
4. ✅ Q3报告中的相对M1变化：总费用+3.58%、紧急购电-17.50%、紧急量CVaR95-0.97%，与 `robustness/Q3/baseline_comparison.csv` 一致。
5. ✅ Q4-3报告中的总费用18,405,519.64元、紧急购电966,930.38 kWh、未来价格泄漏0，与round2指标一致。
6. ✅ `output/result3.xlsx` 和 `output/result4-3.xlsx` 的工作表及行列结构与官方模板一致，计划/调整矩阵全部为非负有限值。
7. ✅ Q3/Q4 round2年末SOC均为6000 kWh，同时充放电为0，最大平衡与SOC残差均低于 $2\times10^{-11}$ kWh。
8. ✅ Q3/Q4 README、TASKS、进度看板、数据报告和数据字典均已指向round2当前结果，并明确round1只作历史证据。
9. ✅ 完整回归测试17项通过，覆盖成本公式、非前视、物理约束、工作簿结构、参数传播和原始附件哈希。

## Divergences and Warnings

| # | Severity | Dimension | Claim Location | Source/Target Location | Claim | Actual State | Repair Skill |
|---|---|---|---|---|---|---|---|
| 1 | BLOCKING | decision provenance | `methods/Q3/decisions/reserve-alpha_modeler_decision.md:7-34` | `methods/Q3/q3_decision_log.md` | 选择0.99 | 用户已明确选择，但人工理由仍为哨兵、状态PENDING，不能写入决定日志 | modeler-decision-logger（需用户先写理由） |
| 2 | BLOCKING | stability verdict | `methods/Q3/decisions/robustness-checker_modeler_decision.md` | `robustness/Q3/q3_robustness_report.md` | Q3稳定性 | 置信度与人工理由均PENDING，G4.5未通过 | robustness-checker / modeler-decision-logger |
| 3 | WARNING | missing evidence | `robustness/Q3/uploaded_q3_robustness_report.md:53-57` | `robustness/Q3/validation_rerun.json`、嵌套验证CSV | 上传报告称证据可追溯 | 所引用的验证哈希和嵌套CSV未上传；本轮只复现全年固定参数结果 | robustness-checker |

## Unauditable Items

| # | Reason | Affects | Suggested Resolution |
|---|---|---|---|
| 1 | Q3/Q4尚无 `frozen_numbers.json` | 最终论文数值追溯 | G4.5通过后运行solution-package-builder |
| 2 | 尚无论文正文 | 论文数值、图表、符号和决定来源 | 结果冻结并形成材料包后重新运行正式G6审计 |
| 3 | 上传嵌套验证报告缺少原始CSV和验证哈希 | “0.99具有独立/盲测稳定性”的主张 | 上传原始工件或将结论限定为回溯式辅助证据 |

## Verdict

- **当前round2机械一致性**：通过，有警示。
- **G4结果冻结允许**：否；缺少人工参数理由、稳定性置信度和结果判定。
- **最终论文组装允许**：否。
- **Blocking divergences**：2。
- **Warnings**：1。
- **Recommended next skill**：用户完成两项人工理由后运行 `modeler-decision-logger`。
