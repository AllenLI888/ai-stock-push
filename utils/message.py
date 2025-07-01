# utils/message.py

# 股票代號對應公司名稱
STOCK_NAME_MAP = {
    '3062': '建漢',
    '3583': '辛耘',
    '4931': '新盛力',
    '3625': '西勝'
}

def predict_price(close_price):
    close = float(close_price)
    predict = close * 1.03
    return round(predict, 2)

def generate_message(stock_id, info):
    predict = predict_price(info['close'])
    suggestion = '✅ 多頭趨勢，可考慮買進' if predict > float(info['close']) else '⚠️ 觀望為宜'
    stock_name = STOCK_NAME_MAP.get(stock_id, '')

    message = (
        f"📈 股票代號: {stock_id} {stock_name}\n"
        f"📅 日期: {info['date']}\n"
        f"💰 收盤價: {info['close']} 元\n"
        f"📊 成交量: {info['volume']} 張\n"
        f"🤖 AI 預測價: {predict} 元\n"
        f"📌 投資建議: {suggestion}\n"
        f"🎯 目標價: {predict} 元 (短線)\n"
        f"🏦 法人動向: 觀察中"
    )
    return message
