import sqlite3

from database.connection import create_connection

conn = create_connection()
if conn:
    try:
        cursor = conn.cursor()

        # Извлекаем данные из таблицы users с названиями полей
        cursor.execute(
            "SELECT * FROM users")
        users = cursor.fetchall()  # Извлекаем все записи для удобного вывода
        print("\nСодержание таблицы users:")
        for user in users:
            print(user)

        # Извлекаем данные из таблицы diary_entries с названиями полей
        cursor.execute(
            "SELECT * FROM diary_entries")
        entries = cursor.fetchall()  # Извлекаем все записи для удобного вывода
        print("\nСодержание таблицы diary_entries:")
        for entry in entries:
            print(entry)

        cursor.execute(
            "SELECT * FROM audit_logs")
        audits = cursor.fetchall()  # Извлекаем все записи для удобного вывода
        print("\nСодержание таблицы audit_log:")
        for audit in audits:
            print(audit)


    except sqlite3.Error as e:
        print(f"Произошла ошибка {e}")
    finally:
        conn.close()

