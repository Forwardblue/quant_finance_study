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
sma5 = prices.rolling(window=5).mean().round(2)

# 3. 拼成表格打印
df = pd.DataFrame({"price": prices, "SMA5": sma5})
print(df)

# 前 4 个是 NaN，因为凑不满 5 个价格。
# 想让它们也有值，就加 min_periods=1：
# prices.rolling(window=5, min_periods=1).mean()
