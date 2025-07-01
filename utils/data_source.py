import os
import datetime
import requests
import pandas as pd
import re
import json
from datetime import datetime

def get_yahoo_intraday_data(stock_id):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_id}.TW?interval=5m&range=1d"
        print(f"🌐 Yahoo API 請求: {url}")
        resp = requests.get(url).json()

        result = resp.get("chart", {}).get("result", [])[0]
        timestamps = result.get("timestamp", [])
        indicators = result.get("indicators", {}).get("quote", [{}])[0]

        if not timestamps or "close" not in indicators or "volume" not in indicators:
            print("⚠️ Yahoo 回傳資料不完整")
            return None

        for i in range(-1, -len(timestamps) - 1, -1):
            close = indicators["close"][i]
            volume = indicators["volume"][i]
            if close is not None and volume is not None:
                ts = datetime.fromtimestamp(timestamps[i])
                now = datetime.now()
                diff = now - ts
                if ts.date() != now.date():
                    print(f"⚠️ 最新資料不是今天 ({ts})，略過")
                    return None
                if diff.total_seconds() > 600:
                    print(f"⚠️ 最新資料已超過 10 分鐘 ({ts})，略過")
                    return None

                return {
                    "close": str(close),
                    "volume": str(int(volume / 1000)),
                    "date": ts.strftime('%Y-%m-%d %H:%M')
                }

        print("⚠️ 無有效即時資料")
        return None

    except Exception as e:
        print(f"❌ Yahoo 即時資料解析失敗: {e}")
        return None


def get_xq_intraday_data(stock_id):
    try:
        url = f"https://www.xq.com.tw/stock/{stock_id}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(url, headers=headers, timeout=10)
        html = res.text

        pattern = r'root.App.main = (.*?);\n'
        match = re.search(pattern, html)
        if not match:
            print("⚠️ 無法從 XQ 網頁擷取 JSON 結構")
            return None

        raw_json = json.loads(match.group(1))
        quote = raw_json["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]["price"]

        close = quote.get("regularMarketPrice", {}).get("raw")
        ts = quote.get("regularMarketTime", {}).get("raw")
        volume = quote.get("regularMarketVolume", {}).get("raw", 0)

        if close is None or ts is None:
            print("⚠️ XQ 無有效價格或時間資料")
            return None

        dt = datetime.fromtimestamp(ts)
        now = datetime.now()
        if dt.date() != now.date():
            print(f"⚠️ XQ 資料不是今天（{dt}）")
            return None

        return {
            "close": str(close),
            "volume": str(int(volume / 1000)),
            "date": dt.strftime('%Y-%m-%d %H:%M')
        }

    except Exception as e:
        print(f"❌ XQ 股價解析失敗: {e}")
        return None


def get_reliable_intraday_data(stock_id):
    yahoo_data = get_yahoo_intraday_data(stock_id)
    if yahoo_data:
        print(f"✅ 使用 Yahoo 即時資料: {yahoo_data}")
        return yahoo_data

    xq_data = get_xq_intraday_data(stock_id)
    if xq_data:
        print(f"✅ 使用 XQ 即時資料: {xq_data}")
        return xq_data

    print(f"❌ Yahoo 和 XQ 都無法取得 {stock_id} 的即時資料")
    return None
