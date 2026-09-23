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


# 在真实数据上读取ma5、ma20ma60
# 这里遇到一个问题，我一开始想用df[['date', 'open']]进行滚动，但是rolling之前学习的方式是用series进行滚动
# 所以想先转换格式，但ai告诉我不用，直接取一列就行，但是我不知道这一列的索引是不是日期啊，现在就要确定open的索引是不是日期
print(df['open'].index)
print(df['open'].head())
# 可从输出结果上知，open的索引并不是日期，那么现在就需要将其索引更换成日期
# 从前面的学习得知，我是将csv的内容读取进来的，那么读取的日期就不会是日期格式
# 先将日期从文本格式转成日期格式
df['date'] = pd.to_datetime(df['date'])
# 再将日期改为整个df的索引
df = df.set_index('date')
# 检查open的索引是否更正完毕
print(df['open'].head())
# 成功更改索引
# 现在开始rolling操作

ma5 = df['open'].rolling(window = 5).mean()
ma20 = df['open'].rolling(window = 20).mean()
ma60 = df['open'].rolling(window = 60).mean()
# 检查这一步
print(ma5.tail())
print(ma20.tail())
print(ma60.tail())



