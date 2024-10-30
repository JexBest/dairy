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


def get_all_users(database):
    conn = connect_to_bd(database)
    if conn:
        try:
            sql = "SELECT * FROM users"  # Запрос на получение всех пользователей
            cursor = conn.cursor()
            cursor.execute(sql)
            users = cursor.fetchall()  # Получаем все строки из результата запроса
            for user in users:
                print(user)  # Выводим каждую запись
        except sqlite3.Error as e:
            print(f"Произошла ошибка {e}")
        finally:
            conn.close()  # Закрываем подключение


if __name__ == "__main__":
    db_file = "data.db"
    get_all_users(db_file)
