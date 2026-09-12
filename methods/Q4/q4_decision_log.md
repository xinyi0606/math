# Q4 Decision Log

> Canonical, append-only record of the modeler's decisions for Q4.
> Downstream narratives transcribe from here with `decision_id` provenance. Never edited in place.

---

### Q4-D01 · method_choice · 2026-09-12T03:35+08:00 · mode: learning
- **options_considered**: Q4-M1波动价无储能基线 / Q4-M2全天真实价格确定性重优化 / Q4-M3历史价格情景最坏费用鲁棒LP
- **evidence**: `methods/Q4/poc/q4_m1_no_storage_poc.py`、`q4_m2_price_aware_lp_poc.py`、`q4_m3_scenario_robust_poc.py`；M1单日费用86577.76元，M2单日oracle费用74061.30元，M3三情景最坏/平均费用74373.25/61421.65元，M3终端SOC误差3.64e-12 kWh
- **ai_suggestion**: Q4-M3 — 在滚动价格边界下可用历史情景控制最坏费用，但需防止情景集过度保守
- **modeler_decision**: Q4-M3（CHOSEN）；Q4-M1保留为基线，Q4-M2保留为完全信息oracle
- **modeler_rationale**: 电价按时间滚动获知，任何决策时刻不得使用同日未来真实价格。选择Q4-M3仅用决策时刻之前的历史价格构造情景，以最坏情景费用控制尾部风险。PoC三情景最坏费用74373.25元、平均费用61421.65元，终端SOC误差3.64e-12 kWh、平衡残差1.14e-13 kWh，证明结构可解且物理可行；因样本窗口不同，不据此宣称费用优于M1/M2。M1不响应价格，仅作无储能基线；M2使用全天真实价格，在滚动边界下只作oracle。正式实验须逐日更新历史情景，比较全年费用、最坏日、紧急购电、相对oracle机会损失及情景敏感性；过度保守时调整滚动时域或情景权重，不得引入未来真实价格。
- **confidence**: medium
- **supersedes**: —
