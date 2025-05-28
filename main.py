import requests
import time
import os
from bs4 import BeautifulSoup
import telegram

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TARGET_URL = os.environ.get('TARGET_URL')

bot = telegram.Bot(token=TELEGRAM_TOKEN)

def fetch_latest_records():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(TARGET_URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 根據實際的 HTML 結構調整以下選擇器
    records = soup.select('.css-1vuj9rf')  # 假設這是每筆紀錄的 class
    return [record.get_text(strip=True) for record in records]

def main():
    previous_records = set()
    while True:
        try:
            current_records = set(fetch_latest_records())
            new_records = current_records - previous_records
            if new_records:
                message = "📈 Binance 最新交易紀錄出現變動！\n" + "\n".join(new_records)
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                previous_records = current_records
            time.sleep(600)  # 每 10 分鐘檢查一次
        except Exception as e:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"發生錯誤：{e}")
            time.sleep(600)

if __name__ == "__main__":
    main()
