from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from database.database import database

main_admin_buttons = [
    # [KeyboardButton(text="Добавить задание")],
    [KeyboardButton(text="Начислить баллы")],
    [KeyboardButton(text="Список заданий")],
    [KeyboardButton(text="Задать дату старта")],
]
main_admin_keyboard = ReplyKeyboardMarkup(keyboard=main_admin_buttons, resize_keyboard=True)


async def get_choose_task_type_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Фотоохота",
                                 callback_data=f"add_photohunting_task:")
        ],
        [
            InlineKeyboardButton(text="Головоломка",
                                 callback_data=f"add_puzzle_task:")
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
