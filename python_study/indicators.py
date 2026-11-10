import pandas as pd
import akshare as ak
import datetime
from pathlib import Path

def get_df(code, adjust="qfq", start_date="20240101"):  # 注意这个函数的前后逻辑，将日期设定为索引后，一定要将其保留下来，不然后续读不到日期。重新读取缓存后，还是要重新设定一遍日期作为索引
    csv_path = Path(__file__).with_name(f"{code}_{adjust}_{start_date}.csv")
    today = datetime.date.today()
    cal = ak.tool_trade_date_hist_sina()["trade_date"]
    cal_trade = cal[cal <= today]
    trade_data_date = cal_trade.iloc[-2]
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        last_date = df.index.max().date()
        if last_date >= trade_data_date:
            return df

    df = ak.stock_zh_a_daily(
        symbol=code,  # 必须带 sh / sz 前缀
        start_date=start_date,
        end_date=datetime.date.today().isoformat(),
        adjust=adjust,
    )
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    df.to_csv(csv_path, index=True)   # 注意这里为什么要设定index = True，因为不设定的话，日期作为索引是无法保存在csv里的
    return df

def ma(df, n):
    return df['close'].rolling(window=n).mean()


def get_ma(code, adjust="qfq", start_date="20240101"):
    df = get_df(code, adjust, start_date)
    windows = [5, 20, 60]
    df1 = pd.DataFrame({'close': df['close']})
    for w in windows:
        df1[f'ma{w}'] = ma(df, w)
    df1["daily_return"] = df1["close"].pct_change()
    df1["nav"] = (1 + df1["daily_return"].fillna(0)).cumprod()
    return df1

