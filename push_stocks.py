# push_stocks.py

import datetime
from utils.line import push_line_message
from utils.message import generate_message
from utils.data_source import (
    get_verified_stock_data,
    get_finmind_intraday_data
)

# 股票代號清單
STOCK_IDS = ['3062', '3583', '4931', '3625']

def use_intraday():
    now = datetime.datetime.now()
    return now.hour < 15 or (now.hour == 15 and now.minute < 30)

if __name__ == '__main__':
    for stock_id in STOCK_IDS:
        print(f"\n🚀 [分析] 股票代號 {stock_id}...")

        if use_intraday():
            info = get_finmind_intraday_data(stock_id)
            if info:
                print(f"✅ 使用即時盤中資料: {info['date']}")
                message = generate_message(stock_id, info)
                push_line_message(message)
            else:
                print(f"❌ 無法取得 {stock_id} 即時資料")
        else:
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            info = get_verified_stock_data(stock_id, today)
            if info:
                print(f"✅ 使用日資料 (交叉驗證): {today}")
                message = generate_message(stock_id, info)
                push_line_message(message)
            else:
                print(f"❌ {stock_id} 資料驗證不一致，略過推播")
