import sqlite3
from database.connection import create_connection
from datetime import datetime
from config import generate_photo_path

conn = create_connection()
if conn:
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM diary_entries WHERE entry_id = 9")
        conn.commit()
        print("Че-то удалилось!")
    except sqlite3.Error as e:
        print(f"Ошибочка {e}")
    finally:
        conn.close()
