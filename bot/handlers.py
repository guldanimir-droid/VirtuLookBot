import logging
import requests
import io
import os
import base64
import hmac
import hashlib
from telebot import TeleBot, types
from telebot.types import InputFile
from config import TELEGRAM_TOKEN, FASHN_API_KEY, VIRTUAL_TRYON_SECRET
from bot.fashn import FashnClient

logger = logging.getLogger(__name__)

def verify_tryon_token(token: str) -> str | None:
    """Проверяет токен и возвращает user_id, если токен верен"""
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        user_id, signature = decoded.rsplit(':', 1)
        expected = hmac.new(VIRTUAL_TRYON_SECRET.encode(), user_id.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(signature, expected):
            return user_id
    except Exception:
        pass
    return None

bot = TeleBot(TELEGRAM_TOKEN)
fashn_client = FashnClient(FASHN_API_KEY)

# Хранилище активных сессий: chat_id -> словарь с данными
active_sessions = {}

@bot.message_handler(commands=['start'])
def start(message: types.Message):
    text = message.text
    if ' ' in text:
        token = text.split(' ', 1)[1]
        user_id = verify_tryon_token(token)
        if user_id and user_id == str(message.from_user.id):
            active_sessions[message.chat.id] = {'user_id': user_id}
            bot.send_message(message.chat.id, 
                "✅ Доступ разрешён. Пришлите, пожалуйста, фото человека (модели) в полный рост.")
            return
    # Если токен неверный или отсутствует
    bot.send_message(message.chat.id, 
        "🚫 Этот бот работает только через @stil_snap_ai_bot. Пожалуйста, начните с основного бота.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in active_sessions:
        bot.send_message(chat_id, "Доступ не разрешён. Используйте команду /start с правильной ссылкой.")
        return
    
    session = active_sessions[chat_id]
    if 'model_bytes' not in session:
        # Это первое фото — модель
        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)
        session['model_bytes'] = file_bytes
        bot.send_message(chat_id, "Отлично! Теперь пришлите фото одежды, которую хотите примерить.")
    else:
        # Это второе фото — одежда
        model_bytes = session['model_bytes']
        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = bot.get_file(file_id)
        garment_bytes = bot.download_file(file_info.file_path)
        
        bot.send_message(chat_id, "⏳ Генерирую виртуальную примерку... Это может занять до минуты.")
        try:
            prediction_id = fashn_client.run(model_bytes, garment_bytes)
            result_url = fashn_client.poll(prediction_id)
            resp = requests.get(result_url)
            if resp.status_code == 200:
                bot.send_photo(chat_id, InputFile(io.BytesIO(resp.content), filename="result.jpg"),
                    caption="✅ Примерка готова! Хотите ещё? Пришлите новое фото одежды или начните заново через основного бота.")
            else:
                bot.send_message(chat_id, "❌ Не удалось получить изображение результата.")
        except Exception as e:
            logger.exception("Ошибка при генерации примерки")
            bot.send_message(chat_id, f"⚠️ Ошибка: {str(e)}")
        finally:
            # Удаляем сессию, чтобы можно было начать заново (или оставить для следующей одежды)
            del active_sessions[chat_id]

@bot.message_handler(func=lambda message: True)
def echo(message: types.Message):
    bot.send_message(message.chat.id, "Пожалуйста, отправьте фото.")
