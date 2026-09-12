# Q1 Decision Log

> Canonical, append-only record of the modeler's decisions for Q1.
> Downstream narratives transcribe from here with `decision_id` provenance. Never edited in place.

---

### Q1-D01 · method_choice · 2026-09-12T03:43+08:00 · mode: learning
- **options_considered**: Q1-M1无储能动作 / Q1-M2连续确定性线性规划 / Q1-M3离散SOC动态规划
- **evidence**: `methods/Q1/poc/q1_m1_no_storage_poc.py`、`q1_m2_linear_program_poc.py`、`q1_m3_dynamic_program_poc.py`；M1/M2/M3费用分别为48052.05/35126.95/35982.00元，M2终端SOC误差为 $3.64\times10^{-12}$ kWh
- **ai_suggestion**: Q1-M2 — 10分钟连续LP费用最低、约束残差近零且本次解无同时充放电；M1保留为基线，M3用于离散网格交叉验证
- **modeler_decision**: Q1-M2（CHOSEN）；Q1-M1保留为基线，Q1-M3保留为交叉验证
- **modeler_rationale**: 选择Q1-M2作为正式主模型，主要看重其经济性、连续模型全局最优性和向后续问题扩展的便利性；同一附件1和10分钟尺度下，M2费用35126.95元，比M1降低12925.10元（26.90%），终端SOC误差仅 $3.64\times10^{-12}$ kWh。接受“LP先求解、逐时审计互斥、发现异常立即升级MILP”的实施规则。M1不能利用储能，仅作无储能基线；M3当前采用24个小时步和400 kWh SOC网格，只保证离散网格内最优，后续统一到10分钟尺度并加密网格作为独立核验。
- **confidence**: high
- **supersedes**: —
