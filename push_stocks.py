# push_stocks.py
from utils.data_source import get_verified_stock_data
from utils.message import generate_message
from utils.line import push_line_message
from datetime import datetime, timedelta

def get_query_date():
    now = datetime.now()
    if now.hour < 15:
        return (now - timedelta(days=1)).strftime('%Y-%m-%d')
    return now.strftime('%Y-%m-%d')

if __name__ == '__main__':
    stock_list = ['3062', '3583', '4931', '3625']
    date = get_query_date()

    for stock_id in stock_list:
        print(f"\n🚀 [分析] 股票代號 {stock_id}...")
        info = get_verified_stock_data(stock_id, date)

        if info:
            msg = generate_message(stock_id, info)
            print("✅ 推播內容:\n", msg)
            push_line_message(msg)
        else:
            print(f"❌ {stock_id} 資料來源不一致，已略過推播。")
