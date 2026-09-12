---
schema_version: "1.0"
skill: "robustness-checker"
scope: "Q3"
decision_id: "q3_stability_verdict"
decision_point: "confidence"
status: PENDING
decided_by: human
decided_at: ""
captured_in_mode: learning
choice: "needs_caution"
choice_source: "建模者在当前会话中明确写出：needs_caution"
ai_suggestion: "WITHHELD_UNTIL_HUMAN_RATIONALE"
evidence_refs:
  - "robustness/Q3/q3_robustness_report.md"
  - "robustness/Q3/reserve_alpha_sensitivity.csv"
  - "robustness/Q3/baseline_comparison.csv"
  - "robustness/Q3/round_comparison.csv"
rejected_alternatives:
  - candidate_id: "high"
    reason: "<<<HUMAN>>>"
  - candidate_id: "medium"
    reason: "<<<HUMAN>>>"
  - candidate_id: "needs_caution"
    reason: "<<<HUMAN>>>"
---

# Q3 稳定性判定

## Modeler's rationale

<<<HUMAN：已选择 needs_caution。请用自己的话说明理由，并引用稳健性报告中的至少一个具体数值；同时说明为何不选择 high 与 medium。>>>
