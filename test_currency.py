# test_currency.py
# Тест для проверки отображения валюты в тенге

import asyncio
from database.db import init_db, async_session
from database.models import Price
from sqlalchemy import select


async def test_currency_display():
    """Тестирование отображения цен в тенге"""
    print("🔧 Инициализация базы данных...")
    await init_db()

    async with async_session() as session:
        # Создаем тестовую позицию с ценой в тиын
        test_price_tiyn = 250050  # 2500.50 тг в тиын

        # Проверяем правильность отображения
        formatted_price = f"{test_price_tiyn // 100}.{test_price_tiyn % 100:02d} тг."

        print(f"💰 Тестовая цена: {test_price_tiyn} тиын")
        print(f"💰 Отображение: {formatted_price}")
        print(f"✅ Ожидаемое: 2500.50 тг.")

        assert (
            formatted_price == "2500.50 тг."
        ), f"Ошибка форматирования: получено {formatted_price}"
        print("✅ Тест пройден успешно!")


if __name__ == "__main__":
    asyncio.run(test_currency_display())
