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

def get_yahoo_intraday_data(stock_id):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_id}.TW?interval=1m&range=1d"
        print(f"🌐 Yahoo API 請求: {url}")
        resp = requests.get(url).json()

        result = resp.get("chart", {}).get("result", [])[0]
        timestamps = result.get("timestamp", [])
        indicators = result.get("indicators", {}).get("quote", [{}])[0]

        if not timestamps or "close" not in indicators or "volume" not in indicators:
            print("⚠️ Yahoo 回傳資料不完整")
            return None

        latest_idx = -1
        close = indicators["close"][latest_idx]
        volume = indicators["volume"][latest_idx]
        if close is None or volume is None:
            print("⚠️ Yahoo 最新筆為 None，跳過")
            return None

        ts = datetime.datetime.fromtimestamp(timestamps[latest_idx]).strftime('%Y-%m-%d %H:%M')

        return {
            "close": str(close),
            "volume": str(int(volume / 1000)),  # 單位張（粗略估算）
            "date": ts
        }

    except Exception as e:
        print(f"❌ Yahoo 解析失敗: {e}")
        return None


def get_finmind_intraday_data(stock_id):
    token = os.environ['FINMIND_TOKEN']
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        "dataset": "TaiwanStockPriceMinute",
        "data_id": stock_id,
        "start_date": date,
        "token": token,
    }
    resp = requests.get(url, params=params).json()
    if resp["status"] != 200 or not resp["data"]:
        return None
    df = pd.DataFrame(resp["data"])
    if df.empty:
        return None
    latest = df.iloc[-1]
    return {
        "close": str(latest["close"]),
        "volume": str(int(latest["Trading_Volume"] / 1000)),  # 分鐘成交量換成張
        "date": latest["date"] + " " + latest["time"]
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

def is_volume_close(x, y, tol=500):
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
    volumes = [s["volume"] for s in sources]

    close_ok = all(is_close(cp, close_prices[0]) for cp in close_prices)
    volume_ok = all(is_volume_close(v, volumes[0]) for v in volumes)

    if close_ok and volume_ok:
        return sources[0]
    else:
        print("❌ 三方資料不一致，略過推播")
        print("🔍 三方資料來源比較：")
        print("[FINMIND]     ", sources[0])
        print("[TWSE_AVG_ALL]", sources[1])
        print("[TWSE_DAY]    ", sources[2])
        print("Close prices:", close_prices)
        print("Volumes:", volumes)
        return None
