def check_trade_history():
    global last_trade_key
    try:
        url = "https://www.binance.com/bapi/copy-trade/api/v1/friendly/copy-trade/lead-history/get-position-history"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.binance.com'
        }
        payload = {
            "page": 1,
            "pageSize": 1,
            "traderUid": TRADER_ID
        }

        response = requests.post(url, json=payload, headers=headers)

        print("🔍 狀態碼：", response.status_code)
        print("🔍 回應內容：", response.text[:300])

        if response.status_code != 200:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ 請求失敗，狀態碼：{response.status_code}")
            return

        try:
            data = response.json()
        except Exception as e:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ 回應無法解析為 JSON：{e}")
            return

        trade_list = data.get("data", {}).get("records", [])
        if not trade_list:
            print("📭 沒有歷史交易紀錄")
            return

        trade = trade_list[0]
        symbol = trade.get("symbol", "")
        side = trade.get("side", "")
        entry_price = trade.get("entryPrice", "")
        close_price = trade.get("closePrice", "")
        pnl = trade.get("pnl", "")
        update_time = trade.get("updateTimeStr", "")
        trade_id = trade.get("id", "")

        trade_key = f"{symbol}-{side}-{entry_price}-{trade_id}"
        if trade_key != last_trade_key:
            message = (
                f"📒 新歷史交易紀錄：\n"
                f"🪙 幣種: {symbol}\n"
                f"📥 方向: {side}\n"
                f"💵 入場: {entry_price}\n"
                f"🏁 平倉: {close_price}\n"
                f"💰 盈虧: {pnl}\n"
                f"🕰 時間: {update_time}"
            )
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            last_trade_key = trade_key
        else:
            print("📉 無新交易")

    except Exception as e:
        print("❌ 其他錯誤：", e)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ 檢查失敗：{e}")
