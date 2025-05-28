import os
import requests
import schedule
import time
from bs4 import BeautifulSoup
import telegram
from flask import Flask
import threading

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TARGET_URL = os.environ.get("TARGET_URL")

bot = telegram.Bot(token=TELEGRAM_TOKEN)
last_known = ""

# 🟢 Flask 假 Web 服務
app = Flask(__name__)

@app.route('/')
def home():
    return 'Binance monitor is running.'

def start_flask():
    app.run(host='0.0.0.0', port=10000)

# 🔍 Binance 監控邏輯
def check_latest_records():
    global last_known
    try:
        res = requests.get(TARGET_URL, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        records = soup.find_all("div", string=lambda t: t and "position" in t.lower())
        if records:
            latest = records[0].text.strip()
            if latest != last_known:
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"📈 Binance 最新交易：\n{latest}")
                last_known = latest
    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ 檢查錯誤：{e}")

schedule.every(10).minutes.do(check_latest_records)

def start_scheduler():
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ 監控程式已啟動")
    while True:
        schedule.run_pending()
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=start_scheduler).start()
    start_flask()
