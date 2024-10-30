import sqlite3


def connect_to_bd(database):
    conn = None
    try:
        conn = sqlite3.connect(database)
        print("Мы успешно подключились к БД")
        return conn
    except sqlite3.Error as e:
        print(f"Произошла ошибка {e}")
        return None
def alter_table(conn):
    try:
        cursor = conn.cursor()

        # Шаг 1: Создаем новую таблицу с нужной структурой
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_new (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Шаг 2: Переносим данные из старой таблицы в новую
        cursor.execute("""
        INSERT INTO users_new (user_id, username, email, created_at)
        SELECT id, username, email, created_at FROM users;
        """)

        # Шаг 3: Удаляем старую таблицу
        cursor.execute("DROP TABLE users;")

        # Шаг 4: Переименовываем новую таблицу в старое имя
        cursor.execute("ALTER TABLE users_new RENAME TO users;")

        conn.commit()
        print("Таблица успешно изменена")
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    db_file = "data.db"
    conn = connect_to_bd(db_file)
    if conn:
        alter_table(conn)
        conn.close()