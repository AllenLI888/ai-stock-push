# utils/data_source.py

import os
import datetime
import requests
import pandas as pd

def get_finmind_data(stock_id, date):
    token = os.environ['FINMIND_TOKEN']
    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        "dataset": "TaiwanStockPrice",
        "data_id": stock_id,
        "start_date": date,
        "token": token,
    }
    resp = requests.get(url, params=params).json()
    if resp["status"] != 200 or not resp["data"]:
        return None
    df = pd.DataFrame(resp["data"])
    row = df[df["date"] == date]
    if row.empty:
        return None
    return {
        "close": str(row.iloc[0]["close"]),
        "volume": str(int(row.iloc[0]["Trading_Volume"] / 1000)),  # 單位張
        "date": date
    }

def get_twse_avg_all(stock_id, date):
    date_fmt = date.replace("-", "")
    url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG_ALL?response=json&date={date_fmt}"
    resp = requests.get(url).json()
    if resp.get("stat") != "OK":
        return None
    for row in resp["data"]:
        if row[0] == stock_id:
            return {
                "close": row[2].replace(",", ""),
                "volume": row[1].replace(",", ""),
                "date": date
            }
    return None

def get_twse_stock_day(stock_id, date):
    yyyymm = date[:7].replace("-", "")
    url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={yyyymm}01&stockNo={stock_id}"
    resp = requests.get(url).json()
    if resp.get("stat") != "OK":
        return None
    for row in resp["data"]:
        if row[0].replace("/", "-") == date:
            return {
                "close": row[6].replace(",", ""),
                "volume": row[1].replace(",", ""),
                "date": date
            }
    return None

def is_close(x, y, tol=0.5):
    return abs(float(x) - float(y)) <= tol

def is_volume_close(x, y, tol=500):  # 容許 500 張誤差
    return abs(int(float(x)) - int(float(y))) <= tol

def get_verified_stock_data(stock_id, date):
    sources = [
        get_finmind_data(stock_id, date),
        get_twse_avg_all(stock_id, date),
        get_twse_stock_day(stock_id, date)
    ]

    if any(s is None for s in sources):
        print(f"⚠️ 有資料來源缺失: {[s is not None for s in sources]}")
        return None

    close_prices = [s["close"] for s in sources]
