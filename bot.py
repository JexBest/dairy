import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from database.models import add_user, add_diary_entry  # импорт функции для добавления пользователя в БД
from datetime import datetime

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для приветственного сообщения и регистрации пользователя
async def start(update: Update, context: CallbackContext):
    # Получаем данные пользователя
    telegram_id = update.message.from_user.id
    username = update.message.from_user.username
    phone_number = None  # Если у пользователя нет привязанного телефона

    # Пытаемся добавить пользователя в БД
    try:
        user_id = add_user(telegram_id, username, phone_number)
        registration_message = "Вы успешно зарегистрированы!"
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        registration_message = "Вы уже зарегистрированы!"

    # Создаем клавиатуру с кнопками
    keyboard = [
        ["Добавить запись", "Посмотреть записи"],
        ["Изменить запись", "Настройки"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Отправляем сообщение с результатом регистрации и клавиатуру
    await update.message.reply_text(
        f"Привет, {username}! {registration_message}\nВыберите действие:",
        reply_markup=reply_markup
    )

# Обработчик кнопки "Добавить запись"
async def add_entry(update: Update, context: CallbackContext):
    # Сохраняем состояние, чтобы знать, что ожидаем текст записи
    context.user_data['waiting_for_entry_text'] = True
    await update.message.reply_text("Введите текст для новой записи:")

# Обработчик для получения текста записи
async def handle_message(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id

    # 1. Проверка: ожидается текст записи
    if context.user_data.get('waiting_for_entry_text'):
        entry_text = update.message.text
        context.user_data['waiting_for_entry_text'] = False
        context.user_data['waiting_for_photo'] = True
        context.user_data['entry_text'] = entry_text
        await update.message.reply_text("Хотите добавить фото к записи? Отправьте фото или введите 'нет'.")
        return

    # 2. Проверка: ожидается фото
    if context.user_data.get('waiting_for_photo'):
        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            photo_path = f"{telegram_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            await photo_file.download(photo_path)
            context.user_data['photo_path'] = photo_path
            await update.message.reply_text("Фото добавлено к записи.")
        elif update.message.text.lower() == "нет":
            context.user_data['photo_path'] = None
            await update.message.reply_text("Фото не добавлено.")
        context.user_data['waiting_for_photo'] = False
        context.user_data['waiting_for_reminder'] = True
        await update.message.reply_text("Укажите дату напоминания в формате ГГГГ-ММ-ДД или введите 'нет' для пропуска.")
        return

    # 3. Проверка: ожидается дата напоминания
    if context.user_data.get('waiting_for_reminder'):
        if update.message.text.lower() == "нет":
            context.user_data['reminder_time'] = None
            await update.message.reply_text("Дата напоминания не добавлена.")
        else:
            try:
                reminder_time = datetime.strptime(update.message.text, "%Y-%m-%d")
                context.user_data['reminder_time'] = reminder_time
                await update.message.reply_text("Дата напоминания успешно добавлена.")
            except ValueError:
                await update.message.reply_text("Некорректный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
                return

        context.user_data['waiting_for_reminder'] = False

        # Заключительный шаг: сохранение записи с текстом, фото и напоминанием
        entry_text = context.user_data.get('entry_text')
        photo_path = context.user_data.get('photo_path')
        reminder_time = context.user_data.get('reminder_time')

        # Вызов функции добавления записи в БД
        add_diary_entry(telegram_id, entry_text, photo=photo_path, reminder_time=reminder_time)

        await update.message.reply_text("Запись успешно сохранена!")



# Основная функция для запуска бота
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики команд и кнопок
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Добавить запись$"), add_entry))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    app.run_polling()


if __name__ == '__main__':
    main()
