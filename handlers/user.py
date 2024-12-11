from datetime import datetime

import pytz
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InputFile, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import re
from database.database import database
from database.models import TaskType
from keyboards.user_keyboards import *
from utils import get_results_message, get_absolute_path, check_answer
import os

router = Router()


class AnswerStates(StatesGroup):
    waiting_for_answer = State()


@router.message(F.text == "Отправить ответ на текущее задание")
async def answer(message: Message, state: FSMContext):
    moscow_tz = pytz.timezone("Europe/Moscow")
    now_in_moscow = datetime.now(moscow_tz)
    event_date_start = await database.get_date_start()
    if event_date_start is None:
        await message.answer("Ивент еще не начался!")
    else:
        current_event_day = (now_in_moscow.date() - event_date_start).days + 1
        current_task = await database.get_user_task_by_day(user_id=message.from_user.id, day=current_event_day)

        if current_task is None:
            await message.answer(
                "У Вас нет текущего задания")
        else:
            await message.answer(
                "Присылайте свой ответ на задание следующим сообщением! "
                "Если ответ требует нескольких слов - вводите их через запятую")
            await state.set_state(AnswerStates.waiting_for_answer)


@router.message(AnswerStates.waiting_for_answer)
async def answer_step2(message: Message, state: FSMContext) -> None:
    moscow_tz = pytz.timezone("Europe/Moscow")
    now_in_moscow = datetime.now(moscow_tz)
    event_date_start = await database.get_date_start()
    if event_date_start is None:
        await message.answer("Ивент еще не начался!")
    else:
        current_event_day = (now_in_moscow.date() - event_date_start).days + 1
        current_task = await database.get_user_task_by_day(user_id=message.from_user.id, day=current_event_day)

        result_url = None
        answer = None
        try:
            # если задание - фотоохота
            if current_task.type.value == TaskType.PHOTOHUNTING.value:

                photo = message.photo[-1]  # Берем фотографию с наивысшим качеством
                file = await message.bot.get_file(photo.file_id)
                result_url = await get_absolute_path(f"images/{photo.file_id}.jpg")
                print(result_url)
                # Скачиваем файл
                await message.bot.download_file(file_path=file.file_path, destination=result_url)

            else:
                # ожидаем текст
                answer = message.text.strip()
                # проверяем ответ на правильность
                # начисляем пользователю баллы
                await database.add_points(current_task.user_task_id, check_answer(answer, current_task.answer))

            await database.set_user_answer(current_task.user_task_id, answer, result_url)

            await message.answer("Ответ принят! О результатах Вы узнаете позже")
            await state.clear()
        except Exception as e:
            print(str(e))
            await message.answer(
                "Что-то пошло не так. Проверьте условие задания, вызовите команду еще раз и отправьте корректный ответ")
            await state.clear()


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
        await message.answer("К сожалению, ивент еще не начался!")
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

            if current_task.image_url:
                image_path = await get_absolute_path(current_task.image_url)
                try:
                    photo = FSInputFile(image_path)
                    await message.bot.send_photo(chat_id=message.chat.id, photo=photo, caption=text,
                                                 reply_markup=await get_hint_keyboard(current_task.variant_id,
                                                                                      current_task.user_task_id) if current_task.hint else None)
                except FileNotFoundError:
                    print("Изображение для задания не найдено.")
            else:
                await message.answer(text, reply_markup=await get_hint_keyboard(current_task.variant_id,
                                                                                current_task.user_task_id) if current_task.hint else None)


@router.callback_query(lambda c: c.data.startswith("try_to_get_hint:"))
async def try_to_get_hint(callback_query: CallbackQuery):
    await callback_query.answer("Выбрано")

    variant_id, user_task_id = callback_query.data.split(":")[1:]

    await callback_query.message.answer(
        f"Ты хочешь воспользоваться подсказкой? Это обойдётся фракции в -10 очков. Подтверждаешь? "
        f"(Если нет, просто продолжай пользоваться ботом)",
        reply_markup=await confirm_get_hint_keyboard(variant_id, user_task_id))


@router.callback_query(lambda c: c.data.startswith("get_hint:"))
async def get_hint(callback_query: CallbackQuery):
    await callback_query.answer("Выбрано")

    variant_id, user_task_id = callback_query.data.split(":")[1:]
    hint = await database.get_hint_by_variant_id(int(variant_id))
    await database.add_points(int(user_task_id), -10)

    await callback_query.message.answer(
        f"Внимательно прочти:\n\n"
        f"{hint}\n\n"
        f"Удачи!")


@router.callback_query(lambda c: c.data.startswith("set_fraction:"))
async def set_fraction(callback_query: CallbackQuery):
    await callback_query.answer("Выбрано")

    fraction_id, user_login = callback_query.data.split(":")[1:]

    await database.register_user(callback_query.from_user.id, user_login, int(fraction_id))

    fraction = await database.get_fraction_by_id(int(fraction_id))
    await callback_query.message.answer(
        f"Ты вступил в фракцию {fraction.fraction_name}! Теперь ты сражаешься за свою честь и за свой город.",
        reply_markup=main_user_keyboard)
