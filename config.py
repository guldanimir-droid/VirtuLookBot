# --- секреты ---
TELEGRAM_TOKEN = '8602871973:AAHJQ048-nTZcFxAeWFtX2d5zqJ_eHGcH9U'
FASHN_API_KEY  = 'fa-ie2irJofsoGJ-4Fr9itDyZsrar7hzZ51QhOQm'

# --- сеть ---
# На тесте (ngrok) подменяйте это на https://<твой-.ngrok.app>
WEBHOOK_URL_BASE = '----------------------------------------p'   # ← поменяйте в продакшне
WEBHOOK_URL_PATH = f"/bot/{TELEGRAM_TOKEN}"

# Локальный порт, который будете пробрасывать через ngrok
PORT = 8080
