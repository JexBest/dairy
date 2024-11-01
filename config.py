import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "data.db")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(BASE_DIR, "uploaded_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)

def generate_photo_path(telegram_id):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(PHOTO_DIR, f"{telegram_id}_{timestamp}.jpg")
# Создаем папку для фото, если её нет

LOG_DIR = os.path.join(BASE_DIR, "logs_py")
os.makedirs(LOG_DIR, exist_ok=True)  # Создает папку для логов, если её нет
LOG_FILE_PATH = os.path.join(LOG_DIR, "bot.log")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7835013090:AAFfvl5iTih4qoXxBRh0wxTYjEQjChBr0Q8")

