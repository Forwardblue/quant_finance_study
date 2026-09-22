import pandas as pd
from pathlib import Path

csv_path = Path(__file__).with_name("sh600519_qfq.csv")
df = pd.read_csv(csv_path)

# df[['date' , 'open']]执行选列操作，但不影响原来的df，相当于有一个新的dateframe
print(df[['date', 'open']].head())    # 查看我的选列操作是否正确
print(df[['date', 'high']].tail())    # 试一下tail操作

print(df.dtypes)    # 查看我的df列的类型，以免筛选出现字符不匹配的问题
print(type(df['date']))   # 这里的df['date']是选取一列形成了pandas.Series，
print(type(df[['date' , 'open']]))  # 而df[['date' , 'open']]是形成了一个pandas.DataFrame

print(df[['date']].head())    # 查看日期格式，准备执行日期筛选

# df[df['date'] > '2026-01-01']和上面做对比，取行和取列的对比

# 筛选出日期大于2026-01-01的行并降序
print(df[df['date'] > '2026-01-01'].sort_values('date', ascending=False).head())

# 筛选出日期大于2026-01-01且开盘价大于1300的行并降序
print(df[(df['date'] > '2026-01-01') & (df['open'] > 1300.00)].sort_values('date',ascending=False).head())

# df.describe() 对数值列进行整体的描述
print(df.describe())