import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
# ================================================================
# 第一部分：算指标 —— 这一段每一行都要懂
# ================================================================

# 1. 造 500 个价格：算术随机游走（固定种子，保证每次运行结果一样）
#    和上一版的区别：uniform 是每天都独立抽签，价格之间毫无关系；
#    随机游走是「今天 = 昨天 + 一个随机增量」，所以价格会连着走、走出一段"趋势"。
#    但增量本身每天独立、均值为 0 —— 走出去的那段趋势纯属偶然，不是行情有方向。
#    这就是后面能说「均线不预测方向」的由来。
rng = np.random.default_rng(seed=42)
steps = rng.normal(loc=0.0, scale=1.0, size=500)   # 每日增量：均值 0、标准差 1 元
steps[0] = 0.0                                     # 第一天不动，起点正好是 100
prices = pd.Series(
    (100 + np.cumsum(steps)).round(2),             # cumsum = 逐日累加，这就是"游走"
    index=pd.date_range("2026-01-01", periods=500, freq="D"),
    name="price",
)

# 2. SMA5：滚动窗口取平均
#    min_periods=1 = 数据不够 5 个也先算；去掉它，前 4 行会变成 NaN
sma5 = prices.rolling(window=5, min_periods=1).mean().round(1)

# 3. EMA5：指数移动平均
#    adjust=False = 用递推式 EMA(t) = α·P(t) + (1-α)·EMA(t-1)，其中 α = 2/(5+1)
ema5 = prices.ewm(span=5, adjust=False).mean().round(1)

# 4. MA20 / MA60：同一个 rolling，但故意不写 min_periods
#    不写 = 用默认值 min_periods=window → 前 19 / 59 行是 NaN。
#    为什么和上面的 SMA5 不一样：窗口越长，"凑合着算"离真值越远。
#    100 个点里 MA60 只有后 41 个是真值，前 59 个要是也硬算，
#    那条线会被自己误读成"60 日均线"，其实只是"前 N 天的平均"。
sma20 = prices.rolling(window=20).mean().round(1)
sma60 = prices.rolling(window=60).mean().round(1)

# 5. 打印对比表
df = pd.DataFrame({"price": prices, "SMA5": sma5, "EMA5": ema5, "MA20": sma20, "MA60": sma60})
#    500 行不打了 —— 刷屏看不出东西。真正要盯的是尾部：
#    那是 MA5 / MA20 / MA60 全都算得出值的区间，方便直接比谁更贴价格、谁更滞后。
print(df.tail(10))

# 6. 手写循环再算一遍 EMA，和 pandas 对拍 —— 证明自己真懂 α 在干什么
#    注意：每步都拿「没取整」的值往下递推，只在最后 round。
#          每步都 round 的话，误差会顺着递推式滚雪球，就和 pandas 对不上了。
alpha = 2 / (5 + 1)
ema_manual = [prices.iloc[0]]                        # 第一天：EMA = 第一个价格
for p in prices.iloc[1:]:
    ema_manual.append(alpha * p + (1 - alpha) * ema_manual[-1])
ema_manual = pd.Series(ema_manual, index=prices.index).round(1)

print("EMA 两种算法完全一致:", ema_manual.equals(ema5))

# 7. 手写循环再累加一遍价格，和 np.cumsum 对拍 —— 同一个套路，换个地方再用一次
#    第 6 步是「一行 ewm   vs  手写递推」，这一步是「一行 cumsum  vs  手写累加」。
#    两次都在说明同一件事：库函数不是魔法，拆开就是一个循环。
#    种子和参数跟第 1 步保持一致，所以算出来必须和 prices 一模一样。
rng = np.random.default_rng(seed=42)
steps = rng.normal(loc=0.0, scale=1.0, size=500)
steps[0] = 0.0

# 手写累加，替代 np.cumsum
# 注意：和上面的 EMA 一样，循环里不 round，只在最后 round 一次。
#      中间每步取整的话，累加 500 次误差一样会滚雪球。
cumulative = []
total = 0.0
for s in steps:
    total += s
    cumulative.append(total)

