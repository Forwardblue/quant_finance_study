import pandas as pd
import akshare as ak
import datetime
from pathlib import Path
# 假设股票代码是code


def get_df(code):
    df = ak.stock_zh_a_daily(
        symbol=code,  # 必须带 sh / sz 前缀
        start_date="20240101",
        end_date=datetime.date.today().isoformat(),
        adjust="qfq",
    )
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    csv_path = Path(__file__).with_name("sh600519_qfq.csv")
    df.to_csv(csv_path, index=False)
    print(f"{code}本地缓存成功")
    return df


def ma(df, n):
    return df['close'].rolling(window=n).mean()


def get_ma(code):
    df = get_df(code)
    ma5 = ma(df, 5)
    ma20 = ma(df, 20)
    ma60 = ma(df, 60)

    df1 = pd.DataFrame({
        'close': df['close'],
        'ma5': ma5,
        'ma20': ma20,
        'ma60': ma60,
    })

    return df1


result = get_ma("sh600519")
print(result.tail())

result = get_ma("sz000001")
print(result.tail())

result = get_ma("sh601318")
print(result.tail())
