import numpy as np
import pandas as pd

# 1. 造 20 个价格（随机数 + 固定种子，保证每次运行结果一样）
rng = np.random.default_rng(seed=42)

prices = pd.Series(
    rng.uniform(90, 110, size=20).round(2),  # 90 ~ 110 之间取 20 个价格
    index=pd.date_range("2026-01-01", periods=20, freq="D"),
    name="price",
)

# 2. 算 SMA5：窗口为 5 的简单移动平均
sma5 = prices.rolling(window=5, min_periods=1).mean().round(1)
# 注意：上面用了 min_periods=1，意思是数据不够 5 个也照算，
# 所以前 4 行的 SMA5 其实只是前 1~4 个价格的平均，不算真正的 5 日均线。
# 如果想让它变回 NaN（诚实地表示「数据不够」），去掉 min_periods=1 就行：
# prices.rolling(window=5).mean()


# 3. 算 EMA5：指数移动平均
#    EMA(t) = α × P(t) + (1 - α) × EMA(t-1)，其中 α = 2 / (n + 1)
#    n = 5 时 α = 2/6 ≈ 0.3333，意思是今天的价格占 1/3 权重，昨天的 EMA 占 2/3
#    adjust=False = 就用上面这个递推式，且第一天 EMA 直接等于第一天价格
ema5 = prices.ewm(span=5, adjust=False).mean().round(1)

# 4. 拼成表格打印
df = pd.DataFrame({"price": prices, "SMA5": sma5, "EMA5": ema5})

print(df)

# 5. 换个方式：手写循环再算一遍 EMA5，和 pandas 对拍
#    pandas 的 ewm 内部也是这个递推式，只是用 C 写的、跑得快。
#    手写这一遍不是为了取代 pandas，是为了证明自己真懂 α 在干什么。
span = 5
alpha = 2 / (span + 1)          # 2/6 ≈ 0.3333

ema_manual = [prices.iloc[0]]   # 第一天：EMA 就是第一个价格本身
for p in prices.iloc[1:]:
    ema_manual.append(alpha * p + (1 - alpha) * ema_manual[-1])

# 注意：上面每步都拿「没取整」的 ema_manual[-1] 往下递推，只在最后才 round。
# 如果每步都 round 一下，误差会一步一步滚雪球，就和 pandas 对不上了。
ema_manual = pd.Series(ema_manual, index=prices.index).round(1)

print(ema_manual.equals(ema5))  # True = 两种方式算出来完全一样

