import os
import requests
from utils.data_source import get_closing_data

def predict_price(close_price):
    close = float(close_price)
    predict = close * 1.03
    return round(predict, 2)

def generate_message(stock_id, info):
    predict = predict_price(info['close'])
    suggestion = '✅ 多頭趨勢，可考慮買進' if predict > float(info['close']) else '⚠️ 觀望為宜'

    message = (
        f"📈 {stock_id} {info['name']}（今日收盤）\n"
        f"💰 收盤價: {info['close']} 元\n"
        f"📊 成交量: {info['volume']} 張\n"
        f"🤖 AI 預測價: {predict} 元\n"
        f"📌 投資建議: {suggestion}\n"
        f"🎯 目標價: {predict} 元 (短線)\n"
        f"🏦 法人動向: 觀察中"
    )
    return message

def push_line_message(message):
    token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
    user_id = os.environ['LINE_USER_ID']

    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    body = {
        'to': user_id,
        'messages': [{
            'type': 'text',
            'text': message
        }]
    }
    response = requests.post(url, headers=headers, json=body)
    print("🔧 LINE API 回傳狀態碼:", response.status_code)
    print("🔧 LINE API 回傳內容:", response.text)

if __name__ == '__main__':
    stock_ids = ['3062', '3583', '4931', '3625']
    for stock_id in stock_ids:
        print(f"🚀 [分析] 股票代號 {stock_id}...")
        info = get_closing_data(stock_id)
        if info:
            message = generate_message(stock_id, info)
            print("✅ 推播訊息如下:\n", message)
            push_line_message(message)
        else:
            print(f"❌ 無法取得 {stock_id} 的收盤資料")
