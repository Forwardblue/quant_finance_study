import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

rng = np.random.default_rng(seed=42)
steps = rng.normal(loc=0.0, scale=1.0, size=500)   # 每日增量：均值 0、标准差 1 元
steps[0] = 0.0                                     # 第一天不动，起点正好是 100
prices = pd.Series(
    (100 + np.cumsum(steps)).round(2),             # cumsum = 逐日累加，这就是"游走"
    index=pd.date_range("2026-01-01", periods=500, freq="D"),
    name="price",
)
