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


def add_column(conn, column_sql):
    try:
        cursor = conn.cursor()
        cursor.execute(column_sql)
        conn.commit()
        print("Столбец добавлен.")
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении столбца: {e}")


if __name__ == "__main__":
    database = "data.db"  # имя файла вашей базы данных SQLite
    conn = create_connection(database)

    if conn is not None:
        # SQL-запрос для добавления столбца email в таблицу users
        column_sql = "ALTER TABLE users ADD COLUMN email TEXT;"

        # Вызываем функцию с SQL-запросом
        add_column(conn, column_sql)

        conn.close()
