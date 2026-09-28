# 首先要明确累计收益的数学公式
# 从日收益率入手，就是前一天的价格 乘以 这一天的日收益率，就是今天的累计收益
from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt

cumulative_return = []  # 我现在最熟悉list，就先用list来写
# 第一天的累计收益是什么
# 第一天的累计收益就是1
# 先导入收盘价
# 不对不对，我是顺着日收益率的逻辑来的，意味着我必须先将日收益率算出来
# 回到日收益率的部分，在最后面加上累计收益的计算即可
code = "sh600519"
adjust = "qfq"
start_date = "20240101"
csv_path = Path(__file__).with_name(f"{code}_{adjust}_{start_date}.csv")
df = pd.read_csv(csv_path)
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date")

cumulative_return.append(1)
print(cumulative_return[0])

