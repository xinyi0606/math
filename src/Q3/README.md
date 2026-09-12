# Q3正式实验

运行：

```bash
python -m src.Q3.run_q3 --round-number 2 --reserve-alpha 0.99
```

脚本复用Q2-M3的日前净负荷预测，并比较M1只用00:00预测、M2四时点确定性滚动、M3四时点99%分位安全裕度滚动。每次更新冻结已执行前缀，调整后的总购电只与00:00计划比较一次。round1保留原0.90参数结果，round2按建模者选择使用0.99。

官方输出为 `output/result3.xlsx`。round2的主方法完整调度、全年逐日费用分解和方法比较保存在 `results/Q3/experiments/round2/`。
