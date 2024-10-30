import sqlite3

def add_column(conn, column_sql):
    try:
        cursor = conn.cursor()
        cursor.execute(column_sql)
        conn.commit()
        print("Столбец добавлен.")
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении столбца: {e}")
#ew
if __name__ == "__main__":
    database = "data.db"
    conn = create_connection(database)
    if conn is not None:
        add_column(conn, "ALTER TABLE users ADD COLUMN email TEXT;")
        conn.close()
