import pandas as pd
import akshare as ak
import datetime
from pathlib import Path
# 假设股票代码是code


def get_df(code):  # 注意这个函数的前后逻辑，将日期设定为索引后，一定要将其保留下来，不然后续读不到日期。重新读取缓存后，还是要重新设定一遍日期作为索引
    csv_path = Path(__file__).with_name(f"{code}_qfq.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        print(f"{code} 读取本地缓存")
        print("读取的列名:", df.columns.tolist())
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
    else:
        df = ak.stock_zh_a_daily(
            symbol=code,  # 必须带 sh / sz 前缀
            start_date="20240101",
            end_date=datetime.date.today().isoformat(),
            adjust="qfq",
        )
        print("akshare 返回的列名:", df.columns.tolist())
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df.to_csv(csv_path, index=True)   # 注意这里为什么要设定index = True，因为不设定的话，日期作为索引是无法保存在csv里的
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
