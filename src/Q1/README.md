# Q1正式实验

运行：

```bash
python -m src.Q1.run_q1
```

主模型为Q1-M2连续LP；M1作为无储能基线，M3只用于10分钟尺度SOC网格收敛核验。输入只读加载 `data/raw/附件1.xlsx`，正式结果写入 `results/Q1/experiments/round1/`，官方同名工作簿复制到 `output/result1.xlsx`。

若逐时互斥审计发现任何同时充放电，脚本直接失败并要求升级MILP，不会继续生成可行性结论。
