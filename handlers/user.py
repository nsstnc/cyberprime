from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import re
from database.database import database
from keyboards.user_keyboards import *

router = Router()


@router.callback_query(lambda c: c.data.startswith("set_fraction:"))
async def set_fraction(callback_query: CallbackQuery):
    await callback_query.answer("Выбрано")

    fraction_id, user_login = callback_query.data.split(":")[1:]

    await database.register_user(callback_query.from_user.id, user_login, int(fraction_id))

    fraction = await database.get_fraction_by_id(int(fraction_id))
    await callback_query.message.answer(
        f"Ты вступил в фракцию {fraction.fraction_name}! Теперь ты сражаешься за свою честь и за свой город.")


@router.callback_query(lambda c: c.data.startswith("set_branch:"))
async def set_branch(callback_query: CallbackQuery):
    await callback_query.answer("Выбрано")

    city_name, user_login = callback_query.data.split(":")[1:]

    await callback_query.message.answer(
        f"Выбери свой филиал.", reply_markup=await get_branch_select_keyboard(city_name, user_login))
