import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
from indicators import get_df, get_ma
import numpy as np


# 设置中文字体（SimHei 黑体，Windows 自带）
plt.rcParams['font.sans-serif'] = ['SimHei']
# 解决负号显示异常的问题
plt.rcParams['axes.unicode_minus'] = False


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

plt.close(fig)

# 首先统计金叉出现次数，result_sh600519_start[cross_sh600519 == 1]
result_sh600519_start["cross"] = cross_sh600519 # 新增几列我需要的数据
result_sh600519_start["fwd5"] = result_sh600519_start["close"].shift(-5) / result_sh600519_start["close"] - 1
result_sh600519_start["fwd10"] = result_sh600519_start["close"].shift(-10) / result_sh600519_start["close"] - 1
result_sh600519_start["s"] = s_sh600519
result_sh600519_start["pos"] = s_sh600519.shift(1)

print(result_sh600519_start[["close", "ma5", "ma20", "s", "cross", "pos"]].loc["2024-02-05":"2024-02-09"])
print(result_sh600519_start[["close", "ma5", "ma20", "s", "cross", "pos"]].head(5))
print(result_sh600519_start[["close", "ma5", "ma20", "s", "cross", "pos"]].tail(5))
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

result_sh600519_start["pos"]=result_sh600519_start["pos"].fillna(0)      # "策略启动前空仓" ← 建议这个
# Day 23：策略每日收益 = 仓位 × 当天涨跌
result_sh600519_start["strat_ret"] = result_sh600519_start["pos"] * result_sh600519_start["daily_return"]
print(result_sh600519_start[["daily_return", "pos", "strat_ret"]].head(8))
print(f"策略收益为 0 的天数: {(result_sh600519_start['strat_ret'] == 0).sum()} / {len(result_sh600519_start)}")
print(f"空仓天数: {(result_sh600519_start['pos'] == 0).sum()}")


n = len(result_sh600519_start)      # → 677，是去除了预热期的，后续要保持一致
total = (1 + result_sh600519_start["strat_ret"]).prod() - 1  # 策略利润率
annual = (1 + total) ** (252 / n) - 1 # 策略年化收益率
bh_total = (1 + result_sh600519_start["daily_return"]).prod() - 1  # 保持持仓不变利润率
bh_annual = (1 + bh_total) ** (252 / n) - 1 # 保持持仓不变年化收益率

print(f"区间: {result_sh600519_start.index[0].date()} ~ {result_sh600519_start.index[-1].date()}  ({n} 个交易日, {n/252:.2f} 年)")
print(f"策略总收益    : {total:+.4f}  ({total*100:+.2f}%)")
print(f"策略年化      : {annual:+.4f}  ({annual*100:+.2f}%)")
print(f"买入持有总收益: {bh_total:+.4f}  ({bh_total*100:+.2f}%)")
print(f"买入持有年化  : {bh_annual:+.4f}  ({bh_annual*100:+.2f}%)")

nav = (1 + result_sh600519_start["strat_ret"]).cumprod()  #一块钱买入，每天该策略挣了多少钱，之前还是把这个当成一个数了，而不是一列数。
dd  = nav / nav.cummax() - 1 # 最后的收益和策略最高点的比较，减1是为了把倍数换成涨跌幅。
print(f"策略最大回撤：{dd.min():+.4f}") # nav是一列数，dd也是一列数，一开始还以为是一个数。看到min（）才反应过来。这一步是为了看回撤，就是看自己到底会掉多深的坑。

print(f"策略最大回撤日期：{dd.idxmin().date()}")                        # 谷底是哪天
print(f"策略回撤前挣得最多的那一天：{nav.loc[:dd.idxmin()].idxmax().date()}")     # 谷底之前的最高点（山顶）是哪天

nav_bh = (1 + result_sh600519_start["daily_return"]).cumprod()
dd_bh  = nav_bh / nav_bh.cummax() - 1
print(f"保持买入的最大回撤：{dd_bh.min():+.4f}") # 上面这三行是为了和买入持有做对比，是在计算保持买入的值。

dd.plot()
plt.savefig(Path(__file__).with_name("drawdown.png"))
plt.close()

# 取出所有金叉日、死叉日
golden = list(result_sh600519_start.index[result_sh600519_start["cross"] == 1])
death  = list(result_sh600519_start.index[result_sh600519_start["cross"] == -1])

# 每个金叉配它之后最近的死叉（没有就跳过 = 未平仓）
trades = []
for g in golden:
    after = [d for d in death if d > g]
    if after:
        trades.append(result_sh600519_start['close'][after[0]] / result_sh600519_start['close'][g] - 1)

wins   = [x for x in trades if x > 0]
losses = [x for x in trades if x <= 0]
wins_rate= len(wins) / len(trades)
Profit_Loss_Ratio= np.mean(wins) / abs(np.mean(losses))

print("\n===== Day 26：胜率与盈亏比 =====")
print(f"金叉 {len(golden)} 次，死叉 {len(death)} 次 → 配成 {len(trades)} 笔已平仓（未平仓 {len(golden) - len(trades)} 笔，不计入统计）")
print(f"胜率      : {len(wins)} / {len(trades)} = {wins_rate:.2%}")
print(f"平均盈利  : {np.mean(wins):+.4%}   （赢的 {len(wins)} 笔）")
print(f"平均亏损  : {np.mean(losses):+.4%}   （输的 {len(losses)} 笔）")
print(f"盈亏比    : {Profit_Loss_Ratio:.3f}   ← 平均盈利 / 平均亏损")
print(f"每笔期望  : {wins_rate * np.mean(wins) + (1 - wins_rate) * np.mean(losses):+.4%}   ← 胜率×平均盈利 + (1-胜率)×平均亏损")
print(f"盈利因子  : {sum(wins) / abs(sum(losses)):.3f}   ← 总盈利 / 总亏损（另一个指标，别和盈亏比混）")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(nav,    label="MA5/MA20 择时")
ax.plot(nav_bh, label="买入持有")
ax.set_title("策略 vs 买入持有（净值，起点 1.0）")
ax.legend()
fig.savefig(Path(__file__).with_name("nav_compare.png"))
plt.close(fig)

print(f"策略最高   {nav.max():.4f} @ {nav.idxmax().date()}")
print(f"买入持有最高 {nav_bh.max():.4f} @ {nav_bh.idxmax().date()}")
ratio = nav / nav_bh      # >1 = 策略领先，<1 = 策略落后
print(f"策略相对最强 {ratio.max():.3f} @ {ratio.idxmax().date()}")
print(f"策略相对最弱 {ratio.min():.3f} @ {ratio.idxmin().date()}")


cost = result_sh600519_start["pos"].diff().abs().fillna(0) * 0.001   # 第一行没有"前一天"，成本按 0 算
result_sh600519_start["strat_ret_cost"] = result_sh600519_start["pos"] * result_sh600519_start["daily_return"] - cost

print("\n===== Day 28：加入交易成本（每次买卖扣 0.1%）=====")
print(f"换手次数            : {int((cost > 0).sum())} 次（每次 0.1%）")
print(f"成本累计（算术和）  : {cost.sum():.4%}")
print(f"无成本总收益        : {(1 + result_sh600519_start['strat_ret']).prod() - 1:+.2%}")
print(f"有成本总收益        : {(1 + result_sh600519_start['strat_ret_cost']).prod() - 1:+.2%}")
print(f"成本吃掉            : {((1 + result_sh600519_start['strat_ret']).prod() - 1) - ((1 + result_sh600519_start['strat_ret_cost']).prod() - 1):.2%}   ← 净值上的实际差额，不是简单的 4.5%")

