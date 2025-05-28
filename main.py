import os
import requests
import schedule
import time
from flask import Flask
import threading
import asyncio
import telegram

# 📌 環境變數
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TRADER_ID = os.environ.get("TRADER_ID")  # 交易員 ID，例如：4466349480575764737

bot = telegram.Bot(token=TELEGRAM_TOKEN)
last_trade_key = ""

# ✅ Flask 假 Web 服務，防止 Render 休眠
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Binance Monitor is running.'

def start_flask():
    app.run(host='0.0.0.0', port=10000)

# 🔍 主邏輯：查詢 Copy Trading API
def check_latest_trade():
    global last_trade_key
    try:
        url = f"https://www.binance.com/bapi/copy-trade/api/v1/friendly/copy-trade/lead-portfolio/page-query"
        headers = {'Content-Type': 'application/json'}
        params = {
            "page": 1,
            "pageSize": 1,
            "traderUid": TRADER_ID
        }

        response = requests.post(url, json=params, headers=headers)
        data = response.json()

        trade_list = data.get("data", {}).get("openPositionList", [])
        if not trade_list:
            print("❗ 無開倉紀錄")
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

# 📆 每 10 分鐘執行一次
schedule.every(10).minutes.do(check_latest_trade)

def start_scheduler():
    asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Binance 監控程式已啟動"))
    while True:
        schedule.run_pending()
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=start_scheduler).start()
    start_flask()
