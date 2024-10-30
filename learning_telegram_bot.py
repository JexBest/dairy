from email.policy import default
from database.models import filter_diary_by_date
from httpx import request
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN

# Включаем логирование
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext):
    user = update.effective_user  # Получаем информацию о пользователе

    # Удаляем старую клавиатуру, если она есть
    await update.message.reply_text("Обновляем меню...", reply_markup=ReplyKeyboardRemove())

    # Создаем новую клавиатуру с командами
    keyboard = [
        ["Добавить запись", "Посмотреть записи"],
        ["Изменить запись", "Удалить запись"],
        ["О программе", "Информация о пользователе"],
        [KeyboardButton("Поделиться контактом", request_contact=True)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    # Отправляем сообщение с приветствием и новой клавиатурой
    await update.message.reply_text(
        f"Привет, {user.first_name}! Это базовый бот. Выберите команду или отправьте текст.",
        reply_markup=reply_markup
    )

async def about_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Привет, это твой помощник, который поможет тебе в следующем:\n"
        "Сохранить фото в личное хранилище\n"
        "Вести свой дневник, либо ставить напоминание о событиях\n"
        "Ты можешь в любой момент отредактировать любую свою запись или время\n"
        "Мы всегда рядом, если у тебя будут предложения об улучшении, обязательно пиши о них нам!"
    )


async def view_entries_command(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    context.user_data['waiting_for_data'] = False
    await update.message.reply_text("Введите дату в формате 'ГГГГ-ММ-ДД' для поиска записей")
    if context.user_data.get('waiting_for_data'):
        date = context.user_data['waiting_for_data']
        filter_diary_by_date(telegram_id, date)




async def contact_handler(update: Update, context: CallbackContext):
    contact = update.message.contact
    context.user_data['phone_number'] = contact.phone_number
    await update.message.reply_text(
        f"Спасибо за предоставленную информацию {contact.phone_number}"
    )
# Обработчик команды /help
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Это команда /help. Выберите команду из меню или отправьте текст.")

# Обработчик команды /info
async def info_command(update: Update, context: CallbackContext):
    user = update.effective_user

    # Извлекаем имя, фамилию, ID и телефон (если он доступен)
    first_name = user.first_name
    last_name = user.last_name or "Нет фамилии!"
    user_id = user.id
    phone_number = context.user_data.get('phone_number', "Телефон не указан")

    await update.message.reply_text(
        f"Твое имя: {first_name}\n"
        f"Твоя фамилия: {last_name}\n"
        f"Твой аккаунт ID: {user_id}\n"
        f"Твой телефон: {phone_number}"
    )

#dsd
# Основная функция для запуска бота
def main():
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.Text("Информация о пользователе"), info_command))
    app.add_handler(MessageHandler(filters.Text("Посмотреть записи"), view_entries_command))
    app.add_handler(MessageHandler(filters.Text("О программе"), about_command))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    # Обработчик для любых текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help_command))

    # Запуск бота
    app.run_polling()

if __name__ == "__main__":
    main()