# 加上初始价格 100
prices_manual = pd.Series(
    (100 + np.array(cumulative)).round(2),
    index=pd.date_range("2026-01-01", periods=500, freq="D"),
    name="price",
)

print("价格两种算法完全一致:", prices_manual.equals(prices))

# 8. 手写循环算一遍 SMA，和 pandas rolling 对拍 —— 三种「一行 vs 手写」凑齐了
#    第 6 步 ewm、第 7 步 cumsum、这一步 rolling，套路一模一样：库函数拆开就是个循环。
#    SMA 比前两个更好懂，因为它没有"递推"，就是老老实实把最近 5 个加起来除以 5。

# 手写滑动窗口：算第 i 天的 SMA5，就把 [i-4, i] 这 5 个（含当天）拿来平均。
# max(0, i-4) 这个夹逼就是 min_periods=1 的落点：
#   不够 5 个时不让起点跑到负数，直接从第 0 个开始拿 —— 前 4 天就是"有几个算几个"。
#   想要"不够就留 NaN"那版（真实窗口），把 max 去掉、改成 i < 4 时 append(np.nan) 即可。
manual_raw = []
for i in range(len(prices)):
    manual_raw.append(prices.iloc[max(0, i - 4): i + 1].mean())  # 这里的iloc遵循左闭右开，所以会取到i+1
manual_raw = pd.Series(manual_raw, index=prices.index)

# 只在最后 round 一次 —— 和第 6、7 步同一条规矩
sma5_manual = manual_raw.round(1)
sma5_raw = prices.rolling(window=5, min_periods=1).mean()   # 不取整的 pandas 版，用来对拍

print("SMA 两种算法完全一致（.equals） :", sma5_manual
      .equals(sma5))
print("SMA 两种算法完全一致（allclose）:", np.allclose(manual_raw, sma5_raw))

# ----------------------------------------------------------------
# 上面第一个是 False、第二个是 True —— 这一步别跳过，值得停下来看
# ----------------------------------------------------------------
# .equals() 比的是"一个 bit 都不能差"。两个版本在浮点上真的不同：
#   pandas 的 rolling 内部用滚动累加，手写版用切片求和 —— 累加顺序不同，
#   结果差了 1.4e-14（小数点后 14 位）。
#
# 这么点误差本来无所谓，但 2027-04-14 那天运气不好：
#   5 个价格 = 91.0, 90.54, 90.24, 92.18, 93.29，和 = 457.25，除以 5 = 91.45
#   正好卡在 round(1) 的进位边界上。差 1.4e-14 就让它从 91.4 翻成 91.5 —— 最后一位差 0.1。
#
# 所以：对比浮点结果，永远别用 == 或 .equals()，用 np.allclose
#       （它默认容忍 1e-8 的相对误差，小数点后 14 位的噪声自然被放过去）。
#
# 顺带解释第 6 步为什么能 bit 级对上：ewm 的递推式和你的循环顺序完全相同，
# 每一步的舍入都落在同一个地方。rolling 内部换了一套算法，就对不上了。

# ================================================================
# 第二部分：画图 —— 核心只有下面 5 行 plot，其它都是可删的外观
# ================================================================

fig, ax = plt.subplots(figsize=(10, 5))       # 画布大小，10×5 英寸

ax.plot(prices, label="price")                # ← 核心：把五条线画上去
ax.plot(sma5, label="SMA5")                   # 不画 marker，500 个点会糊成一片
ax.plot(ema5, label="EMA5")
ax.plot(sma20, label="MA20")
ax.plot(sma60, label="MA60")

ax.legend()                     # 图例 —— 不加就分不清哪条是哪条，别删
ax.set_title("price - SMA5 - EMA5 - MA20 - MA60")
ax.set_ylabel("price")
ax.grid(alpha=0.3)              # 淡网格，纯粹为了好看，删掉不影响结果
ax.tick_params(axis="x", rotation=45)   # 500 个日期横着排会挤，转 45 度纯属好看

fig.tight_layout()              # 别让标题被裁掉

fig.savefig(Path(__file__).with_name("ma.png"))
plt.show()                      # 弹窗显示
