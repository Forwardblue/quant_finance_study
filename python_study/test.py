import pandas as pd
import akshare as ak
import datetime
from pathlib import Path

from matplotlib import pyplot as plt


# 假设股票代码是code，采取adjust复权方式，开始日期start_date


def get_df(code, adjust="qfq", start_date="20240101"):  # 注意这个函数的前后逻辑，将日期设定为索引后，一定要将其保留下来，不然后续读不到日期。重新读取缓存后，还是要重新设定一遍日期作为索引
    csv_path = Path(__file__).with_name(f"{code}_{adjust}_{start_date}.csv")
    today = datetime.date.today()
    print(f"今天是{today}")
    cal = ak.tool_trade_date_hist_sina()["trade_date"]
    cal_trade = cal[cal <= today]
    trade_data_date = cal_trade.iloc[-2]
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        last_date = df.index.max().date()
        if last_date >= trade_data_date:
            print(f"数据已经是最新的")
            print(f"读取成功")
            return df
        else:
            print(f"重新取数据")

    df = ak.stock_zh_a_daily(
        symbol=code,  # 必须带 sh / sz 前缀
        start_date=start_date,
        end_date=datetime.date.today().isoformat(),
        adjust=adjust,
    )
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    df.to_csv(csv_path, index=True)   # 注意这里为什么要设定index = True，因为不设定的话，日期作为索引是无法保存在csv里的
    print(f"数据缓存成功")
    return df


def ma(df, n):
    return df['close'].rolling(window=n).mean()


def get_ma(code, adjust="qfq", start_date="20240101"):
    df = get_df(code, adjust, start_date)
    windows = [5, 20, 60]
    df1 = pd.DataFrame({'close': df['close']})
    df = get_df(code, adjust, start_date)
    df["daily_return"] = df["close"].pct_change()
    df["nav"] = (1 + df['daily_return'].fillna(0)).cumprod()
    for w in windows:
        df1[f'ma{w}'] = ma(df, w)
    return df1

# 加一列daily_return和一列累计收益率
def get_daily_return(code, adjust="qfq", start_date="20240101"):
    df = get_df(code, adjust, start_date)
    df["daily_return"] = df["close"].pct_change()
    df["nav"] = (1 + df['daily_return'].fillna(0)).cumprod()
    return df




result_sh600519 = get_ma("sh600519", "qfq", "20240101")
print(result_sh600519.tail())
result_sh600519 = get_daily_return("sh600519", "qfq", "20240101")
print(result_sh600519.tail())
# result_sz000001 = get_ma("sz000001", "qfq", "20240101")
# print(result_sz000001.tail())
#
# result_sh601318 = get_ma("sh601318", "qfq", "20240101")
# print(result_sh601318.tail())

# 第一个"全部都有值"的日期
cols = ["ma5", "ma20"]
start = result_sh600519[cols].dropna().index[0]
result_sh600519_start = result_sh600519.loc[start:]


s_sh600519 = (result_sh600519_start["ma5"] > result_sh600519_start["ma20"]).astype(int)    # 状态
# 这里计算的是两列之间的状态，如果ma5大于ma20，则新产生的这列状态就是1
# 涉及到的问题是预热期可能会出现ma20第一天有数据，这天正好ma5大于ma20，那这一天其实不算金叉，需要将其隔离出来
# 如何隔离呢，应该是将预热期结束的第一天忽略掉，也就是照常计算金叉和死叉，但不显示为金叉和死叉
# 预热期结束应该只会有错误的金叉，不存在出现死叉的情况
# 在计算金叉和死叉的时候直接将预热期切掉，说这么多，主要是在考虑在代码的哪一步进行切除
# 在比大小的时候就切
# 下面才开始计算这列状态的变化情况，即一阶差分

# 以下是两种办法，第一种是底层逻辑，第二种是直接写
# 第一种
diff = []
for i in range(len(s_sh600519)):
    if i == 0:
        diff.append(None)
    else:
        diff.append(s_sh600519.iloc[i] - s_sh600519.iloc[i - 1])

diff_series = pd.Series(diff, index=s_sh600519.index)
# 第二种
cross_sh600519 = s_sh600519.diff()                            # 事件

# 自此，这里就完成了对金叉死叉的计算，接下来是画图
# fig, ax = plt.subplots(figsize=(10, 6))
# ax.plot(result_sh600519_start['close'], label='Close Price', color='blue')
#
# ax.plot(result_sh600519_start["ma5"], label="MA5", linewidth=1)
# ax.plot(result_sh600519_start["ma20"], label="MA20", linewidth=1)
#
# golden_cross_idx = result_sh600519_start[cross_sh600519 == 1].index   # 金叉时间点
# death_cross_idx = result_sh600519_start[cross_sh600519 == -1].index   # 死叉时间点
#
# ax.scatter(golden_cross_idx, result_sh600519_start['close'].loc[golden_cross_idx],
#            marker='^', s=100, color='green', label='Golden Cross', zorder=5)
# ax.scatter(death_cross_idx, result_sh600519_start['close'].loc[death_cross_idx],
#            marker='v', s=100, color='red', label='Death Cross', zorder=5)
# ax.set_title("result_sh600519_cross")
# ax.legend()
# fig.savefig(Path(__file__).with_name("result_sh600519_cross.png"))
# plt.show()
# plt.close(fig)

# 首先统计金叉出现次数，result_sh600519_start[cross_sh600519 == 1]
cross_count = result_sh600519_start['cross_sh600519'].value_counts()
print(cross_count)
# 计算每次金叉后 5 日、10 日的平均收益
# 把金叉的日期选出来 ：golden_cross_idx(画图的时候已经选出来了)

# print(s_sh600519.tail())
# print(diff_series.tail())
# print(cross_sh600519.tail())
# print(s_sh600519.isna().sum())
# print(s_sh600519.first_valid_index())
# print(diff_series.isna().sum())
# print(diff_series.first_valid_index())
# print(cross_sh600519.isna().sum())
# print(cross_sh600519.first_valid_index())