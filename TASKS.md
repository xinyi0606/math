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
| 已完成 | 整合完整记录分卷包的补充信息 | 电脑 A | `dev-pc-a` | `PACKAGE_README.md`, `data/data_report.md`, `results/Q1-Q4/experiments/round1/logs/`, `planning/progress_dashboard.md` | 保留当前新版规则与看板；补入数据状态修正和4份运行日志；用户明确要求本次不重跑测试 |
| 已完成 | 核验并整合最新上传的 Q3/Q4-3 结果工作簿 | 电脑 A | `dev-pc-a` | `output/result3.xlsx`, `output/result4-3.xlsx`, `data/data_report.md`, `docs/data-dictionary.md`, `planning/progress_dashboard.md` | 根目录上传件与既有规范副本 SHA-256 完全一致；已审计结构、日期、汇总和数值有效性，并移除根目录重复副本 |
| 已完成 | 整理最新上传的冻结与敏感性文件 | 电脑 A | `dev-pc-a` | `robustness/`, `workspace/archived/Q3-Q4/` | 敏感性和稳定性报告按规范路径留存；矛盾且哈希失配的冻结文件原样归档为UNVERIFIED，不作为正式数字源 |
| 已完成 | 识别并登记 Q1/Q2 最终方法说明 | 电脑 A | `dev-pc-a` | `Q1_Q2最终方法说明.docx`, `planning/progress_dashboard.md` | Q1确认M2连续线性规划；Q2确认M3非前视梯度提升预测加日前线性规划；敏感性验证和结果冻结仍待完成 |
| 已完成 | 禁用项目全部流程门禁 | 电脑 A | `dev-pc-a` | `AGENTS.md`, `planning/session_config.json`, `planning/workflow_override.md`, `planning/progress_dashboard.md` | 用户明确授权；门禁改为非阻塞记录项，未验证状态与审计警示仍须保留 |
| 已完成 | 生成四问最终方法详解、结果分析与论文材料包 | 电脑 A | `dev-pc-a` | `methods/Q1-Q4/`, `results/Q1-Q4/reports/`, `planning/progress_dashboard.md` | 按用户禁用门禁的授权生成；全部标为未冻结写作材料，并保留各问证据边界 |
| 已完成 | 审核并整理 Q1/Q2 中文高清论文图 | 电脑 A | `dev-pc-a` | `paper/figures/`, `paper/fonts/`, `planning/progress_dashboard.md` | 筛选18张图；逐图目视复核与600 dpi PNG严格检查通过；Q2 PDF字体嵌入未在本机复验并已如实记录 |
| 已完成 | 撰写数学建模论文正文初稿 | 电脑 A | `dev-pc-a` | `paper/sections/`, `paper/main.md`, `paper/writing_summary.json`, `paper/audits/`, `planning/progress_dashboard.md` | 已形成中文第一版并整合Q4证据图；纠正鲁棒目标与价格oracle边界；Q3正式图、数字冻结和文献核验列为后续项 |
| 已完成 | 整合Q4高清图与复现证据完善论文 | 电脑 A | `dev-pc-a` | `paper/figures/Q4/`, `paper/sections/complete_first_draft.md`, `paper/audits/`, `planning/progress_dashboard.md` | 从34图中筛选7张正文图；19个正文图片链接全部存在；Q4 PNG均为600 dpi；完整复验脚本因本机缺少可选依赖pypdf未重跑，沿用包内PASS_WITH_SOURCE_LIMITATION并保留PDF字体警示 |
| 已完成 | 生成论文正文 Word 版 | 电脑 A | `dev-pc-a` | `paper/光储微电网多时间尺度协调调度论文正文.docx` | 已转换正文、表格和19张配图；以本机 Word 导出并逐页目视检查26页，已去除标题装饰线与原稿“待插图”空白页 |
| 已完成 | 展开方案名称并补齐 Q3 正式图 | 电脑 A | `dev-pc-a` | `paper/sections/complete_first_draft.md`, `paper/figures/Q1-Q4/`, `paper/光储微电网多时间尺度协调调度论文正文.docx` | 正文、表格及正文采用图不再使用M1/M2/M3代号；新增7张Q3中文600 dpi图；Word扩展为30页并完成逐页视觉检查 |
| 已完成 | 按竞赛评审意见完善论文（公式排版除外） | 电脑 A | `dev-pc-a` | `paper/`, `robustness/`, `planning/`, `src/analysis/`, `tests/` | 已分离PoC与正式结果、补充7条引用和配对时间稳定性证据、冻结数字、重建25页Word；22项测试通过 |
| 已完成 | 完成问题 1 确定性优化与 `result1.xlsx` | 电脑 A | `dev-pc-a` | `src/Q1/`, `results/Q1/`, `output/result1.xlsx` | M2费用35126.95元；互斥审计与DP网格收敛通过 |
| 待审核 | 完成问题 2 全年日前优化与 `result2.xlsx` | 电脑 A | `dev-pc-a` | `src/Q2/`, `results/Q2/`, `output/result2.xlsx` | M3首轮总费用与紧急购电均优于M1/M2；待稳健性实验 |
| 待审核 | 完成问题 3 滚动调整与 `result3.xlsx` | 电脑 A | `dev-pc-a` | `src/Q3/`, `results/Q3/`, `robustness/Q3/`, `output/result3.xlsx` | 建模者已选择0.99并完成round2；紧急购电较M1下降17.50%、费用增加3.58%；稳定性理由与置信度仍待人工填写 |
| 待审核 | 完成问题 4 波动电价重算 | 电脑 A | `dev-pc-a` | `src/Q4/`, `results/Q4/`, `output/result4-2.xlsx`, `output/result4-3.xlsx` | Q4-3已继承0.99完成round2；M3未来价格泄漏0；待Q3稳定性判定后冻结 |
| 待认领 | 撰写论文并验证结果、图表和文件大小 | — | — | `docs/`, `tests/`, `output/` | 对照题面逐项验收 |

状态使用：`待认领`、`进行中`、`待审核`、`已完成`、`阻塞`。

建议分工：电脑 A 负责统一模型、求解器和问题 1/2；电脑 B 负责数据检查、问题 3/4、结果复核与论文材料。发生文件重叠时，以任务认领记录为准。
