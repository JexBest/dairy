import sqlite3


def connect_to_bd (database):
    conn = None
    try:
        conn = sqlite3.connect(database)
        print("Мы успешно подключились к БДшечке")
        return conn
    except sqlite3.Error as e:
        print(f"Произошла ошибка {e}")
        return None





def create_user (database, username, email, password):
    conn = connect_to_bd(database)
    if conn:
        try:
            sql = "INSERT INTO users (username, email, password) VALUES (?, ? ,?)"
            cursor = conn.cursor()
            cursor.execute(sql, (username, email, password))
            conn.commit()
            print("Пользователь успешно добавлен")
        except sqlite3.Error as e:
            print(f"Произошла ошибка {e}")
        finally:
            conn.close()
def user_param():
    db_file = "data.db"
    username = input("Введите имя пользователя: ")
    email = input("Введите email пользователя: ")
    password = input("Введите пароль пользователя: ")
    create_user(db_file, username, email, password)






if __name__ == "__main__":
    user_param()