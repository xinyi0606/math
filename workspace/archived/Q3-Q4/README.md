# 外部上传冻结文件归档说明

`uploaded_frozen_numbers_UNVERIFIED.json` 是2026-09-12从仓库根目录收到的外部上传文件，保留其原始字节用于追溯，但它不是本项目的规范 `frozen_numbers.json`，不得作为论文数字源。

归档原因：

1. 文件标记 `status=FROZEN`，但同批 `uploaded_stability_assessment.md` 明确写明结果冻结 `NOT_RUN`。
2. Q3参数决定文件尚缺人工理由，稳定性置信度与结果判定仍为PENDING，G4.5未通过。
3. 文件记录的 `output/result3.xlsx` 与 `output/result4-3.xlsx` 哈希，分别为 `6cbc8a...`、`5b1714...`；当前经17项测试通过的工作簿哈希分别为 `4fdff1...`、`bb4b4a...`，二者不一致。
4. 项目规则禁止手工修订冻结快照，因此选择原样归档，而不是修改其内容。

待人工门禁通过后，应由 `solution-package-builder` 从规范round2指标重新生成真正的 `results/Qx/reports/frozen_numbers.json`。
