import sqlite3
from config import DATABASE_PATH

def create_connection(database=DATABASE_PATH):
    """Создает и возвращает подключение к базе данных."""
    conn = None
    try:
        conn = sqlite3.connect(database)
        print("Успешное подключение к БД")
    except sqlite3.Error as e:
        print(f"Ошибка подключения к БД: {e}")
    return conn
if __name__ == "__main__":
    create_connection()