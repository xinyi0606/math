# 跨媒介一致性审计

- 审计日期：2026-09-12
- 当前状态：NOT_RUN
- 当前范围：C题附件归档、题面解析、问题分类、相关文献分析与初版统一符号表的增量预检
- 正式门禁：G6 未执行

## 结论

当前尚未形成论文正文、冻结结果与最终方法说明，因此无法执行面向最终交付物的正式跨媒介一致性审计，也不能给出G6通过结论。题面解析、问题分类、相关文献分析与初版统一符号表层面的增量预检已经完成，未发现这些规划工件之间的已知事实冲突。

## 建模前一致性预检

1. **PASS**：data/manifest.sha256 中 9 个工作簿的 SHA-256 与归档文件逐一一致。
2. **PASS**：附件与问题 1—4 的对应关系在题面、data/data_report.md 和 docs/data-dictionary.md 中一致。
3. **PASS**：结果模板文件名与题面要求的 result1、result2、result3、result4-2、result4-3 一致。
4. **PASS**：原始逐日数据覆盖 2025-01-01 至 2025-12-31，结果模板覆盖 2025-02-01 至 2025-12-31，符合首月用于计划/预测、后续月份输出运行结果的结构。
5. **PASS**：输入功率单位为 kW、购电结果单位为 kWh、电价单位为元/kWh；文档已明确 10 分钟功率转电量需乘以 1/6 小时。
6. **PASS**：result2.xlsx 与 result4-2.xlsx 结构一致，result3.xlsx 与 result4-3.xlsx 结构一致，符合问题 4 复用问题 2、3 输出结构的要求。
7. **PASS**：附件 1、2、4 的 10 分钟时间轴均为 144 个时点/时段，附件 3 的预测结构为每日 4 次、每次 24 小时。
8. **PASS**：题面四个问题均在 planning/parse/problem_parse.md 与 problem_parse.json 中逐问表示，且依赖关系保持 Q1→Q2→Q3、Q2/Q3→Q4。
9. **PASS**：储能参数 12000、5000、6000、1200-10800 与 90% 在题面摘要和两份解析文件中一致。
10. **PASS**：紧急购电 5 倍、减少计划量相关价格 50%、增加购电超出部分 1.5 倍在题面摘要和两份解析文件中一致。
11. **PASS**：四个指定日期及“Q2、Q3均按表1、表2、表3展示”的要求在 docs/problem-definition.md 和两份解析文件中一致。
12. **PASS**：problem_parse.json 已通过 JSON 语法校验，包含Q1-Q4四个小问、每问非空评价口径和五条已确认机制关系。
13. **PASS**：用户的确认原话、来源任务ID与确认日期已记录在 planning/modeling_conventions.md；本次用户另行明确授权将AI起草的分类论证作为人工回答，两个授权范围已分开记录。
14. **PASS**：planning/parse/problem_parse.md 与 problem_parse.json 中已无 `[MODELER INPUT NEEDED]`、`[AI-DRAFT]` 或 `DRAFT_GATE_FAIL` 残留。
15. **PASS**：效率主口径 `eta_c=eta_d=0.9`、`sqrt(0.9)` 敏感性方案在问题定义、解析和口径记录中一致。
16. **PASS**：Q2严格非前视、附件3线性插值、调整购电量为调整后总量在问题定义、解析和口径记录中一致。
17. **PASS**：Q3取消量承担50%违约成本、增加量按1.5倍计费、紧急购电按5倍计费且不重复计费的口径一致。
18. **PASS**：Q2-Q4跨日连续、不要求每日回到固定值、全年末主约束6000 kWh的口径一致。
19. **PASS**：Q1“机制—优化混合”、Q2/Q3“预测—优化混合”和Q4“情景分析—优化混合”在 framing_input.md、problem_classification.md 与 problem_classification.json 中逐项一致。
20. **PASS**：Q1在三份分类工件中均明确为“机制主线、优化求解层”，同时保留最低成本策略的输出要求，没有被误写成纯优化或纯机制问题。
21. **PASS**：Q2在分类工件与题面解析中均遵守严格非前视边界，并将预测误差通过紧急购电传递到决策评价。
22. **PASS**：Q3在分类工件与题面解析中均包含0时、6时、12时、18时预测更新、滚动调整和非对称结算机制。
23. **PASS**：Q4在分类工件与题面解析中均表述为保持Q2/Q3其余口径不变、更换波动电价并重新求解，而非新增价格预测任务。
24. **PASS**：分类JSON通过语法解析，含Q1-Q4四条非空分类与理由，未发现待确认或草稿门禁标记。
25. **PASS**：用户授权来源在 framing_input.md、problem_classification.md 和 problem_classification.json 中均如实标为“AI起草、用户直接采纳”，没有冒充用户亲笔理由。
26. **PASS**：TASKS.md、planning/progress_dashboard.md 与 planning/parse/problem_parse.md 均将分类标记为完成、G1通过，状态一致。
27. **PASS**：三篇原文文件名、作者和年份与 docs/literature-notes.md、workspace/papers/related_paper_analysis.md 的登记一致。
28. **PASS**：文献分析对Q1-Q4均给出方法线索和不适用边界，且没有把候选方法误标为最终已选方法。
29. **PASS**：related_paper_analysis.md 中Q2/Q3的文献映射与预测—优化分类一致，Q4的文献映射与情景分析—优化分类一致。
30. **PASS**：用户已明确确认三篇PDF获得发布同意；.gitignore中的本地排除规则已移除，三篇原文与可追溯分析报告将一并纳入GitHub。
31. **PASS**：problem_parse.md与problem_parse.json均保留解析工件自身的READY_FOR_CLASSIFICATION状态，同时Markdown注明下游分类已完成；该历史工件状态与进度看板的当前全局G1通过状态不存在语义冲突。
32. **PASS**：Codex Python运行环境已实际导入NumPy 2.3.5、pandas 3.0.1和matplotlib 3.11.2，进度看板的环境记录与验证输出一致。
33. **PASS**：`symbol-table-builder` → `model-assumptions-builder` → 完善问题依赖图 → `method-selector` 的唯一优先工作链在进度看板、任务看板、问题定义、分类说明、文献分析和数据报告中一致。
34. **PASS**：规划文件均明确符号表和假设表先建立题面初版、候选方法产生后再回填方法特有内容，未将初版误标为最终版。
35. **PASS**：方法候选、PoC、代码和结果文件均尚未生成；进度看板继续禁止越过全局基础工件和G2门禁直接生成正式模型代码。
36. **PASS**：TASKS.md中的四项工作严格按统一符号表、全局模型假设、问题依赖图、候选方法池排序；统一符号表已完成，其余任务待认领，不存在文件职责重叠。
37. **PASS**：planning/symbol_table.md中的储能容量12000 kWh、运行上下限1200/10800 kWh、最大功率5000 kW、单步电量上限5000/6 kWh与题面解析及冻结口径一致。
38. **PASS**：planning/symbol_table.md中的主模型效率 `eta_c=eta_d=0.9`、敏感性方案两侧取 `sqrt(0.9)` 与 planning/modeling_conventions.md 一致。
39. **PASS**：统一符号表将大写 `P` 固定为功率、小写变量固定为10分钟电量，并对每个核心量列出单位，未发现kW与kWh混用。
40. **PASS**：统一符号表的能量平衡、储能状态转移、弃光、禁止负购电售电、充放电互斥与跨日衔接关系均与五条冻结机制一致。
41. **PASS**：Q1、Q2/Q4-2、Q3/Q4-3的最终外网购电定义分别为计划购电、计划加紧急购电、最终调整加紧急购电，与冻结口径一致。
42. **PASS**：Q3结算式中的0.5退款比例、1.5上调倍数和5倍紧急购电仅结算一次，与冻结公式一致。
43. **PASS**：用户《符号说明.docx》中的 `L_t,P_t,N_t,G_t,H_t,C_t,D_t,E_t,p_t,eta,q,S,W,rho,lambda,alpha,tau` 均已在符号映射表中逐项处理；未选方法的符号明确标为暂不启用。
44. **PASS**：日期索引采用 `n`，未与放电量 `d_{n,t}` 重名；正常电价 `p_{n,t}` 未与功率 `P` 重名；调整后总量 `q^A` 未误写为有符号增减量。
45. **PASS**：TASKS.md将统一符号表标为已完成，planning/progress_dashboard.md将当前动作顺延至模型假设，二者与实际工件状态一致。

## 尚不可审计的内容

- 初版统一符号表已存在；预测、风险、情景与求解辅助符号须待 `method-selector` 完成后回填，因此这些方法特有符号当前不可审计。
- 尚无冻结参数、冻结数值结果或 frozen_numbers.json。
- 尚无正式方法说明、实验结果分析与论文正文。
- 尚无图表、附录和代码输出可供交叉核验。

## 后续门禁

题面解析、问题分类、相关文献分析与初版统一符号表均已完成，G1通过；本次符号、数值、单位、机制和工作流状态增量检查未发现规划工件漂移。下一步运行 `model-assumptions-builder`，再依次完善问题依赖图和候选方法池；`method-selector` 完成后必须回填方法特有符号。待模型结果、图表和论文正文齐备后，必须重新执行正式G6跨媒介一致性审计；当前状态仍为NOT_RUN，不允许据此批准最终装配。
