# 协作任务看板

开始工作前先认领任务；同一文件尽量只由一台电脑在同一时间修改。

| 状态 | 任务 | 负责人 | 分支 | 主要文件 | 备注 |
|---|---|---|---|---|---|
| 已完成 | 项目级接入 MathModeling-skills | 电脑 A | `dev-pc-a` | `.codex/skills/`, `AGENTS.md`, `docs/math-modeling-skills/` | 已接入 28 个技能并通过文件完整性、元数据和格式检查；重启 Codex 后生效 |
| 已完成 | 收集并归档附件 1-5（含数据和结果模板） | 电脑 A | `dev-pc-a` | `data/raw/`, `data/templates/` | 用户已确认映射；原始文件校验值保持一致 |
| 已完成 | 整理主要参考文献与采用边界 | 电脑 A | `dev-pc-a` | `docs/literature-notes.md` | 三篇学位论文已登记，后续补充同行评审文献 |
| 已完成 | 核对附件字段、时间粒度、缺失值和单位 | 电脑 A | `dev-pc-a` | `data/data_report.md`, `docs/data-dictionary.md` | 基础数据可用；时间标签解释须在建模前冻结 |
| 已完成 | 解读题面并形成结构化问题解析 | 电脑 A | `dev-pc-a` | `planning/parse/`, `planning/modeling_conventions.md` | 用户已采纳证据任务结论，七项口径、五条机制关系与评价口径已冻结 |
| 已完成 | 对问题 1-4 进行类型分类 | 电脑 A | `dev-pc-a` | `planning/classification/` | Q1为机制—优化混合，Q2/Q3为预测—优化混合，Q4为情景分析—优化混合；论证由AI起草并由用户直接采纳 |
| 已完成 | 归档、分析并发布三篇主要参考文献 | 电脑 A | `dev-pc-a` | `workspace/papers/`, `docs/literature-notes.md` | 用户确认已获发布同意；原文和分析报告均纳入GitHub并已用于候选方法比较 |
| 已完成 | 完善问题依赖图 | 电脑 A | `dev-pc-a` | `planning/question_dependency.md` | 保留Q1→Q2→Q3主链、Q2/Q3→Q4双分支及非前视接口契约 |
| 已完成 | 建立统一符号、模型假设与四问候选方法池 | 电脑 A | `dev-pc-a` | `planning/`, `methods/`, `tests/` | 12个Python候选PoC均通过；Q1-M2、Q2-M3、Q3-M3、Q4-M3均已DECIDED |
| 已完成 | 建立统一储能状态转移与购电成本模型 | 电脑 A | `dev-pc-a` | `src/model-code-analyzer.md`, `src/common/` | 统一LP、预测、结算、模板与审计接口已实现并通过单元测试 |
| 已完成 | 整合手动上传的四问方法、源码与首轮结果 | 电脑 A | `dev-pc-a` | `methods/`, `src/`, `results/`, `output/`, `tests/`, `planning/` | 108个项目文件已整合；Q1按用户决定统一为机制—优化混合；本机16项回归测试全部通过 |
| 已完成 | 完成问题 1 确定性优化与 `result1.xlsx` | 电脑 A | `dev-pc-a` | `src/Q1/`, `results/Q1/`, `output/result1.xlsx` | M2费用35126.95元；互斥审计与DP网格收敛通过 |
| 待审核 | 完成问题 2 全年日前优化与 `result2.xlsx` | 电脑 A | `dev-pc-a` | `src/Q2/`, `results/Q2/`, `output/result2.xlsx` | M3首轮总费用与紧急购电均优于M1/M2；待稳健性实验 |
| 阻塞 | 完成问题 3 滚动调整与 `result3.xlsx` | 电脑 A | `dev-pc-a` | `src/Q3/`, `results/Q3/`, `output/result3.xlsx` | 0.90参数不满足回退条件；0.975/0.99需嵌套验证后确认 |
| 待审核 | 完成问题 4 波动电价重算 | 电脑 A | `dev-pc-a` | `src/Q4/`, `results/Q4/`, `output/result4-2.xlsx`, `output/result4-3.xlsx` | M3未来价格泄漏0；Q4-3待Q3参数冻结后重算 |
| 待认领 | 撰写论文并验证结果、图表和文件大小 | — | — | `docs/`, `tests/`, `output/` | 对照题面逐项验收 |

状态使用：`待认领`、`进行中`、`待审核`、`已完成`、`阻塞`。

建议分工：电脑 A 负责统一模型、求解器和问题 1/2；电脑 B 负责数据检查、问题 3/4、结果复核与论文材料。发生文件重叠时，以任务认领记录为准。
