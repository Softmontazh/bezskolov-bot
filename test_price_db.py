# test_price_db.py
# Тестовый скрипт для проверки работы с базой данных цен

import asyncio
import os
from dotenv import load_dotenv
from database.db import init_db, async_session
from database.models import Price
from sqlalchemy import select

load_dotenv()


async def test_price_operations():
    """Тестирование CRUD операций с прайсом"""
    print("🔧 Инициализация базы данных...")
    await init_db()

    async with async_session() as session:
        # Проверяем, есть ли уже записи
        result = await session.execute(select(Price))
        existing_prices = result.scalars().all()
        print(f"📊 Найдено существующих позиций в прайсе: {len(existing_prices)}")

        # Добавляем тестовую позицию, если прайс пуст
        if not existing_prices:
            print("➕ Добавляем тестовые позиции...")
            test_prices = [
                Price(
                    title="Покраска бампера",
                    description="Полная покраска переднего/заднего бампера",
                    price=1500000,  # 15000.00 руб в копейках
                ),
                Price(
                    title="Покраска двери",
                    description="Покраска одной двери автомобиля",
                    price=1200000,  # 12000.00 руб в копейках
                ),
                Price(
                    title="Покраска крыла",
                    description="Покраска переднего или заднего крыла",
                    price=1000000,  # 10000.00 руб в копейках
                ),
            ]

            for price in test_prices:
                session.add(price)

            await session.commit()
            print("✅ Тестовые позиции добавлены!")

        # Показываем все позиции
        result = await session.execute(select(Price).order_by(Price.id))
        all_prices = result.scalars().all()

        print("\n📋 Текущий прайс-лист:")
        for price in all_prices:
            print(f"  {price.id}. {price.title}")
            print(f"     💰 {price.price // 100}.{price.price % 100:02d} руб.")
            print(f"     📝 {price.description}")
            print()


if __name__ == "__main__":
    asyncio.run(test_price_operations())
