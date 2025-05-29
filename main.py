def check_latest_trade():
    global last_trade_key
    try:
        url = "https://www.binance.com/bapi/copy-trade/api/v1/friendly/copy-trade/lead-portfolio/page-query"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.binance.com'
        }
        params = {
            "page": 1,
            "pageSize": 1,
            "traderUid": TRADER_ID
        }

        response = requests.post(url, json=params, headers=headers)

        print("🔍 狀態碼：", response.status_code)
        print("🔍 回應內容：", response.text[:300])  # 限制前 300 字方便觀察

        if response.status_code != 200:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ 請求失敗，狀態碼：{response.status_code}")
            return

        try:
            data = response.json()
        except Exception as e:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ 回應無法解析為 JSON：{e}")
            return

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
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            last_trade_key = trade_key
        else:
            print("📉 無變化")

    except Exception as e:
        print("❌ 其他錯誤：", e)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ 檢查失敗：{e}")
