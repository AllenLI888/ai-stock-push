# utils/line.py
import os
import requests

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
    print("📤 LINE API 回傳狀態碼:", response.status_code)
    print("📤 LINE API 回傳內容:", response.text)
