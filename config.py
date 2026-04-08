import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FASHN_API_KEY = os.getenv('FASHN_API_KEY')
VIRTUAL_TRYON_SECRET = os.getenv('VIRTUAL_TRYON_SECRET', 'default-secret-change-me')
WEBHOOK_URL_BASE = os.getenv('WEBHOOK_URL_BASE', '')
WEBHOOK_URL_PATH = f"/bot/{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else "/bot/"
PORT = int(os.getenv('PORT', 8080))
