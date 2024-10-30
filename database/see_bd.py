import sqlite3


def create_connection(db_file):
    """Создаём подключение к SQLite базе данных"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Успешное подключение к БД")
    except sqlite3.Error as e:
        print(f"Ошибка подключения к БД: {e}")
    return conn


def show_tables(conn):
    """Отображаем список таблиц и столбцов в каждой таблице"""
    try:
        cursor = conn.cursor()

        # Получаем список всех таблиц в базе данных
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            print(f"\nТаблица: {table_name}")

            # Получаем структуру (столбцы) для каждой таблицы
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            for column in columns:
                print(f"  - {column[1]} ({column[2]})")  # column[1] - название столбца, column[2] - тип данных

    except sqlite3.Error as e:
        print(f"Ошибка при отображении структуры базы данных: {e}")


if __name__ == "__main__":
    database = "data.db"  # имя файла вашей базы данных SQLite
    conn = create_connection(database)

    if conn is not None:
        show_tables(conn)
        conn.close()
