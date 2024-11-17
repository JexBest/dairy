# bot.py
import re
import os
import logging
from email.policy import default
from multiprocessing.context import assert_spawning

from config import LOG_FILE_PATH
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputFile
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, ConversationHandler
from config import TELEGRAM_BOT_TOKEN

from database.models import add_user, add_diary_entry, update_diary_entry, view_all_notes, filter_diary_by_date
from datetime import datetime


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),  # Запись логов в logs_py/bot.log
        logging.StreamHandler()  # Продолжаем вывод в консоль
    ]
)
logger = logging.getLogger(__name__)

ADD_TEXT, ADD_PHOTO, ADD_REMINDER = range(3)

VIEW_NOTES, VIEW_ALL_NOTES, VIEW_ONE_DATE_NOTES, VIEW_RANGE_DATE_NOTES = range(4)


async def view_note_start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Давай поищем твои записи",
        reply_markup=ReplyKeyboardRemove()
    )
    keyboard = [
        ["Просмотр всех записей"],
        ["За дату", "За период"],
        ["Отмена"],
    ]
    reply_markup = ReplyKeyboardMarkup (keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Выбери действие как будем искать, или 'отмена' для выхода в главное меню",
        reply_markup = reply_markup
    )
    return VIEW_NOTES



async def view_all_note(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    entries = view_all_notes(telegram_id)
    await update.message.reply_text(
        "Ищем ваши записи...",
        reply_markup=ReplyKeyboardRemove()
    )
    keyboard = [
        ["Назад", "Отмена"],
    ]
    reply_markup = ReplyKeyboardMarkup (keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "По завершению просмотра нажмите 'Назад' для продолжение просмотра либо 'Отмена' для выхода в главное меню\nЕсли нужно будет изменить запись в будущем, запомните ее ID",
        reply_markup = reply_markup
    )
    if entries is None:
        await update.message.reply_text("Возникла ошибка при запросе записей.")
    elif not entries:
        await update.message.reply_text("Записи не найдены.")
    else:
        for entry in entries:
            entry_id = entry[0]
            date = entry[2]
            content = entry[3]
            photo_path = entry[4]
            await update.message.reply_text(
                f"ID: {entry_id}, Дата: {date}, Запись: {content}\n"
            )
            if photo_path and os.path.exists(photo_path):
                try:
                    with open(photo_path, 'rb') as photo:
                        await update.message.reply_photo(InputFile(photo))
                except Exception as e:
                    await update.message.reply_text(f"Не удалось отправить фото: {e}")


async def one_date_note (update: Update, context:CallbackContext):
    await update.message.reply_text(
        "За какую дату ищем запись?",
        reply_markup=ReplyKeyboardRemove()
    )
    keyboard = [
        ["Назад", "Отмена"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Введите дату в формате ГГГГ-ММ-ДД, 'Назад' для возврата в предыдущее меню, либо 'Отмена' для возврата в главное меню",
        reply_markup=reply_markup
    )
    return VIEW_ONE_DATE_NOTES

async def view_one_date_note (update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    context.user_data['date_note'] = update.message.text
    date = context.user_data['date_note']
    await update.message.reply_text(
        "Ищем ваши записи...",
        reply_markup=ReplyKeyboardRemove()
    )
    keyboard = [
        ["Назад", "Отмена"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "По завершению просмотра нажмите 'Назад' для продолжение просмотра либо 'Отмена' для выхода в главное меню\nЕсли нужно будет изменить запись в будущем, запомните ее ID",
        reply_markup=reply_markup
    )
    entries = filter_diary_by_date(telegram_id, date)
    if entries is None:
        await update.message.reply_text("Возникла ошибка при запросе записей.")
    elif not entries:
        await update.message.reply_text("Записи не найдены.")
    else:
        for entry in entries:
            entry_id = entry[0]
            date = entry[2]
            content = entry[3]
            photo_path = entry[4]
            await update.message.reply_text(
                f"ID: {entry_id}, Дата: {date}, Запись: {content}\n"
            )
            if photo_path and os.path.exists(photo_path):
                try:
                    with open(photo_path, 'rb') as photo:
                        await update.message.reply_photo(InputFile(photo))
                except Exception as e:
                    await update.message.reply_text(f"Не удалось отправить фото: {e}")
    return VIEW_NOTES




async def add_note_start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Введите текст для новой записи:",
        reply_markup=ReplyKeyboardRemove()  # Убираем клавиатуру, чтобы не мешала
    )
    keyboard = [
        ["Отмена"],
    ]
    reply_markup = ReplyKeyboardMarkup (keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Если хотите отменить, нажмите 'Отмена'",
        reply_markup=reply_markup
    )
    return ADD_TEXT


async def add_text(update: Update, context: CallbackContext):
    # Сохраняем текст записи в user_data
    context.user_data['note_text'] = update.message.text

    # Переходим к этапу добавления фото
    await update.message.reply_text(
        "Хотите добавить фото к записи? Отправьте фото",
        reply_markup=ReplyKeyboardRemove()
    )
    keyboard = [
        ["нет", "Отмена"],
    ]
    reply_markup = ReplyKeyboardMarkup (keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Нажмите 'нет', если не хотите добавлять фото, или 'отмена', если хотите завершить",
        reply_markup=reply_markup
    )

    return ADD_PHOTO

async def add_photo(update: Update, context: CallbackContext):
    if update.message.photo:  # Если пользователь отправил фото
        photo_file = await update.message.photo[-1].get_file()
        photo_path = f"{update.message.from_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        await photo_file.download_to_drive(photo_path)
        context.user_data['photo_path'] = photo_path
        await update.message.reply_text("Фото добавлено к записи.")
    elif update.message.text.lower() == 'нет':  # Если пользователь не хочет добавлять фото
        context.user_data['photo_path'] = None
        await update.message.reply_text("Фото не добавлено.")

    # Переходим к этапу добавления напоминания
    await update.message.reply_text("Укажите дату напоминания в формате 'ГГГГ-ММ-ДД' или введите 'нет', чтобы пропустить.")
    return ADD_REMINDER

async def add_reminder(update: Update, context: CallbackContext):
    user_input = update.message.text
    if update.message.text.lower() == 'нет':
        reminder_time = None
    else:
        try:
            reminder_date = datetime.strptime(user_input, "%Y-%m-%d")
            today = datetime.now().date()
            if reminder_date.date() < today:
                await update.message.reply_text(
                    "Напоминание не может быть установлено на прошедшую дату. Пожалуйста, введите корректную дату.")
                return ADD_REMINDER

            context.user_data['reminder_time'] = reminder_date
            await update.message.reply_text(f"Напоминание установлено на {reminder_date.strftime('%Y-%m-%d')}.")

        except ValueError:
            await update.message.reply_text(
            "Некорректный формат даты. Пожалуйста, введите дату в формате 'ГГГГ-ММ-ДД' или введите 'нет', чтобы пропустить.")
            return ADD_REMINDER  # Оставляем в текущем состоянии для повторного ввода
        reminder_time = update.message.text
    telegram_id = update.message.from_user.id
    content = context.user_data['note_text']
    photo_path = context.user_data.get('photo_path')

    # Добавление записи в БД через функцию из models.py
    try:
        entry_id = add_diary_entry(
            telegram_id=telegram_id,
            content=content,
            photo=None if not photo_path else open(photo_path, "rb").read(),
            reminder_time=reminder_time
        )
        if entry_id:
            await update.message.reply_text(f"Ваша запись успешно добавлена с ID: {entry_id}")
        else:
            await update.message.reply_text("Произошла ошибка при добавлении записи.")
    except Exception as e:
        logger.error(f"Ошибка при добавлении записи: {e}")
        await update.message.reply_text("Произошла ошибка при добавлении записи. Попробуйте снова.")

    # Завершаем диалог и возвращаем пользователя в главное меню
    await update.message.reply_text("Возвращаемся в главное меню", reply_markup=ReplyKeyboardRemove())

    keyboard = [
        ["Добавить запись", "Изменить запись"],
        ["Просмотр записей", "О программе"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Что делаем дальше?",
        reply_markup=reply_markup
    )


    return ConversationHandler.END

# Функция отмены
# async def cancel(update: Update, context: CallbackContext):
#     await update.message.reply_text("Действие отменено.", reply_markup=ReplyKeyboardRemove())
#     return ConversationHandler.END


def cleanup_temp_images():
    current_directory = os.getcwd()  # Текущая директория (корень проекта)

    # Перебираем все файлы в корневой директории
    for filename in os.listdir(current_directory):
        # Проверяем, если файл имеет расширение .jpg
        if filename.endswith(".jpg"):
            try:
                os.remove(os.path.join(current_directory, filename))  # Удаляем файл
                print(f"Удален временный файл: {filename}")
            except Exception as e:
                print(f"Ошибка при удалении файла {filename}: {e}")


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Действие отменено. Возвращаемся в главное меню...",
                                    reply_markup=ReplyKeyboardRemove())

    # Создаем основное меню с клавиатурой
    keyboard = [
        ["Добавить запись", "Изменить запись"],
        ["Просмотр записей", "О программе"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Меню обновлено:",
        reply_markup=reply_markup
    )
    return ConversationHandler.END


async def start (update: Update, context: CallbackContext):
    cleanup_temp_images()
    telegram_id = update.message.from_user.id
    username = update.message.from_user.username
    phone_number = None

    try:
        user_id = add_user(telegram_id, username, phone_number)
        registration_message = "Вы успешно зарегистрированы!"
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        registration_message = "Вы уже зарегистрированы!"
    await update.message.reply_text("Обновляем меню...", reply_markup=ReplyKeyboardRemove())

    keyboard = [
        ["Добавить запись","Изменить запись"],
        ["Просмотр записей","О программе"],
    ]
    reply_markup = ReplyKeyboardMarkup (keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Привет {username}, и добро пожаловать в самый удобный дневник/ежедневник, который я верен тебе понравиться своим функционалом. Давай уже создадим первую запись, и ты увидишь как это легко и удобно!",
        reply_markup=reply_markup
    )

async def help_command (update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Вот команды, которые вы можете использовать:\n"
        "/start - Запустить бота и увидеть главное меню\n"
        "/help - Получить справку по командам\n"
        "/info - Показать вашу информацию\n"
        "/about - Узнать о возможностях бота\n"
        "Или выберите команду из меню."
    )
async def cleanup_command(update: Update, context: CallbackContext):
    cleanup_temp_images()
    await update.message.reply_text("Временные файлы были успешно удалены.")



async def view_info (update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    nick_name = update.message.from_user.username
    await update.message.reply_text(
        "Информация о пользователе\n"
        f"Твой Telegram ID: {telegram_id}\n"
        f"Твое имя: {first_name}\n"
        f"Твоя фамилия: {last_name}\n"
        f"Твой никнейм: {nick_name}\n"
    )

async def about_dairy (update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Спасибо, что проявил интерес к данному приложению!\n"
        "С ним ты можешь\n"
        "Хранить свои записи и в любой момент посмотреть, вести это как свой личный дневник\n"
        "Если у тебя есть фото которые ты не хочешь ни где хранить кроме надежного места, \n"
        "мы это сделаем профессионально, просто добавь новую запись и приложи фотку. \n"
        "В любой момент ты сможешь его запросить зная ID записи.\n"
        "Еще удобная функция, это напоминалка, ты можешь через записи задать дату и время\n"
        "любого события, и мы тебе о нем напомним.\n"
        "Если есть предложения или пожелание или хочешь помочь проекту, просто свяжись с админом.\n"
        "Желаю успехов, твоя команда Your the best dairy!"

    )


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("Добавить запись"), add_note_start)],
        states={
            ADD_TEXT: [
                MessageHandler(filters.Regex("^Отмена$"), cancel),  # Добавляем сюда обработку кнопки "Отмена"
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_text)
            ],
            ADD_PHOTO: [
                MessageHandler(filters.Regex("^Отмена$"), cancel),  # Обработка "Отмена" в состоянии ADD_PHOTO
                MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), add_photo)
            ],
            ADD_REMINDER: [
                MessageHandler(filters.Regex("^Отмена$"), cancel),  # Обработка "Отмена" в состоянии ADD_REMINDER
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_reminder)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), cancel)]  # Обработка "Отмена" как fallback
    )
    view_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("Просмотр записей"), view_note_start)],
        states={
            VIEW_NOTES: [
                MessageHandler(filters.Text("Просмотр всех записей"), view_all_note),
                MessageHandler(filters.Text("Назад"), view_note_start),
                MessageHandler(filters.Text("За дату"), one_date_note),
                # MessageHandler(filters.Text("За период"), view_range_date_note),
                MessageHandler(filters.Text("Отмена"), cancel)
            ],
            VIEW_ONE_DATE_NOTES: [
                MessageHandler(filters.Text("Назад"), view_note_start),
                MessageHandler(filters.Text("Отмена"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, view_one_date_note)

            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), cancel)]  # Обработка "Отмена" как fallback
    )



    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", view_info))
    app.add_handler(CommandHandler("about", about_dairy))
    # В main() добавляем новый обработчик
    app.add_handler(CommandHandler("cleanup", cleanup_command))
    app.add_handler(conv_handler)
    app.add_handler(view_conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()