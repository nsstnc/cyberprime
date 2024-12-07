from datetime import datetime

import pytz
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import re
from database.database import database
from database.models import TaskType
from keyboards.user_keyboards import *
from utils import get_results_message
router = Router()


@router.message(F.text == "Общие результаты")
async def get_user_results(message: Message):
    text = await get_results_message()
    text = "Общие очки фракций" + text
    await message.answer(text)


@router.message(F.text == "Мои результаты")
async def get_user_results(message: Message):
    user_tasks = await database.get_user_tasks(message.from_user.id)

    text = ""
    for user_task in user_tasks:
        text += (
            f"Задание {user_task.day}. Баллы: {user_task.points}\n"
        )

    user = await database.get_user_by_id(message.from_user.id)
    fraction_points = await database.get_fraction_points(user.fraction_id)

    text += f"\n\nОчки Вашей фракции: {fraction_points}"
    await message.answer(text)


@router.message(F.text == "Получить текущее задание")
async def get_current_task(message: Message):
    event_date_start = await database.get_date_start()
    # если дата старта не задана, ничего не делаем
    if event_date_start is None:
        pass
    # если дата задана, то выполняем получаем задачу, согласно текущему дню
    else:
        moscow_tz = pytz.timezone("Europe/Moscow")
        now_in_moscow = datetime.now(moscow_tz)

        # Вычисляем номер текущего дня с учётом начальной даты события
        current_event_day = (now_in_moscow.date() - event_date_start).days + 1
        if current_event_day > 5:
            # ивент закончился
            await message.answer("К сожалению, наш ивент подошел к концу!")
        elif current_event_day < 1:
            # ивент еще не начался
            await message.answer("К сожалению, ивент еще не начался!")
        else:
            current_task = await database.get_user_task_by_day(user_id=message.from_user.id, day=current_event_day)
            pprint(current_task)
            text = (
                f"Задание {current_event_day}. {'Фотоохота' if current_task.type == TaskType.PHOTOHUNTING else 'Головоломка'}\n\n"
                f"{current_task.description}"
            )
            await message.answer(text)


@router.callback_query(lambda c: c.data.startswith("set_fraction:"))
async def set_fraction(callback_query: CallbackQuery):
    await callback_query.answer("Выбрано")

    fraction_id, user_login = callback_query.data.split(":")[1:]

    await database.register_user(callback_query.from_user.id, user_login, int(fraction_id))

    fraction = await database.get_fraction_by_id(int(fraction_id))
    await callback_query.message.answer(
        f"Ты вступил в фракцию {fraction.fraction_name}! Теперь ты сражаешься за свою честь и за свой город.",
        reply_markup=main_user_keyboard)


@router.callback_query(lambda c: c.data.startswith("set_branch:"))
async def set_branch(callback_query: CallbackQuery):
    await callback_query.answer("Выбрано")

    city_name, user_login = callback_query.data.split(":")[1:]

    await callback_query.message.answer(
        f"Выбери свой филиал.", reply_markup=await get_branch_select_keyboard(city_name, user_login))
