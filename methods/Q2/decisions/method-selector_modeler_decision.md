---
decision_id: q2_method_choice
status: DECIDED
decided_by: human
captured_in_mode: learning
choice: "Q2-M3"
ai_suggestion: "Q2-M3 — PoC的RMSE与MAE均明显最低，值得进入严格非前视的全年预测—优化联动验证。"
evidence_refs:
  - "methods/Q2/poc/q2_m1_persistence_poc.py"
  - "methods/Q2/poc/q2_m2_rolling_mean_poc.py"
  - "methods/Q2/poc/q2_m3_gradient_boosting_poc.py"
  - "Q2-M1: RMSE 1270.33 kW; MAE 751.36 kW"
  - "Q2-M2: RMSE 1044.67 kW; MAE 823.39 kW"
  - "Q2-M3: RMSE 301.91 kW; MAE 196.96 kW"
  - "Q2-M1/M2/M3 emergency-cost proxies: 261011.20 / 273087.94 / 54992.61 yuan"
  - "evaluation window: 2025-01-22..2025-01-28"
rejected_alternatives:
  - candidate_id: "Q2-M1"
    reason: "前日持久性虽简单透明、适合作为基线，但RMSE为1270.33 kW且尾部欠预测风险较高，不作为正式主模型。"
  - candidate_id: "Q2-M2"
    reason: "7日均值的RMSE虽降至1044.67 kW，但MAE升至823.39 kW，欠预测电量和紧急成本代理也高于M1，未稳定降低运营风险。"
---

# Q2 建模者方法决定

## Modeler's rationale

我选择Q2-M3梯度提升模型进入全年预测—优化实验。统一时间外窗口中，其RMSE为301.91 kW，明显低于M1的1270.33 kW和M2的1044.67 kW。由于紧急购电价格为正常价格的5倍，少数严重欠预测可能显著推高总费用，因此采用对大误差更敏感的RMSE作为预测层主要指标更合理。M3的欠预测电量和紧急购电成本代理也分别降至15,258.78 kWh和54,992.61元，进一步说明其控制欠预测风险的能力更强。

不选择M1作为主模型，是因为前日持久性虽然简单透明、适合作为基线，但其RMSE和尾部欠预测风险较高，难以满足高额紧急购电场景下的精度要求。不选择M2作为主模型，是因为它的RMSE虽较M1有所下降，但MAE由751.36 kW上升至823.39 kW，欠预测电量和紧急成本代理也分别增至66,907.21 kWh和273,087.94元，说明7日均值平滑没有稳定转化为更低的运营风险。

因此，M1保留为透明基线，M2作为简单平滑方法的对照，M3作为主要候选模型；同时对M3实施严格的时间切分、特征时间戳和滚动训练防泄漏审计。最终是否采用M3，仍应以全年总购电费用、5倍紧急购电量及欠预测尾部风险为核心标准，RMSE和MAE仅作为预测层辅助指标。
