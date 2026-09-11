# MathModeling-skills 项目级接入说明

本项目从 `D:\MathModeling-skills` 接入数学建模辅助技能，仅对当前仓库生效。

## 接入内容

- `.codex/skills/`：28 个 Codex 技能，共 31 个文件。
- `docs/math-modeling-skills/upstream-AGENTS.md`：上游完整流程与质量门禁规则。
- `docs/math-modeling-skills/skills-docs/`：方法选择、论文写作、图表和质量检查参考资料。
- `docs/math-modeling-skills/templates/`：问题解析、方法计划、图表计划和质量报告模板。
- `docs/math-modeling-skills/implementation-targets.md`：实现目标说明。
- `docs/math-modeling-skills/matlab-beita-tianyuan-guidelines.md`：MATLAB/北太天元兼容说明。

## 来源版本

- 源目录：`D:\MathModeling-skills`
- 源提交：`f9547d4d216e123f83483227c54d1591b455b811`
- 接入日期：2026-09-11

这些文件采用快照复制方式接入，不依赖 `D:` 盘运行，因此仓库在另一台电脑上也能使用相同版本。

## 使用与优先级

重新打开本项目或启动新的 Codex 会话后，Codex 应能自动发现 `.codex/skills/` 中的技能。可以直接点名，例如：

- “使用 `problem-parser` 解析题目。”
- “使用 `data-auditor-cleaner` 检查附件数据。”
- “使用 `workflow-orchestrator` 判断下一步。”

本项目根目录 `AGENTS.md` 中的双电脑协作和目录兼容规则优先。上游文档中的目录名是通用示例，不应直接覆盖本项目已有结构。

## 更新方法

上游更新后，先查看差异，再同步 `.codex/skills/` 和本目录中的支持文件。更新时同时修改本文件记录的源提交，并验证所有技能的 YAML 头信息和引用文件。
