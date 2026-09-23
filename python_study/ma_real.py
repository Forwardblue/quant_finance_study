import pandas as pd
from pathlib import Path

from matplotlib import pyplot as plt

csv_path = Path(__file__).with_name('sh600519_qfq.csv')
df = pd.read_csv(csv_path)

print(df['close'].head())

df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')

ma5 = df['close'].rolling(window=5).mean()
ma20 = df['close'].rolling(window=20).mean()
ma60 = df['close'].rolling(window=60).mean()

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(df['close'], label='close')
ax.plot(ma5, label='ma5')
ax.plot(ma20, label='ma20')
ax.plot(ma60, label='ma60')

ax.legend()
ax.set_title("real_prices")

fig.savefig(Path(__file__).with_name("ma_real.png"))
plt.show()
# 发现横坐标轴不是日期
print(ma5.head())
# 原来是索引没整好,少了一步把日期作为整个df的索引
# df = df.set_index('date')把这个补到前面去

