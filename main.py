from database.models import create_tables
from auth.auth import auth_user  # предполагаем, что функция авторизации уже написана
from diary.diary import add_entry, view_entries

def main():
    create_tables()
    user_name = auth_user()  # Логика авторизации пользователя
    if user_name:
        # Основной цикл работы с дневником
        while True:
            command = input("Выберите действие: добавить запись, просмотреть записи, выйти: ").lower()
            if command == "добавить запись":
                add_entry(user_name)
            elif command == "просмотреть записи":
                view_entries(user_name)
            elif command == "выйти":
                print("Завершение работы")
                break
            else:
                print("Неизвестная команда")

if __name__ == "__main__":
    main()
