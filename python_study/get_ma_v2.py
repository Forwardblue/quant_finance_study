import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
from indicators import get_df, get_ma

print("\n===== 取数结果（get_ma 的返回值，最后 5 行）=====")

result_sh600519 = get_ma("sh600519", "qfq", "20240101")
print("[sh600519 贵州茅台]")
print(result_sh600519.tail())

result_sz000001 = get_ma("sz000001", "qfq", "20240101")
print("[sz000001 平安银行]")
print(result_sz000001.tail())

result_sh601318 = get_ma("sh601318", "qfq", "20240101")
print("[sh601318 中国平安]")
print(result_sh601318.tail())

# 第一个"全部都有值"的日期
cols_ma20 = ["ma5", "ma20"] # 加了后缀 20 ，指明这里的全部都有值的日期是按照ma20来计算的
start = result_sh600519[cols_ma20].dropna().index[0]
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
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(result_sh600519_start['close'], label='Close Price', color='blue')

ax.plot(result_sh600519_start["ma5"], label="MA5", linewidth=1)
ax.plot(result_sh600519_start["ma20"], label="MA20", linewidth=1)

golden_cross_idx = result_sh600519_start[cross_sh600519 == 1].index   # 金叉时间点
death_cross_idx = result_sh600519_start[cross_sh600519 == -1].index   # 死叉时间点

ax.scatter(golden_cross_idx, result_sh600519_start['close'].loc[golden_cross_idx],
           marker='^', s=100, color='green', label='Golden Cross', zorder=5)
ax.scatter(death_cross_idx, result_sh600519_start['close'].loc[death_cross_idx],
           marker='v', s=100, color='red', label='Death Cross', zorder=5)
ax.set_title("result_sh600519_cross")
ax.legend()
fig.savefig(Path(__file__).with_name("result_sh600519_cross.png"))
plt.show()
plt.close(fig)

# 首先统计金叉出现次数，result_sh600519_start[cross_sh600519 == 1]
result_sh600519_start["cross"] = cross_sh600519 # 新增几列我需要的数据
result_sh600519_start["fwd5"] = result_sh600519_start["close"].shift(-5) / result_sh600519_start["close"] - 1
result_sh600519_start["fwd10"] = result_sh600519_start["close"].shift(-10) / result_sh600519_start["close"] - 1

# 计算每次金叉后 5 日、10 日的平均收益
# 把金叉的日期选出来 ：golden_cross_idx(画图的时候已经选出来了)

print("\n===== Day 20：金叉之后到底涨不涨 =====")
print(f"切点（预热期结束的第一天）: {start.date()}")
print(f"切完之后的行数            : {len(result_sh600519_start)}")
print("事件分布（1=金叉，-1=死叉，0=没穿越；NaN 不计数）:")
print(result_sh600519_start["cross"].value_counts())
print(f"金叉后 5 个交易日的平均收益 : {result_sh600519_start.loc[result_sh600519_start['cross'] == 1, 'fwd5'].mean():.6f}")
print(f"金叉后 10 个交易日的平均收益: {result_sh600519_start.loc[result_sh600519_start['cross'] == 1, 'fwd10'].mean():.6f}")

print("\n===== 校验 1：状态列 s（1 = ma5 在 ma20 上方，0 = 下方）=====")
print(f"NaN 个数（有多少行算不出来）: {s_sh600519.isna().sum()}")
print(f"第一个有值的日期            : {s_sh600519.first_valid_index()}")
print("最后 5 行:")
print(s_sh600519.tail())

print("\n===== 校验 2：事件列 A（手写循环版本）=====")
print(f"NaN 个数（第一行没有前一天）: {diff_series.isna().sum()}")
print(f"第一个有值的日期            : {diff_series.first_valid_index()}")
print("最后 5 行:")
print(diff_series.tail())

print("\n===== 校验 3：事件列 B（s.diff() 版本）=====")
print(f"NaN 个数（第一行没有前一天）: {cross_sh600519.isna().sum()}")
print(f"第一个有值的日期            : {cross_sh600519.first_valid_index()}")
print("最后 5 行:")
print(cross_sh600519.tail())

print(f"基线（所有 5 日窗口）平均收益: {result_sh600519_start['fwd5'].mean():.6f}")