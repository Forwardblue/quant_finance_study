
import pandas as pd
import akshare as ak
import datetime
from pathlib import Path
from datetime import date, timedelta

today = date.today()
yesterday = today - timedelta(days=1)
today = datetime.date.today()
cal = ak.tool_trade_date_hist_sina()["trade_date"]
cal_trade = cal[cal <= today]
cal_trade_max = cal_trade.max()
trade_data_date = cal_trade_max-timedelta(days=1)
print(type(cal_trade_max))
print(trade_data_date)
