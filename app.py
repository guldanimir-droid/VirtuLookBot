import os
import logging
from flask import Flask, request, abort
from config import TELEGRAM_TOKEN, WEBHOOK_URL_BASE, WEBHOOK_URL_PATH, PORT
from bot.handlers import bot
from telebot.types import Update

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.get("/")
def index():
    return "OK", 200

@app.post(WEBHOOK_URL_PATH)
def telegram_webhook():
    if request.headers.get("content-type") == "application/json":
        data = request.get_data().decode('utf-8')
        logger.info("Received update from Telegram")
        update = Update.de_json(data)
        bot.process_new_updates([update])
        return "", 200
    abort(403)

def set_webhook():
    """Устанавливает вебхук, если задан WEBHOOK_URL_BASE и TELEGRAM_TOKEN"""
    if not WEBHOOK_URL_BASE:
        logger.warning("WEBHOOK_URL_BASE не задан, пропускаем установку вебхука")
        return
    if not TELEGRAM_TOKEN:
        logger.warning("TELEGRAM_TOKEN не задан, невозможно установить вебхук")
        return
    
    full_webhook_url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH
    try:
        bot.remove_webhook()
        bot.set_webhook(url=full_webhook_url)
        logger.info(f"Webhook successfully set to {full_webhook_url}")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")

if __name__ == "__main__":
    # Устанавливаем вебхук только если переменные окружения заданы
    set_webhook()
    logger.info(f"Starting Flask server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
