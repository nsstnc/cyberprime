from pprint import pprint

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import database


async def get_city_select_keyboard(user_login) -> InlineKeyboardMarkup:
    cities = await database.get_unique_cities()
    pprint(cities)
    buttons = []
    for i in range(0, len(cities) - 1, 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(cities):
                branches = await database.get_branches_by_city_name(cities[i + j].city_name)
                if branches is not None:
                    row_buttons.append(
                        InlineKeyboardButton(text=cities[i + j].city_name,
                                             callback_data=f"set_branch:{cities[i + j].city_name}:{user_login}")
                    )
                else:
                    row_buttons.append(
                        InlineKeyboardButton(text=cities[i + j].city_name,
                                             callback_data=f"set_fraction:{cities[i + j].id}:{user_login}")
                    )
        buttons.append(row_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_branch_select_keyboard(city_name, user_login) -> InlineKeyboardMarkup:
    branches = await database.get_branches_by_city_name(city_name)

    buttons = []
    for branch in branches:
        row_buttons = [
            InlineKeyboardButton(text=branch.branch_name,
                                 callback_data=f"set_fraction:{branch.id}:{user_login}")
        ]

        buttons.append(row_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)
