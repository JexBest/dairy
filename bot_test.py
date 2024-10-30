import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from config import TELEGRAM_BOT_TOKEN

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Функция запуска бота
async def start(update: Update, context: CallbackContext):
    # Создаем клавиатуру с кнопками
    keyboard = [
        ["Добавить запись", "Просмотреть записи"],
        ["Настройки", "Помощь"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Отправляем сообщение с кнопками
    await update.message.reply_text(
        "Привет! Я ваш дневник-бот. Вы можете начать добавлять записи и фотографии.",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    if user_message == "Добавить запись":
        await update.message.reply_text("Введите текст новой записи:")
    elif user_message == "Просмотреть записи":
        await update.message.reply_text("Вот ваши записи.")
    elif user_message == "Настройки":
        await update.message.reply_text("Здесь настройки бота.")
    elif user_message == "Помощь":
        await update.message.reply_text("Чем я могу помочь?")
    else:
        await update.message.reply_text(f"Вы написали: {user_message}")


# Основная функция для запуска бота
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))

    # Добавляем обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    app.run_polling()


if __name__ == '__main__':
    main()
