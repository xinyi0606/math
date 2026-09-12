# Q4正式实验

运行：

```bash
python -m src.Q4.run_q4 --round-number 2 --reserve-alpha 0.99
```

Q4只替换价格输入。M1为无储能基线；M2使用当天完整真实价格，输出只解释为完全信息oracle；M3在00:00使用此前历史价格日，在06/12/18时仅以已经实现的当天价格前缀筛选历史情景，未来真实价格不进入优化。

脚本分别生成Q4-2与Q4-3回放；round2中Q4-3继承Q3选定的0.99安全裕度。官方输出为 `output/result4-2.xlsx` 和 `output/result4-3.xlsx`。情景法实际结算费用、最坏日、紧急购电和相对oracle机会损失可从 `results/Q4/experiments/round2/` 复核。
