import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
# ================================================================
# 第一部分：算指标 —— 这一段每一行都要懂
# ================================================================

# 1. 造 100 个价格（固定种子，保证每次运行结果一样）
rng = np.random.default_rng(seed=42)
prices = pd.Series(
    rng.uniform(90, 110, size=100).round(2),         # 90~110 之间取 100 个数
    index=pd.date_range("2026-01-01", periods=100, freq="D"),
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
#    100 行超过了 pandas 默认的显示上限（60 行），不设这一句，中间会被折叠成 "..."。
#    设成 None = 不限行数，全打出来。
pd.set_option("display.max_rows", None)
print(df)

# 6. 手写循环再算一遍 EMA，和 pandas 对拍 —— 证明自己真懂 α 在干什么
#    注意：每步都拿「没取整」的值往下递推，只在最后 round。
#          每步都 round 的话，误差会顺着递推式滚雪球，就和 pandas 对不上了。
alpha = 2 / (5 + 1)
ema_manual = [prices.iloc[0]]                        # 第一天：EMA = 第一个价格
for p in prices.iloc[1:]:
    ema_manual.append(alpha * p + (1 - alpha) * ema_manual[-1])
ema_manual = pd.Series(ema_manual, index=prices.index).round(1)

print("两种算法完全一致:", ema_manual.equals(ema5))

# ================================================================
# 第二部分：画图 —— 核心只有下面 3 行 plot，其它都是可删的外观
# ================================================================

fig, ax = plt.subplots(figsize=(10, 5))       # 画布大小，10×5 英寸

ax.plot(prices, label="price")                # ← 核心：把五条线画上去
ax.plot(sma5, label="SMA5")                   #    100 个点不画 marker，不然圆圈糊成一片
ax.plot(ema5, label="EMA5")
ax.plot(sma20, label="MA20")
ax.plot(sma60, label="MA60")

ax.legend()                     # 图例 —— 不加就分不清哪条是哪条，别删
ax.set_title("price - SMA5 - EMA5 - MA20 - MA60")
ax.set_ylabel("price")
ax.grid(alpha=0.3)              # 淡网格，纯粹为了好看，删掉不影响结果
ax.tick_params(axis="x", rotation=45)   # 100 个日期横着排会挤，转 45 度纯属好看

fig.tight_layout()              # 别让标题被裁掉

fig.savefig(Path(__file__).with_name("ma.png"))
plt.show()                      # 弹窗显示