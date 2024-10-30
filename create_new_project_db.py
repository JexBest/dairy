import sqlite3

def create_connection(database):
    """Создает подключение к базе данных SQLite (создаёт файл, если его нет)"""
    conn = None
    try:
        conn = sqlite3.connect(database)
        print("Успешное подключение к БД")
        return conn
    except sqlite3.Error as e:
        print(f"Произошла ошибка {e}")
    return conn

def initialize_db(conn):
    """Создаёт таблицы users и entries, если их нет"""
    try:
        cursor = conn.cursor()
        # Создание таблицы пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,   
            username TEXT,                
            phone_number TEXT,             
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Создание таблицы записей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            content TEXT,
            reminder_date TIMESTAMP,
            is_completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        );
        """)
        conn.commit()
        print("Таблицы инициализированы")
    except sqlite3.Error as e:
        print(f"Произошла ошибка при инициализации БД: {e}")

# Основная часть
if __name__ == "__main__":
    db_file = "data.db"
    conn = create_connection(db_file)
    if conn is not None:
        initialize_db(conn)
        conn.close()
