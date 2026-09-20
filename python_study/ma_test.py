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
sma5 = prices.rolling(window=5,min_periods=1).mean().round(1)

# 3. 拼成表格打印
df = pd.DataFrame({"price": prices, "SMA5": sma5})
print(prices)
print(sma5)
print(df)

# 注意：上面用了 min_periods=1，意思是数据不够 5 个也照算，
# 所以前 4 行的 SMA5 其实只是前 1~4 个价格的平均，不算真正的 5 日均线。
# 如果想让它变回 NaN（诚实地表示「数据不够」），去掉 min_periods=1 就行：
# prices.rolling(window=5).mean()
