# 先把思路写下来，不写下来我都无法连续思考了，唉
# 要算日收益率，需要得到连续两天的数据，那么可以用iloc将series里的连续两天价格取出来
# 要以什么形式输出呢，应该是新增一列，这一列就是日收益率，用df的新增列即可
# 差不多了，数学原理基本是一眼可知，重要的是用代码写出来
from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt

# 第一步，取数，直接从缓存里取
code = "sh600519"
adjust = "qfq"
start_date = "20240101"
csv_path = Path(__file__).with_name(f"{code}_{adjust}_{start_date}.csv")
df = pd.read_csv(csv_path)
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date")
# 加了排序
# df = df.sort_values('date', ascending=True)
# 第二步，再理理，我用close来算，要将close的连续两天价格取出来,daily_return要是一个series才行
# 用循环一个一个去算
daily_return = []
for i in range(len(df["close"])):
    daily_return_rate = df["close"].iloc[i]/df["close"].iloc[i-1]-1
    daily_return.append(daily_return_rate)
print(daily_return)

daily_return_series = pd.Series(daily_return, index=df.index)
print(daily_return_series.head())

# 然后加到df上去，这里好像只是按行数匹配的，df读出来也是按行数取的，所以我应该规范的话，在最前面应该加一个按日期排序
df["daily_return"] = daily_return_series
print(df["daily_return"].head())

# 另外的方法，更简便一些
daily_return = df["close"].pct_change()
df["daily_return"] = daily_return
print(df["daily_return"].head())

# 两种算法算出来不对，是哪里错了
# 第一天的数据错了，第一种方法本来前一天没有数据，它把最后一天当成第一天的前一天了，所以会出现数据，而不是直接nan

# 还有画出来的一步
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df["daily_return"])
ax.set_title("daily_return")
fig.savefig(Path(__file__).with_name("daily_return.png"))
plt.show()







