import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.enums import ParseMode
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from handlers import user, admin
from config import ADMINS, PATH_TO_GOOGLE_SERVICE_SECRET_JSON, SPREADSHEET_URL
from keyboards.user_keyboards import get_city_select_keyboard
from keyboards.admin_keyboards import main_admin_keyboard
from database.database import database
from scheduler import scheduler, update_tasks, notificate_for_task_completion, notificate_for_fractions_result, write_report
from apscheduler.triggers.cron import CronTrigger
from GoogleSpreadSheet import GoogleSpreadSheet

load_dotenv()

google_client = GoogleSpreadSheet(PATH_TO_GOOGLE_SERVICE_SECRET_JSON)

# Получение токена
TOKEN = getenv("TOKEN")

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_routers(user.router, admin.router)


class RegistrationStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_city = State()


# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id in ADMINS:
        await message.answer("Добро пожаловать, администратор!", reply_markup=main_admin_keyboard)
    else:
        await message.answer("Привет, странник! Добро пожаловать в наше приключение!")
        await message.answer("Введи свой логин или номер телефона в системе КиберПрайд:")

        # Устанавливаем состояние ожидания логина
        await state.set_state(RegistrationStates.waiting_for_login)


# Обработчик для получения логина
@dp.message(RegistrationStates.waiting_for_login, F.text)
async def process_login(message: Message, state: FSMContext) -> None:
    login = message.text.strip()
    user_exists = await database.check_user_exists(login)

    if user_exists:
        await message.answer(f"Такой логин уже зарегистрирован")
    else:
        await state.update_data(login=login)

        await message.answer(f"Ваш логин: {login}\nВыберите свой город:",
                             reply_markup=await get_city_select_keyboard(login))

    await state.clear()


from database.db_init import db_init


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    scheduler.start()
    scheduler.add_job(update_tasks, args=[bot], trigger=CronTrigger(hour=0, minute=0))
    # scheduler.add_job(update_tasks, args=[bot], trigger=IntervalTrigger(seconds=5))
    scheduler.add_job(notificate_for_task_completion, args=[bot], trigger=CronTrigger(hour=18, minute=0))
    # scheduler.add_job(notificate_for_task_completion, args=[bot], trigger=IntervalTrigger(seconds=5))
    scheduler.add_job(notificate_for_fractions_result, args=[bot], trigger=CronTrigger(hour=15, minute=0))
    # scheduler.add_job(notificate_for_fractions_result, args=[bot], trigger=IntervalTrigger(seconds=5))
    scheduler.add_job(write_report, args=[google_client, SPREADSHEET_URL], trigger=IntervalTrigger(minutes=5))
    # asyncio.create_task(check_and_send_notifications(bot))
    if not await database.is_exist():
        await database.initialize()
    await db_init(database)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
