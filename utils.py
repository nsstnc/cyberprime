import pandas as pd

from database.database import database
import os


async def get_results_message() -> str:
    fractions_points = await database.get_fractions_points()
    print(fractions_points)
    text = ""
    for fraction_id, fraction_name, points in sorted(fractions_points, key=lambda x: x[2], reverse=True):
        text += f"\n{fraction_name}: {points}"
    return text


async def get_absolute_path(file_path):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.normpath(os.path.join(BASE_DIR, file_path))
    return abs_path


async def create_report(drive_client):
    users = await database.get_all_users()

    data_points = []

    for user in users:
        login = user.login
        fraction = await database.get_fraction_by_id(user.fraction_id)
        fraction_name = fraction.fraction_name

        days_points = []
        for day in range(1, 5 + 1):
            user_task_by_day = await database.get_user_task_by_day(user.tgid, day)
            if user_task_by_day:
                days_points.append(user_task_by_day.points)
            else:
                days_points.append(0)

        total_points = sum(days_points)
        data_points.append([login, fraction_name, *days_points, total_points])

    df_points = pd.DataFrame(data_points, columns=[
        'логин', 'фракция', 'задание 1', 'задание 2',
        'задание 3', 'задание 4', 'задание 5', 'итог'
    ])

    distributed_tasks = await database.get_distributed_tasks()
    data_tasks = []

    for task in distributed_tasks:
        if task.result_url:
            # Загружаем файл в Google Drive и получаем публичный URL
            public_url = drive_client.upload_file_to_drive(task.result_url, f"task_{task.id}.jpg")
            answer = f'=IMAGE("{public_url}")'
        else:
            answer = task.user_answer

        data = [task.id, task.user_id, task.points, task.day, answer]
        data_tasks.append(data)

    df_answers = pd.DataFrame(data_tasks, columns=[
        'user_task_id', 'id пользователя', 'очки', 'день',
        'ответ'
    ])

    df_dict = {
        "Баллы": df_points,
        "Решения": df_answers,
    }

    return df_dict