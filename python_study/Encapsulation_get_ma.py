import pandas as pd
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
from indicators import get_df, get_ma

# 设置中文字体（SimHei 黑体，Windows 自带）
plt.rcParams["font.sans-serif"] = ["SimHei"]
# 解决负号显示异常的问题
plt.rcParams["axes.unicode_minus"] = False

N_DAYS = 252        # 一年的交易日数
COST = 0.001        # 单边手续费 0.1%


# ============================================================
# 第一层：逐行变换 —— 输入代码，输出带全部衍生列的 df
# ============================================================
def run(code, adjust="qfq", start_date="20240101", fast=5, slow=20):
    df = get_ma(code, adjust=adjust, start_date=start_date)

    col_fast, col_slow = f"ma{fast}", f"ma{slow}"
    start = df[[col_fast, col_slow]].dropna().index[0]
    df = df.loc[start:].copy()

    df["status"] = (df[col_fast] > df[col_slow]).astype(int)
    df["cross"] = df["status"].diff()
    df["golden_cross_flag"] = (df["cross"] == 1).astype(int)
    df["death_cross_flag"] = (df["cross"] == -1).astype(int)

    df["pos"] = df["status"].shift(1)
    df["pos"] = df["pos"].fillna(0)

    df["strat_ret"] = df["pos"] * df["daily_return"]

    cost = df["pos"].diff().abs().fillna(0) * COST
    df["cost"] = cost
    df["strat_ret_cost"] = df["strat_ret"] - cost

    df["fwd5"] = df["close"].shift(-5) / df["close"] - 1
    df["fwd10"] = df["close"].shift(-10) / df["close"] - 1
    return df


# ============================================================
# 第二层：汇总 —— 一条收益率序列，压成一个 Series
# ============================================================
def summary(returns):
    n = len(returns)
    total = (1 + returns).prod() - 1
    annual = (1 + total) ** (N_DAYS / n) - 1
    nav = (1 + returns).cumprod()
    mdd = (nav / nav.cummax() - 1).min()

    return pd.Series({
        "总收益": total,
        "年化": annual,
        "最大回撤": mdd,
        "天数": n,
    })


# ============================================================
# 另一类汇总：需要事件和价格，光有收益率序列不够
# ============================================================
def trade_stats(df):
    golden = df.index[df["cross"] == 1].tolist()
    death = df.index[df["cross"] == -1].tolist()

    trades = []
    for g in golden:
        after = [d for d in death if d > g]
        if after:
            trades.append(df.loc[after[0], "close"] / df.loc[g, "close"] - 1)

    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t <= 0]

    return pd.Series({
        "笔数": len(trades),
        "未平仓": len(golden) - len(trades),
        "胜率": len(wins) / len(trades) if trades else np.nan,
        "平均盈利": np.mean(wins) if wins else np.nan,
        "平均亏损": np.mean(losses) if losses else np.nan,
        "盈亏比": np.mean(wins) / abs(np.mean(losses)) if (wins and losses) else np.nan,
    })


# ============================================================
# 用法：一个函数调一次，就能把策略和基准摆在一起
# ============================================================
if __name__ == "__main__":
    df = run("sh600519")

    table = pd.DataFrame({
        "策略": summary(df["strat_ret"]),
        "策略(含成本)": summary(df["strat_ret_cost"]),
        "买入持有": summary(df["daily_return"]),
    })
    print(table.round(6).to_string())
    print()
    print(trade_stats(df).to_string())
    print()
    print(f"区间 {df.index[0].date()} ~ {df.index[-1].date()}")

    print()
    codes = ["sh600519", "sz000001", "sh601318", "sh600036", "sz300750"]
    summaries = {}
    for code in codes:
        df = run(code)
        trade_stats(df).to_string()
        summaries[code] = pd.concat([summary(df["strat_ret_cost"]),trade_stats(df)])

    table5 = pd.DataFrame(summaries)
    print(table5.round(6).to_string())
    #针对策略和持续买入的对比，加了几行，不然看不出策略和持续买入的差别
    rows = []
    for code in codes:
        df = run(code)
        s = summary(df["strat_ret"]).add_prefix("策略_")
        b = summary(df["daily_return"]).add_prefix("持有_")
        rows.append(pd.concat([s, b, trade_stats(df)]))
    table5 = pd.DataFrame(rows, index=codes).T
    print(table5.round(4).to_string())



