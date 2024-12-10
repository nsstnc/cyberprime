from pprint import pprint

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import database

main_user_buttons = [
    [KeyboardButton(text="Получить текущее задание")],
    [KeyboardButton(text="Отправить ответ на текущее задание")],
    [KeyboardButton(text="Мои результаты")],
    [KeyboardButton(text="Общие результаты")],
]
main_user_keyboard = ReplyKeyboardMarkup(keyboard=main_user_buttons, resize_keyboard=True)


async def get_hint_keyboard(variant_id, user_task_id):
    hint_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить подсказку",
                              callback_data=f"try_to_get_hint:{variant_id}:{user_task_id}")]
    ])
    return hint_keyboard


async def confirm_get_hint_keyboard(variant_id, user_task_id):
    confirm_hint_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтверждаю. Получить подсказку",
                              callback_data=f"get_hint:{variant_id}:{user_task_id}")],
    ])
    return confirm_hint_keyboard


async def get_city_select_keyboard(user_login) -> InlineKeyboardMarkup:
    cities = await database.get_unique_cities()
    pprint(cities)
    buttons = []
    for i in range(0, len(cities) - 1, 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(cities):
                row_buttons.append(
                    InlineKeyboardButton(text=cities[i + j].city_name,
                                             callback_data=f"set_fraction:{cities[i + j].id}:{user_login}")
                )
        buttons.append(row_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

