import asyncio
from datetime import datetime, timedelta
from pprint import pprint
import random
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.database import database
import pytz

from utils import get_results_message

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


async def get_free_tasks_for_user(old_user_tasks, all_tasks):
    """
    Выдает все задания, которые пользователь еще не получал
    :param old_user_tasks:
    :param all_tasks:
    :return:
    """
    old_task_ids = {task.task_id for task in old_user_tasks}
    free_tasks = [task for task in all_tasks if task.get("id") not in old_task_ids]

    return free_tasks


async def update_tasks(bot: Bot):
    """Задача, по добавлению заданий выполняемая ежедневно."""
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
        if current_day == 6:
            # ивент закончился
            all_users = await database.get_all_users()
            text = await get_results_message()
            text = "Наш ивент подошел к концу! Ознакомьтесь с результатами:\n" + text
            for user in all_users:
                try:
                    await bot.send_message(user.tgid, text)
                except:
                    pass

            # скидываем дату начала ивента чтобы выполнение отложенных функций прекратилось
            date_start = datetime.strptime("01.01.2024", "%d.%m.%Y").date()
            # Записываем дату в базу данных
            await database.set_date_start(date_start)

        elif current_day < 1:
            # ивент еще не начался
            pass
        else:
            task_variants = await database.get_task_variants_by_day(current_day)
            pprint(task_variants)
            users = await database.get_all_users()
            for user in users:
                old_user_tasks = await database.get_user_tasks_by_day(user.tgid, current_day)
                random_task = random.choice(await get_free_tasks_for_user(old_user_tasks, task_variants))
                await database.create_user_task(user_id=user.tgid,
                                                task_id=random_task.get("id"),
                                                day=current_day)
            # for user_with_task in users_with_tasks:
            #     task_type = user_with_task.get('task_type')
            #
            #     tasks = await database.get_all_tasks_by_type(task_type)
            #     old_user_tasks = await database.get_user_tasks_by_type(user_with_task.get('tgid'), task_type)
            #
            #     if tasks:
            #         random_task = random.choice(await get_free_tasks_for_user(old_user_tasks, tasks))
            #
            #         await database.create_user_task(user_id=user_with_task.get('tgid'),
            #                                         task_id=random_task.id,
            #                                         day=user_with_task.get('day'), )
            #     else:
            #         print("Задачи не заполнены")

    print(f"Ежедневная задача выполнена в {datetime.now()}")
