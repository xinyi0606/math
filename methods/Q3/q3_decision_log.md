# Q3 Decision Log

> Canonical, append-only record of the modeler's decisions for Q3.
> Downstream narratives transcribe from here with `decision_id` provenance. Never edited in place.

---

### Q3-D01 · method_choice · 2026-09-12T03:18+08:00 · mode: learning
- **options_considered**: Q3-M1仅00:00预测不调整 / Q3-M2确定性滚动优化 / Q3-M3分位安全裕度滚动优化
- **evidence**: `methods/Q3/poc/q3_m1_midnight_only_poc.py`、`q3_m2_latest_update_poc.py`、`q3_m3_quantile_reserve_poc.py`；统一窗口中M1/M2/M3的紧急购电代理分别为22338.60/5803.97/3762.09 kWh，M3的90%分位裕度为49.83 kW、覆盖率为90.77%
- **ai_suggestion**: Q3-M3 — PoC紧急购电代理最低，适合风险优先方案，但必须通过全年调整成本验证
- **modeler_decision**: Q3-M3（CHOSEN）；Q3-M1保留为基线，Q3-M2保留为对照
- **modeler_rationale**: 选择Q3-M3进入全年预测—优化实验，并将尾部紧急购电风险置于优先位置。M3采用49.83 kW的90%经验分位安全裕度，覆盖率为90.77%，紧急购电代理为3762.09 kWh，较M1的22338.60 kWh降低83.16%，较M2的5803.97 kWh进一步降低35.18%。愿意为降低尾部风险承担一定的计划购电和调整成本。M1无法利用日内更新，仅作不调整基线；M2未对光伏高估误差设置显式安全裕度，仅作确定性滚动对照。本次选择不预先断言M3全年费用最低；若正式实验中增加的计划与调整成本明显超过紧急购电风险收益，则重新校准安全裕度或回退M2。
- **confidence**: medium
- **supersedes**: —
