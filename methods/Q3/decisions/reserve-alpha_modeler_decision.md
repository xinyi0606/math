---
schema_version: "1.0"
skill: "robustness-checker"
scope: "Q3"
decision_id: "q3_reserve_alpha"
decision_point: "hyperparameter"
status: PENDING
decided_by: human
decided_at: ""
captured_in_mode: learning
choice: "0.99"
choice_source: "用户在当前会话中明确写出：选择0.99"
ai_suggestion: "WITHHELD_UNTIL_HUMAN_RATIONALE"
evidence_refs:
  - "results/Q3/experiments/round2/experiment_report.md"
  - "robustness/Q3/reserve_alpha_sensitivity.csv"
  - "robustness/Q3/baseline_comparison.csv"
  - "0.99相对M1紧急购电量下降17.50%，总费用增加3.58%"
rejected_alternatives:
  - candidate_id: "0.95"
    reason: "<<<HUMAN>>>"
  - candidate_id: "0.975"
    reason: "<<<HUMAN>>>"
---

# Q3 安全裕度参数决定

## Modeler's rationale

<<<HUMAN：请用自己的话说明为何愿意为降低紧急购电依赖承担额外费用，并至少引用一个上述数值。>>>

## AI-assisted rationale draft（不能替代人工理由）

选择0.99是将供电安全冗余和紧急购电依赖置于最低期望费用之前的风险偏好决定。与M1相比，该参数使全年紧急购电量下降17.50%，与0.975相比进一步减少60,836.20 kWh，而增加的全年费用为12,901.15元。虽然综合费用CVaR95和最坏日费用仍略高于M1，但0.99对累计紧急购电需求的抑制最强，适合作为“风险优先、费用次优”的竞赛方案；论文中应同步披露这一代价和证据边界。
