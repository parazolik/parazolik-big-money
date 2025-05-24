from flask import Flask, request, jsonify
import logging
from pybit.unified_trading import HTTP
import requests  # <-- импорт для проверки IP добавил сюда

app = Flask(__name__)

# --- Новый роут для проверки IP ---
@app.route('/check_ip', methods=['GET'])
def check_ip():
    try:
        ip = requests.get('https://api.ipify.org').text
        logger.info(f"Внешний IP сервера: {ip}")
        return jsonify({"external_ip": ip})
    except Exception as e:
        logger.error(f"Ошибка при получении IP: {e}", exc_info=True)
        return jsonify({"error": "Не удалось получить внешний IP"}), 500
# --- конец нового роута ---

# Настройка логирования: INFO и выше, формат с датой и временем
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("BotServer")

# API ключи Bybit Testnet
api_key = "PjR6GAcSpsbLlUvqBt"
api_secret = "LTZQMggh6WDJQK2vqs9hqd8vHsQVX7xcK49g"

# Создаем сессию с Bybit Testnet
session = HTTP(testnet=True, api_key=api_key, api_secret=api_secret)

symbol = "BTCUSDT"
order_qty = 2000 / 25000  # Примерно 0.08 BTC при цене 25k
order_type = "Market"
category = "linear"

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        logger.info(f"Получен сигнал: {data}")

        if not data or "action" not in data:
            logger.warning("Нет параметра 'action' в JSON")
            return jsonify({"error": "Missing 'action' parameter"}), 400

        action = data["action"].lower()

        if action == "long":
            place_order("Buy")
        elif action == "short":
            place_order("Sell")
        else:
            logger.warning(f"Неизвестное действие: {action}")
            return jsonify({"error": f"Unknown action '{action}'"}), 400

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


def place_order(side):
    logger.info(f"Отправка ордера: {side}")
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
        logger.info(f"Ответ Bybit API: {response}")

        if response.get("retCode") != 0:
            logger.error(f"Ошибка в ответе Bybit: {response.get('retMsg')}")

    except Exception as e:
        logger.error(f"Исключение при отправке ордера: {e}", exc_info=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
