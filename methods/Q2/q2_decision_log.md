# Q2 Decision Log

> Canonical, append-only record of the modeler's decisions for Q2.
> Downstream narratives transcribe from here with `decision_id` provenance. Never edited in place.

---

### Q2-D01 · method_choice · 2026-09-12T02:57+08:00 · mode: learning
- **options_considered**: Q2-M1前日持久性 / Q2-M2近7日同槽均值 / Q2-M3梯度提升
- **evidence**: `methods/Q2/poc/q2_m1_persistence_poc.py`、`q2_m2_rolling_mean_poc.py`、`q2_m3_gradient_boosting_poc.py`；2025-01-22至28日统一时间外窗口中，M1/M2/M3的RMSE分别为1270.33/1044.67/301.91 kW，紧急购电成本代理分别为261011.20/273087.94/54992.61元
- **ai_suggestion**: Q2-M3 — PoC的RMSE与MAE均明显最低，值得进入严格非前视的全年预测—优化联动验证
- **modeler_decision**: Q2-M3（CHOSEN）；Q2-M1保留为基线，Q2-M2保留为对照
- **modeler_rationale**: 选择Q2-M3进入全年预测—优化实验，因为其RMSE为301.91 kW，明显低于M1的1270.33 kW和M2的1044.67 kW；在紧急购电价格为正常价格5倍的条件下，RMSE对少数严重欠预测更敏感。M3的欠预测电量和紧急成本代理也分别降至15258.78 kWh和54992.61元。M1虽透明但误差和尾部风险较高，仅保留为基线；M2的MAE由M1的751.36 kW升至823.39 kW，欠预测量及紧急成本代理也更高，仅保留为简单平滑对照。M3须接受严格的时间切分、特征时间戳和滚动训练防泄漏审计；最终按全年总费用、紧急购电及尾部风险评价，RMSE和MAE只作预测层辅助指标。
- **confidence**: medium
- **supersedes**: —
