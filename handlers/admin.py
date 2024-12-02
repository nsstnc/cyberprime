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


@router.message(F.text == "Добавить задание")
async def start_add_supervisor(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer("Выберите тип задания", reply_markup=await get_choose_task_type_keyboard())


@router.message(F.text == "Список заданий")
async def start_add_supervisor(message: Message):
    if message.from_user.id in ADMINS:
        tasks = await database.get_all_tasks()
        print(tasks)
        text = "Задания:\n\n"
        for i in range(len(tasks)):
            text += (f"{i + 1}. {'Фотоохота' if tasks[i].type == TaskType.PHOTOHUNTING else 'Головоломка'}\n"
                     f"Описание. {tasks[i].description}\n\n"
                     f"Правильный ответ: {tasks[i].answer}\n\n"
                     )

        await message.answer(text)


@router.callback_query(lambda c: c.data.startswith("add_photohunting_task:"))
async def add_photohunting_task(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Выбрано")

    await callback_query.message.answer(
        f"Введите описание задания для фотоохоты")
    # Устанавливаем состояние ожидания описания задания
    await state.set_state(PhotoHuntingStates.waiting_for_description)


@router.message(PhotoHuntingStates.waiting_for_description, F.text)
async def description_photohunting(message: Message, state: FSMContext) -> None:
    description = message.text.strip()
    await database.add_photohunting_task(description)
    await message.answer(f"Задание записано\n\nОписание задания:\n{description}")
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("add_puzzle_task:"))
async def add_puzzle_task(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Выбрано")

    await callback_query.message.answer(
        f"Введите описание задания для головоломки")
    # Устанавливаем состояние ожидания описания задания
    await state.set_state(PuzzleStates.waiting_for_description)


@router.message(PuzzleStates.waiting_for_description, F.text)
async def description_puzzle(message: Message, state: FSMContext) -> None:
    description = message.text.strip()

    await state.update_data(description=description)
    await message.answer(
        f"Введите ответ на задание головоломки")
    # Устанавливаем состояние ожидания ответа к заданию
    await state.set_state(PuzzleStates.waiting_for_answer)


@router.message(PuzzleStates.waiting_for_answer, F.text)
async def description_puzzle(message: Message, state: FSMContext) -> None:
    answer = message.text.strip()

    data = await state.get_data()
    description = data.get("description")

    await database.add_puzzle_task(description, answer)

    await message.answer(f"Задание записано\n\nОписание задания:\n{description}\n\nОтвет: {answer}")

    await state.clear()
