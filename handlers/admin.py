from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import re
from database.database import database
from database.models import *
from config import ADMINS
from keyboards.admin_keyboards import get_choose_task_type_keyboard

router = Router()


class PhotoHuntingStates(StatesGroup):
    waiting_for_description = State()


class PuzzleStates(StatesGroup):
    waiting_for_description = State()
    waiting_for_answer = State()


class DateStates(StatesGroup):
    waiting_for_date = State()


class AddPointsStates(StatesGroup):
    waiting_for_points = State()


@router.message(F.text == "Начислить баллы")
async def add_points_step1(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer(
            "Для начисления баллов отправьте сообщение в формате: &lt;user_task_id&gt; &lt;кол-во баллов&gt;\n\nНапример:\n35 10",
            parse_mode="HTML"
        )
        await state.set_state(AddPointsStates.waiting_for_points)


@router.message(AddPointsStates.waiting_for_points, F.text)
async def add_points_step2(message: Message, state: FSMContext) -> None:
    command_message = message.text.strip()
    try:
        user_task_id, points = map(int, command_message.split(" "))

        # Начисляем баллы в БД
        user_tgid = await database.add_points(user_task_id, points)
        await message.answer(f"Баллы начислены пользователю: {user_tgid}")
        await message.bot.send_message(user_tgid, f"Задание проверено, фракция получает {points} очков.")
        await state.clear()
    except ValueError:
        # Если формат неверный, сообщаем пользователю
        await message.answer(
            "Неверный формат сообщения. Пожалуйста, вызовите команду еще раз и введите сообщение в нужном формате")
        await state.clear()
    except Exception as e:
        await message.answer(
            "Не удалось добавить баллы. Проверьте, верно ли введен user_task_id")
        await state.clear()


@router.message(F.text == "Добавить задание")
async def start_add_supervisor(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer("Выберите тип задания", reply_markup=await get_choose_task_type_keyboard())


@router.message(F.text == "Список заданий")
async def start_add_supervisor(message: Message):
    if message.from_user.id in ADMINS:
        tasks = await database.get_all_tasks()
        print(tasks)
        for task in tasks:
            text = f"Задание/день {task.task_id}.\n"

            if task.fraction_name is not None:
                text += f"Фракция: {task.fraction_name}\n"

            if task.description is not None:
                text += f"Описание: {task.description}\n\n"

            if task.answer is not None:
                text += f"Правильный ответ: {task.answer}\n\n"

            if task.hint is not None:
                text += f"Подсказка: {task.hint}\n\n"

            await message.answer(text)


@router.message(F.text == "Задать дату старта")
async def set_date_start(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Введите дату старта ивента в формате дд.мм.гггг")
        await state.set_state(DateStates.waiting_for_date)


@router.message(DateStates.waiting_for_date, F.text)
async def set_date_start_step(message: Message, state: FSMContext) -> None:
    date_start_text = message.text.strip()
    try:
        # Преобразуем текст в объект datetime.date
        date_start = datetime.strptime(date_start_text, "%d.%m.%Y").date()

        # Записываем дату в базу данных
        await database.set_date_start(date_start)
        await message.answer(f"Дата начала успешно установлена: {date_start_text}")
        await state.clear()
    except ValueError:
        # Если формат неверный, сообщаем пользователю
        await message.answer(
            "Неверный формат даты. Пожалуйста, вызовите команду еще раз и введите дату в формате дд.мм.гггг")
        await state.clear()


# @router.callback_query(lambda c: c.data.startswith("add_photohunting_task:"))
# async def add_photohunting_task(callback_query: CallbackQuery, state: FSMContext):
#     await callback_query.answer("Выбрано")
#
#     await callback_query.message.answer(
#         f"Введите описание задания для фотоохоты")
#     # Устанавливаем состояние ожидания описания задания
#     await state.set_state(PhotoHuntingStates.waiting_for_description)
#
#
# @router.message(PhotoHuntingStates.waiting_for_description, F.text)
# async def description_photohunting(message: Message, state: FSMContext) -> None:
#     description = message.text.strip()
#     await database.add_photohunting_task(description)
#     await message.answer(f"Задание записано\n\nОписание задания:\n{description}")
#     await state.clear()
#
#
# @router.callback_query(lambda c: c.data.startswith("add_puzzle_task:"))
# async def add_puzzle_task(callback_query: CallbackQuery, state: FSMContext):
#     await callback_query.answer("Выбрано")
#
#     await callback_query.message.answer(
#         f"Введите описание задания для головоломки")
#     # Устанавливаем состояние ожидания описания задания
#     await state.set_state(PuzzleStates.waiting_for_description)
#
#
# @router.message(PuzzleStates.waiting_for_description, F.text)
# async def description_puzzle(message: Message, state: FSMContext) -> None:
#     description = message.text.strip()
#
#     await state.update_data(description=description)
#     await message.answer(
#         f"Введите ответ на задание головоломки")
#     # Устанавливаем состояние ожидания ответа к заданию
#     await state.set_state(PuzzleStates.waiting_for_answer)
#
#
# @router.message(PuzzleStates.waiting_for_answer, F.text)
# async def description_puzzle(message: Message, state: FSMContext) -> None:
#     answer = message.text.strip()
#
#     data = await state.get_data()
#     description = data.get("description")
#
#     await database.add_puzzle_task(description, answer)
#
#     await message.answer(f"Задание записано\n\nОписание задания:\n{description}\n\nОтвет: {answer}")
#
#     await state.clear()
