import sqlite3

def create_connection(datafile):
    conn = None
    try:
        conn = sqlite3.connect(datafile)
        print("Успешное подключение к БД")
    except sqlite3.Error as e:
        print(f"Произошла ошибка {e}")
    return conn


def create_table (conn):
    try:
        sql_create_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        );
        """
        cursor = conn.cursor()
        cursor.execute(sql_create_table)
        conn.commit()
        print("Табличка успешно создана")
    except sqlite3.Error as e:
        print(f"Произошла ошибка {e}")
        

if __name__ == "__main__":
    db_file = "data.db"
    conn = create_connection(db_file)
    if conn is not None:
        create_table(conn)
        conn.close()

