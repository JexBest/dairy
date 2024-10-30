from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import logging
from config import TELEGRAM_BOT_TOKEN
from telegram import ReplyKeyboardMarkup
# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)




async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    keyboard = [['/start', '/help', '/info']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Привет, {user.first_name}! Выберите команду:", reply_markup=reply_markup
    )


# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext):
    user = update.effective_user  # получаем информацию о пользователе
    await update.message.reply_text(f"Привет, {user.first_name}! Это базовый бот. Отправь команду /help для подсказок.")


async def info(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_text(
        f"Информация о вас:\n"
        f"Имя: {user.first_name}\n"
        f"Фамилия: {user.first_name or 'Не указана.'}\n"
        f"Telegram ID {user.id}"
    )


async  def help(update: Update, context: CallbackContext):
    user = update.message.from_user.id
    await  update.message.reply_text(f"Привет, это твой Telegramm ID: {user}! Пока больше ни чем помочь не могу")

async def handle_text(update: Update, context: CallbackContext):
    await update.message.reply_text("Я пока понимаю только команды. Отправь /help для списка команд.")

# Основная функция для запуска бота
def main():
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчик для команды /start
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("", handle_text))

    # Запуск бота
    app.run_polling()

if __name__ == "__main__":
    main()
