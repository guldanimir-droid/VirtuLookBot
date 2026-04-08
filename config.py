import os

# --- секреты (берутся из переменных окружения) ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
FASHN_API_KEY  = os.getenv('FASHN_API_KEY', '')
WEBHOOK_URL_BASE = os.getenv('WEBHOOK_URL_BASE', '')

# --- сеть ---
# Для локального теста можно использовать ngrok, в продакшене Railway сам задаст WEBHOOK_URL_BASE
WEBHOOK_URL_PATH = f"/bot/{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else "/bot/"

# Порт для локального запуска (на Railway используется порт из переменной PORT)
PORT = int(os.getenv('PORT', 8080))
