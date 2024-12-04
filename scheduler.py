import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler


scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


async def update_tasks():
    """Задача, по добавлению заданий выполняемая ежедневно."""
    # TODO получить всех пользователей и тип задачи текущего дня каждого пользователя
    # TODO
    # TODO
    # TODO
    # TODO
    # TODO
    # TODO
    # TODO
    # TODO
    print(f"Ежедневная задача выполнена в {datetime.now()}")



# async def wait_for_next_day():
#     """Ждет наступления следующего дня и выполняет задачу."""
#     while True:
#         now = datetime.now()
#         # Рассчитываем время до следующего дня
#         next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
#         seconds_until_next_day = (next_day - now).total_seconds()
#         print(f"Ожидание следующего дня: {seconds_until_next_day} секунд.")
#
#         # Ожидаем до наступления следующего дня
#         await asyncio.sleep(seconds_until_next_day)
#
#         # Выполняем задачу
#         await daily_task()
