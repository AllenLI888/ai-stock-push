import requests

def get_twse_closing_data(stock_id):
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        for stock in data:
            if stock["Code"] == stock_id:
                return {
                    "name": stock["Name"],
                    "close": stock["ClosingPrice"],
                    "volume": stock["TradeVolume"].replace(",", ""),
                    "date": stock.get("Date", "")  # Optional
                }
        print(f"⚠️ TWSE 找不到股票代號 {stock_id}")
        return None
    except Exception as e:
        print(f"❌ 擷取 TWSE 收盤資料失敗: {e}")
        return None
