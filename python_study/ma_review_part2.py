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

#sma的逻辑展开


