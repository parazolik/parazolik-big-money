from flask import Flask, request
from pybit.unified_trading import HTTP

app = Flask(__name__)

# 🔑 API-ключи от Bybit Testnet
api_key = "PjR6GAcSpsbLlUvqBt"
api_secret = "LTZQMggh6WDJQK2vqs9hqd8vHsQVX7xcK49g"

# 📡 Сессия подключения к Testnet
session = HTTP(
    testnet=True,
    api_key=api_key,
    api_secret=api_secret,
)

# ⚙️ Настройки торговли
symbol = "BTCUSDT"
order_qty = 2000 / 25000  # Пример на $2000 с ценой $25K (можешь поправить вручную)
order_type = "Market"
category = "linear"

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    print("🔔 Получен сигнал:", data)

    action = data.get("action")

    if action == "long":
        place_order("Buy")
    elif action == "short":
        place_order("Sell")
    else:
        print("⚠️ Неизвестное действие:", action)

    return 'ok'

def place_order(side):
    print(f"📤 Отправка ордера: {side}")
    try:
        response = session.place_order(
            category=category,
            symbol=symbol,
            side=side,
            order_type=order_type,
            qty=order_qty,
            time_in_force="GoodTillCancel",
            reduce_only=False
        )
        print("✅ Ордер отправлен:", response)
    except Exception as e:
        print("❌ Ошибка при отправке ордера:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
