import sqlite3

from database.models import add_user, add_diary_entry

telegram_id = input("Нам нужно тут получить user_id, но без реального телеграмма будем баловаться на тестовых значения, так что вводим тут id похожий на телеграмм: ")
username = input("Тут мы получаем username, я думаю это будет что-то на подобии @jexbest: ")
while True:
    phone_number = input("Ввести номер состоящий из цифр: ")
    try:
        phone_number = int(phone_number)
        print(f"Номер {phone_number} успешно записался в переменную 'phone_number'")
        break
    except ValueError:
        print("Номер обязательно должен содержать только цифры! Повторите ввод")



content = input("Введите свою запись для дневника, это пока тестовый режим: ")

users = add_user(telegram_id, username, phone_number)
diary_entries = add_diary_entry(telegram_id, content, photo=None, reminder_time=None)


from database.connection import create_connection

conn = create_connection()
if conn:
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        user = cursor.fetchone()
        print("\nПроверка добавленного пользователя:")
        print(user)
        cursor.execute("SELECT * FROM diary_entries")
        entry = cursor.fetchone()
        print("\nПроверка добавленной записи в дневник:")
        print(entry)
    except sqlite3.Error as e:
        print(f"Произошла ошибка {e}")
    finally:
        conn.close()