from database.connection import create_connection
from database.models import filter_diary_by_date_range, update_diary_entry, filter_diary_by_date, add_diary_entry, delete_user




# telegram_id = input("Для тестового запроса введите телеграмм id: ")
# date = input("Введите дату за которую вы хотите найти записи в формате 'ГГГГ-ММ-ДД'")
# entries = filter_diary_by_date(telegram_id, date)
# content = input("Для тестового текст: ")
#
# diary_entries = add_diary_entry(telegram_id, content)


#посмотрим записи и запомним для работы с ними их ID
# telegram_id = input("Для тестового запроса введите телеграмм id: ")
# date_start = input("Введите начальную дату за которую вы хотите найти записи в формате 'ГГГГ-ММ-ДД': ")
# date_end = input("Введите конечную дату за которую вы хотите найти записи в формате 'ГГГГ-ММ-ДД': ")
# entries = filter_diary_by_date_range (telegram_id, date_start, date_end)
#
# telegram_id = input("Для тестового запроса введите телеграмм id: ")
# entry_id = input("Введите ID записи для редактирования: ")
#
# # Спрашиваем, что пользователь хочет изменить
# new_content = input("Введите новый комментарий (или оставьте пустым): ").strip()
# new_photo_path = input("Введите новую ссылку на фото (или оставьте пустым): ").strip()
# new_reminder_time = input("Введите новую дату напоминания (или оставьте пустым): ").strip()
#
# # Подготавливаем аргументы для обновления
# kwargs = {}
# if new_content:
#     kwargs['content'] = new_content
# if new_photo_path:
#     kwargs['photo_path'] = new_photo_path
# if new_reminder_time:
#     kwargs['reminder_time'] = new_reminder_time
#
# # Обновляем запись, передав только изменённые значения
# update_diary_entry(telegram_id, entry_id, **kwargs)

# #тут выведем еще раз запись что бы убедиться что она изменилась
# entries = filter_diary_by_date_range (telegram_id, date_start, date_end)
# telegram_id = input("Для для удаления id: ")
#
# delete = delete_user(telegram_id)



