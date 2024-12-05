import asyncio
from datetime import datetime, timedelta
from pprint import pprint
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.database import database
import pytz

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


async def get_free_tasks_for_user(old_user_tasks, all_tasks):
    """
    Выдает все задания, которые пользователь еще не получал
    :param old_user_tasks:
    :param all_tasks:
    :return:
    """
    old_task_ids = {task.task_id for task in old_user_tasks}
    free_tasks = [task for task in all_tasks if task.id not in old_task_ids]

    return free_tasks


async def update_tasks():
    """Задача, по добавлению заданий выполняемая ежедневно."""
    # TODO получить всех пользователей и тип задачи текущего дня каждого пользователя
    # получаем дату начала ивента
    event_date_start = await database.get_date_start()
    # если дата старта не задана, ничего не делаем
    if event_date_start is None:
        pass
    # если дата задана, то выполняем распределение задач
    else:
        moscow_tz = pytz.timezone("Europe/Moscow")
        now_in_moscow = datetime.now(moscow_tz)

        # Вычисляем номер текущего дня с учётом начальной даты события
        current_day = (now_in_moscow.date() - event_date_start).days + 1
        if current_day > 7:
            # ивент закончился
            # TODO результаты ивента
            # TODO в конце можно сдвинуть дату, чтобы не срабатывало снова
            pass
        elif current_day < 1:
            # ивент еще не начался
            pass
        else:
            users_with_tasks = await database.get_users_and_fraction_task_type(current_day)
            pprint(users_with_tasks)
            for user_with_task in users_with_tasks:
                task_type = user_with_task.get('task_type')

                tasks = await database.get_all_tasks_by_type(task_type)
                old_user_tasks = await database.get_user_tasks_by_type(user_with_task.get('tgid'), task_type)

                if tasks:
                    random_task = random.choice(await get_free_tasks_for_user(old_user_tasks, tasks))

                    await database.create_user_task(user_id=user_with_task.get('tgid'),
                                                    task_id=random_task.id,
                                                    day=user_with_task.get('day'), )
                else:
                    print("Задачи не заполнены")

    print(f"Ежедневная задача выполнена в {datetime.now()}")

