import asyncio

from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from os import getenv
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from database.database import db
import logging
import sys

load_dotenv()

# Получить значение токена
TOKEN = getenv("TOKEN")
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Привет")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # asyncio.create_task(check_and_send_notifications(bot))
    if not await db.is_exist():
        await db.initialize()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
