# main.py

import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import user
from database.db import init_db

load_dotenv()  # Загружаем переменные из .env файла

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user.router)

    await init_db()  # создаем таблицы
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
# Запуск бота
