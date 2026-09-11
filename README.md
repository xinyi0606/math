# Math

2026 年高教社杯全国大学生数学建模竞赛 C 题“微网与外部电网电力调控策略”的协作项目，适合两台电脑上的 Codex 共同维护。

## 核心目标

在负荷、光伏出力、电价和预测不断变化的条件下，建立包含储能约束的微网购电优化模型，完成问题 1-4，并生成竞赛指定的 5 个 Excel 结果文件。题目摘要见 [`docs/problem-definition.md`](docs/problem-definition.md)，正式结构化解析见 [`planning/parse/problem_parse.md`](planning/parse/problem_parse.md)。

主要参考文献及其在本题中的采用边界见 [`docs/literature-notes.md`](docs/literature-notes.md)。

附件结构、字段、单位和审计结论见 [`docs/data-dictionary.md`](docs/data-dictionary.md) 与 [`data/data_report.md`](data/data_report.md)。

## 项目结构

```text
math/
├── data/
│   ├── raw/       # 竞赛原始附件，保持只读
│   └── templates/ # 官方结果工作簿模板
├── docs/          # 题目说明、推导与设计文档
├── notebooks/     # 探索性计算与笔记本
├── src/           # 可复用的实现
├── tests/         # 自动化测试
├── AGENTS.md      # 两台 Codex 共用的工作规则
└── TASKS.md       # 协作任务看板
```

## 开始协作

1. 在 GitHub 或 GitLab 新建一个空的私有仓库。
2. 在本机为该仓库设置远程地址并推送 `main`。
3. 电脑 B 从远程仓库克隆项目。
4. 两台电脑分别使用 `dev-pc-a` 和 `dev-pc-b` 分支工作。
5. 每项任务开始前在 `TASKS.md` 认领，完成后通过合并请求进入 `main`。

## 基本约定

- 数学结论应在 `docs/` 中写明假设、符号和推导。
- 可复用计算放在 `src/`，并在 `tests/` 中加入验证。
- 大型数据、密钥、缓存和本地环境文件不进入 Git。
- 一次提交只处理一个明确任务，提交信息说明“做了什么”。
- 所有能量统一使用 kWh，功率统一使用 kW，时间步长显式换算为小时。
- 最终模型文件与结果文件均不得超过 5 MB。
