import pandas as pd
import akshare as ak
import datetime

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
    return df


def ma(df,n):
    return df['close'].rolling(window=n).mean()


def get_ma(code):
    df = get_df(code)
    ma5 = ma(5,df)
    ma20 = ma(20,df)
    ma60 = ma(60,df)

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