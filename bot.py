# bot.py
import logging
from config import LOG_FILE_PATH
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from database.models import add_user


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),  # Запись логов в logs_py/bot.log
        logging.StreamHandler()  # Продолжаем вывод в консоль
    ]
)
logger = logging.getLogger(__name__)
w

async def start (update: Update, context: CallbackContext):
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
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", view_info))
    app.add_handler(CommandHandler("about", about_dairy))

    app.run_polling()

if __name__ == "__main__":
    main()
