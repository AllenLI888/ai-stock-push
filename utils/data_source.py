import requests

def get_closing_data(stock_id):
    try:
        # 根據股票代號判斷是上櫃（OTC）或上市（TWSE）
        is_otc = stock_id.startswith(('4', '5', '6', '8'))

        if is_otc:
            url = "https://openapi.tpex.org.tw/v1/stock_day_all"
        else:
            url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"

        print(f"📡 查詢來源: {'TPEx' if is_otc else 'TWSE'}")

        resp = requests.get(url, timeout=10)
        data = resp.json()

        for stock in data:
            if stock["Code"] == stock_id:
                return {
                    "name": stock.get("Name", ""),
                    "close": stock.get("ClosingPrice", "").strip(),
                    "volume": stock.get("TradeVolume", "").replace(",", ""),
                    "date": stock.get("Date", "")
                }

        print(f"⚠️ 找不到股票代號 {stock_id}")
        return None

    except Exception as e:
        print(f"❌ 擷取收盤資料失敗: {e}")
        return None
