import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

rng = np.random.default_rng(seed=42)
steps = rng.normal(loc=0,scale=1,size=500)
steps[0] = 0

prices = pd.Series(
    (100+np.cumsum(steps)).round(2),
    index=pd.date_range("2026-01-01",periods=500,freq="D"),
    name="price"
)

sma5 = prices.rolling(window=5).mean()
ema5 = prices.ewm(span=5,adjust=False).mean()

ma20=prices.rolling(window=20).mean()
ma60=prices.rolling(window=60).mean()

df = pd.DataFrame({"prices":prices,})