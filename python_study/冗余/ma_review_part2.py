import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

rng = np.random.default_rng(seed=42)


# 随机行走的价格展开逻辑
steps = rng.normal(loc=0, scale=1, size=500)
steps[0] = 0

cumulative = []
totals = 0

for i in steps:
    totals += i
    cumulative.append(totals)


prices = pd.Series(
    (100+np.array(cumulative)).round(2),
    index=pd.date_range('1/1/2025', periods=500, freq='D'),
    name='prices'
)

print(prices.head())

cumulative2 = np.cumsum(steps)

prices2 = pd.Series(
    (100+np.array(cumulative2)).round(2),
    index=pd.date_range('1/1/2025', periods=500, freq='D'),
    name='prices'
)

print('随机行走的两种方法结果是否相等：',prices.equals(prices2))

# sma的逻辑展开
sma = prices.rolling(window=5, min_periods=1).mean().round(2)

# 现在是prices已经解决，目的是要展开滚动窗口的算法，选取最近五个周期的价格，加和平均，就可以得到sma5
manual = []
for s in range(len(prices)):
    manual.append(prices.iloc[max(0,s-4):s+1].mean())

# 目前manual还只是列表，要转成和prices一样的格式
sma2 = pd.Series(manual, index=prices.index).round(2)
print('sma5的两种方法结果是否相等：',np.allclose(sma2,sma))  # 记得四舍五入，而且要用allclose，不然很难得到TRUE
