import sqlite3
from database.connection import create_connection
from datetime import datetime
from config import generate_photo_path




def create_tables():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT NOT NULL,
                phone_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            print("Таблица 'users' успешно создана")

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS diary_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content TEXT NOT NULL,
                photo_path TEXT,
                reminder_time TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )''')
            conn.commit()
            print("Таблица 'diary_entries' успешно создана")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            conn.close()



# Создание таблицы аудита
def create_audit_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER,
                    action TEXT NOT NULL,
                    user_created_at TIMESTAMP,
                    entry_created_at TIMESTAMP,
                    old_content TEXT,
                    new_content TEXT,
                    phone_number TEXT,
                    photo_path TEXT,           -- Ссылка на фото (опционально)
                    reminder_time TIMESTAMP,    -- Время напоминания (опционально)
                    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Таблица аудита успешно создана.")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблицы аудита: {e}")
        finally:
            conn.close()
#create_tables()
#create_audit_table()
# Функция для добавления записи в лог
def add_audit_log(
    telegram_id,
    action,
    user_created_at,
    entry_created_at=None,
    old_content=None,
    new_content=None,
    phone_number=None,
    photo_path=None,        # Добавлено
    reminder_time=None      # Добавлено
):
    # Логика сохранения информации об аудите
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = """
            INSERT INTO audit_logs (
                telegram_id, action, user_created_at, entry_created_at, old_content, new_content, phone_number, photo_path, reminder_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (telegram_id, action, user_created_at, entry_created_at, old_content, new_content, phone_number, photo_path, reminder_time))
            conn.commit()
            print("Лог аудита успешно добавлен")
        except sqlite3.Error as e:
            print(f"Произошла ошибка при добавлении лога аудита: {e}")
        finally:
            conn.close()





def add_user(telegram_id, username, phone_number):
    conn = create_connection()
    if conn:
        try:
            sql = "INSERT INTO users (telegram_id, username, phone_number) VALUES (?, ?, ?)"
            cursor = conn.cursor()
            cursor.execute(sql, (telegram_id, username, phone_number))
            user_id = cursor.lastrowid
            conn.commit()
            print("Пользователь успешно добавлен")
            add_audit_log(
                telegram_id=telegram_id,
                entry_created_at=username,
                phone_number=phone_number,
                action="create_user",
                user_created_at=datetime.now()  # можно также запросить из таблицы, если нужно точное значение
            )
            return user_id
        except sqlite3.Error as e:
            print((f"Произошла ошибка {e}"))
        finally:
            conn.close()


def add_diary_entry(telegram_id, content, photo=None, reminder_time=None):
    conn = create_connection()
    if conn:
        try:
            # Создаем путь для сохранения фотографии
            photo_path = generate_photo_path(telegram_id) if photo else None

            # Сохраняем фото, если оно предоставлено
            if photo:
                with open(photo_path, "wb") as file:
                    file.write(photo)

            # Добавление записи в таблицу diary_entries
            sql = "INSERT INTO diary_entries (telegram_id, content, photo_path, reminder_time) VALUES (?, ?, ?, ?)"
            cursor = conn.cursor()
            # Передаем photo_path, а не сам файл
            cursor.execute(sql, (telegram_id, content, photo_path, reminder_time))
            entry_id = cursor.lastrowid
            conn.commit()
            print("Запись успешно добавлена")

            # Логирование действия в таблицу audit_log
            add_audit_log(
                telegram_id=telegram_id,
                action="added_diary_entry",
                user_created_at=datetime.now(),
                entry_created_at=datetime.now(),
                new_content=content,
                phone_number=None,
                photo_path=photo_path,  # Путь сохраняется в логах
                reminder_time=reminder_time  # Если напоминание не нужно, передаем None
            )
            return entry_id

        except sqlite3.Error as e:
            print(f"Произошла ошибка {e}")

        finally:
            conn.close()

# def add_diary_entry (telegram_id, content, photo=None, reminder_time=None):
#     conn = create_connection()
#     if conn:
#         try:
#             photo_path = generate_photo_path(telegram_id) if photo else None
#             if photo:
#                 with open(photo_path, "wb") as file:
#                     file.write(photo)
#             cursor = conn.cursor()
#             cursor.execute("SELECT created_at FROM users WHERE telegram_id = ?", (telegram_id,))
#             user_created_at = cursor.fetchone()
#             if user_created_at:
#                 user_created_at = user_created_at[0]
#             else:
#                 print("Пользователь не найден")
#                 return None
#
#             # Добавление новой записи в дневник
#             sql = "INSERT INTO diary_entries (telegram_id, content, photo_path, reminder_time) VALUES (?, ?, ?, ?)"
#             cursor = conn.cursor()
#             cursor.execute(sql, (telegram_id, content, photo, reminder_time))
#             entry_id = cursor.lastrowid
#             conn.commit()
#             print("Запись успешно добавлена")
#
#             # Логирование действия
#             add_audit_log(
#                 telegram_id=telegram_id,
#                 action="added_diary_entry",
#                 user_created_at=user_created_at,
#                 entry_created_at=datetime.now(),
#                 new_content=content,
#                 phone_number=None,
#                 photo_path=photo_path,
#                 reminder_time=reminder_time# Если номер не нужен
#             )
#             return entry_id
#         except sqlite3.Error as e:
#             print(f"Произошла ошибка {e}")
#         finally:
#             conn.close()

def view_all_notes (telegram_id):
    conn=create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM diary_entries WHERE telegram_id = ?", (telegram_id,))
            entries = cursor.fetchall()
            if entries:
                return entries
            else:
                return []
        except sqlite3.Error as e:
            print(f"Возникла ошибка {e}")
            return None
        finally:
            conn.close()


def filter_diary_by_date(telegram_id, date):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Выполняем запрос с параметрами telegram_id и date
            cursor.execute("SELECT * FROM diary_entries WHERE telegram_id = ? AND DATE(date) = DATE(?)", (telegram_id, date))
            entries = cursor.fetchall()

            # Проверяем, есть ли записи
            if entries:
                return entries
            else:
                return []

        except sqlite3.Error as e:
            print(f"Произошла ошибка {e}")
            return None
        finally:
            conn.close()


def filter_diary_by_date_range (telegram_id, date_start, date_end):
    conn=create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM diary_entries WHERE telegram_id = ? AND DATE(date) BETWEEN DATE(?) AND DATE(?)", (telegram_id, date_start, date_end))
            entries = cursor.fetchall()
            result = []
            if entries:
                for entry in entries:
                    result.append(f"ID:{entry[0]}, Дата: {entry[2]}, Запись: {entry[3]}")
                return result
            else:
                print("Записей за указанный период не найдено.")
        except sqlite3.Error as e:
            print(f"Произошла ошибка {e}")
        finally:
            conn.close()
    return []


def fetch_user_created_at(telegram_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT created_at FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def build_update_query(entry_id, telegram_id, **kwargs):
    fields = [f"{field} = ?" for field in kwargs.keys()]
    values = list(kwargs.values()) + [entry_id, telegram_id]
    query = f"UPDATE diary_entries SET {', '.join(fields)} WHERE entry_id = ? AND telegram_id = ?"
    return query, values

def update_diary_entry(telegram_id, entry_id, **kwargs):
    user_created_at = fetch_user_created_at(telegram_id)
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            update_query, values = build_update_query(entry_id, telegram_id, **kwargs)
            cursor.execute(update_query, values)
            conn.commit()

            if cursor.rowcount > 0:
                print("\nЗапись успешно обновлена.")
                add_audit_log(
                    telegram_id=telegram_id,
                    action="update_diary_entry",
                    user_created_at=user_created_at,
                    entry_created_at=datetime.now(),
                    old_content=kwargs.get("old_content"),
                    new_content=kwargs.get("content"),
                    phone_number=None,
                    photo_path=kwargs.get("photo_path"),
                    reminder_time=kwargs.get("reminder_time")
                )
            else:
                print("Запись с таким ID не найдена.")
        except sqlite3.Error as e:
            print(f"Произошла ошибка {e}")
        finally:
            conn.close()


def delete_user(telegram_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            entry = cursor.fetchone()
            if entry:
                entry_created_at =  entry[2]
                phone_number = entry[3]
                old_content = entry[4]

                cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
                cursor.execute("DELETE FROM diary_entries WHERE telegram_id = ?", (telegram_id,))
                conn.commit()
                print("Запись успешно удалена")
                add_audit_log(
                    telegram_id=telegram_id,
                    action="delete_user",
                    user_created_at=None,  # Если user_created_at не нужен, можно убрать
                    entry_created_at=entry_created_at,
                    old_content=old_content,
                    new_content=None,
                    phone_number=phone_number
                )
            else:
                print("Запись с таким ID не найдена.")
        except sqlite3.Error as e:
            print(f"Произошла ошибка {e}")
        finally:
            conn.close()
