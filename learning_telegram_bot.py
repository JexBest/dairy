import calendar
from datetime import datetime, timedelta

from database.models import filter_diary_by_date, filter_diary_by_date_range
from httpx import request
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN

# Включаем логирование
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async  def show_calendar(update: Update, context: CallbackContext):
    year = 2024
    month = 10
    calendar_keyboard = generate_calendar(year, month)
    await update.message.reply_text("Выберете дату:", reply_markup=calendar_keyboard)


def generate_calendar(year, month):
    days_in_month = (datetime(year, month + 1, 1) - timedelta(days=1)).day
    keyboard = []

    for day in range(1, days_in_month + 1):
        button = InlineKeyboardButton(
            text=str(day),
            callback_data=f"{state}_{year}-{month:02d}-{day:02d}"
        )
        keyboard.append([button])

    return keyboard

async def date_selected_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    state = data[0]
    selected_date = data[1]

    if state == "start_day":
        context.user_data["start_day"] = selected_date
        await query.message.reply_text(f"Начальная дата выбрана: {selected_date}. Теперь выберите конечную дату.")
        await show_calendar(update, context, state = "end_date")

    elif state == "end_date":
        context.user_data["end_date"] = selected_date
        await query.message.reply_text(f"Конечная дата выбрана: {selected_date}. Выполняю поиск…")
        await perform_date_range_search(update, context)

async def perform_date_range_search(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    start_date = context.user_data["start_date"]
    end_date = context.user_data["end_date"]

    entries = filter_diary_by_date_range(telegram_id, start_date, end_date)
    if entries:
        for entry in entries:
            await update.message.reply_text(f"Запись: {entry}")
    else:
        await update.message.reply_text(f"Записей за период с {start_date} по {end_date} не найдено.")


async def show_calendar (update, context, year = None, month = None):
    year = datetime.now().year
    month = datetime.now().month
    keyboard = generate_calendar(year, month)

    await update.message.reply_text(
        f"Выберете дату:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def view_entries_start_date(update: Update, context: CallbackContext):
    # Запрашиваем начальную дату
    context.user_data['waiting_for_start_date'] = True
    await update.message.reply_text("Введите стартовую дату в формате 'ГГГГ-ММ-ДД' для поиска записей")


async def calendar_callback (update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    action = data[0]

    year = int(data[1])
    month = int(data[2])

    if action == 'next':
        month += 1
        if month > 12:
            month = 1
            year = +1
    if action == 'prev':
        month -= 1
        if month < 1:
            month = 12
            year -= 1

    elif action == 'select':
        await show_calendar(update, context, year, month)
        return
    elif action == 'confirm':
        selected_date = data[3]
        await query.message.reply_text(f"Вы выбрали дату {selected_date}")
        return

    keyboard = generate_calendar(year, month)
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardButton(keyboard))




START_DATE, END_DATE = range(2)
CHOOSE_START_DATE, CHOOSE_END_DATE = range(2)
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
        ["Просмотр записи за период"],
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


async def start_date_handler (update: Update, context: CallbackContext):

    await update.message.reply_text("Добавляем кнопочку 'отмена'...", reply_markup=ReplyKeyboardRemove())
    keyboard = [
        ["Отмена"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    reply_markup = reply_markup
    await update.message.reply_text(
        f"Введите начальную дату в формате 'ГГГГ-ММ-ДД' для поиска записей",
        reply_markup=reply_markup
    )
    return START_DATE

async def  get_end_date(update: Update, context: CallbackContext):
    context.user_data['start_date'] = update.message.text
    await update.message.reply_text("Введите конечную дату в формате 'ГГГГ-ММ-ДД'")
    return END_DATE


async def display_results(update: Update, context: CallbackContext):
    date_start = context.user_data['start_date']
    date_end = update.message.text
    telegram_id = update.message.from_user.id
    entries = filter_diary_by_date_range(telegram_id, date_start, date_end)
    if entries:
        for entry in entries:
            await update.message.reply_text(f"{entry}")
    else:
        await update.message.reply_text(f"Записей за период с {date_start} по {date_end} не найдено")

    await update.message.reply_text("Обновляем меню...", reply_markup=ReplyKeyboardRemove())
    keyboard = [
        ["Добавить запись", "Посмотреть записи"],
        ["Изменить запись", "Удалить запись"],
        ["О программе", "Информация о пользователе"],
        ["Просмотр записи за период"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Меню обновлено!",
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("Просмотр записи за период"), view_entries_start_date)],
    states={
        CHOOSE_START_DATE: [CallbackQueryHandler(date_selected_callback)],
        CHOOSE_END_DATE: [CallbackQueryHandler(date_selected_callback)],
    },
    fallbacks=[]
)

async def view_entries_command(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    context.user_data['waiting_for_data'] = False
    await update.message.reply_text("Введите дату в формате 'ГГГГ-ММ-ДД' для поиска записей")
    if context.user_data.get('waiting_for_data'):
        date = context.user_data['waiting_for_data']
        filter_diary_by_date(telegram_id, date)


async def  show_result (update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id



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


# Основная функция для запуска бота
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.Text("О программе"), about_command))
    app.add_handler(MessageHandler(filters.Text("Информация о пользователе"), info_command))
    app.add_handler(MessageHandler(filters.Text("Посмотреть записи"), view_entries_command))
    app.add_handler(CommandHandler("calendar", show_calendar))
    app.add_handler(CallbackQueryHandler(calendar_callback))
    #app.add_handler(MessageHandler(filters.Text("Просмотр записей за период"), view_entries_handler))
    # Указываем обработчик для текстовых сообщений с проверкой флагов
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_result))

    app.add_handler(conv_handler)
    # Контактный обработчик
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    # Запуск бота
    app.run_polling()

if __name__ == "__main__":
    main()
