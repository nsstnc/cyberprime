from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import database


async def get_city_select_keyboard(user_login) -> InlineKeyboardMarkup:
    fractions = await database.get_fractions()
    buttons = []
    for fraction in fractions:
        row_buttons = [
            InlineKeyboardButton(text=str(fraction.city_name), callback_data=f"set_fraction:{fraction.id}:{user_login}")
        ]
        buttons.append(row_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)
