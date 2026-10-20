import pandas as pd
import akshare as ak
import datetime
from pathlib import Path


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
    for w in windows:
        df1[f'ma{w}'] = ma(df, w)
    return df1


result_sh600519 = get_ma("sh600519", "qfq", "20240101")
print(result_sh600519.tail())

result_sz000001 = get_ma("sz000001", "qfq", "20240101")
print(result_sz000001.tail())

result_sh601318 = get_ma("sh601318", "qfq", "20240101")
print(result_sh601318.tail())

s_sh600519 = (result_sh600519["ma5"] > result_sh600519["ma20"]).astype(int)    # 状态

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

print(s_sh600519.tail())
print(diff_series.tail())
print(cross_sh600519.tail())
print(s_sh600519.isna().sum())
print(s_sh600519.first_valid_index())
print(diff_series.isna().sum())
print(diff_series.first_valid_index())
print(cross_sh600519.isna().sum())
print(cross_sh600519.first_valid_index())