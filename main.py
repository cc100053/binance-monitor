import os
import requests
import schedule
import time
from flask import Flask
import threading
import asyncio
import telegram

# === 環境變數 ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TRADER_ID = os.environ.get("TRADER_ID")

bot = telegram.Bot(token=TELEGRAM_TOKEN)
last_trade_key = ""

# === Flask 假 Web Service ===
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Binance Monitor is running.'

def start_flask():
    app.run(host='0.0.0.0', port=10000)

# === Binance 監控邏輯 ===
def check_latest_trade():
    global last_trade_key
    try:
        url = "https://www.binance.com/bapi/copy-trade/api/v1/friendly/copy-trade/lead-portfolio/page-query"
        headers = {'Content-Type': 'application/json'}
        params = {
            "page": 1,
            "pageSize": 1,
            "traderUid": TRADER_ID
        }

        response = requests.post(url, json=params, headers=headers)
        data = response.json()

        print("🔍 API 回傳內容：", data)  # 👉 新增 debug 訊息

        trade_list = data.get("data", {}).get("openPositionList", [])
        if not trade_list:
            print("📭 尚未開倉")
            return

        trade = trade_list[0]
        symbol = trade.get("symbol", "")
        side = trade.get("side", "")
        entry_price = trade.get("entryPrice", "")
        pnl = trade.get("unrealizedPnL", "")

        trade_key = f"{symbol}-{side}-{entry_price}"
        if trade_key != last_trade_key:
            message = f"📈 新交易紀錄：\n🪙 幣種: {symbol}\n📥 方向: {side}\n💵 入場價: {entry_price}\n📊 未實現盈虧: {pnl}"
            asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message))
            last_trade_key = trade_key
        else:
            print("📉 無變化")

    except Exception as e:
        print("❌ 監控錯誤：", e)
        asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ 檢查失敗：{e}"))

# === 啟動排程器的子線程 ===
def start_scheduler():
    def run_scheduler():
        asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Binance 監控已啟動"))
        while True:
            schedule.run_pending()
            time.sleep(5)

    schedule.every(10).minutes.do(check_latest_trade)
    threading.Thread(target=run_scheduler).start()

# === 主程式 ===
if __name__ == "__main__":
    start_scheduler()
    start_flask()
