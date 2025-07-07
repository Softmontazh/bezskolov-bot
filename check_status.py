#!/usr/bin/env python3
# check_status.py - Проверка статуса всех компонентов бота

import asyncio
import sys
import os
from pathlib import Path


async def check_imports():
    """Проверка импортов"""
    print("🔍 Проверка импортов...")
    try:
        # Основные модули
        import main

        print("  ✅ main.py")

        from handlers import user, price

        print("  ✅ handlers.user")
        print("  ✅ handlers.price")

        from database import db, models

        print("  ✅ database.db")
        print("  ✅ database.models")

        from fsm import request

        print("  ✅ fsm.request")

        return True
    except Exception as e:
        print(f"  ❌ Ошибка импорта: {e}")
        return False


async def check_env_template():
    """Проверка наличия шаблона .env"""
    print("\n📋 Проверка файлов конфигурации...")

    env_example = Path(".env.example")
    if env_example.exists():
        print("  ✅ .env.example существует")
        with open(env_example, "r", encoding="utf-8") as f:
            content = f.read()
            required_vars = ["BOT_TOKEN", "CREATOR_ID", "KATYA_ID"]
            for var in required_vars:
                if var in content:
                    print(f"    ✅ {var}")
                else:
                    print(f"    ❌ {var} отсутствует")
    else:
        print("  ❌ .env.example отсутствует")


async def check_database():
    """Проверка базы данных"""
    print("\n🗄️ Проверка базы данных...")
    try:
        from database.db import init_db, async_session
        from database.models import PaintRequest, Price
        from sqlalchemy import select

        await init_db()
        print("  ✅ База данных инициализирована")

        async with async_session() as session:
            # Проверяем таблицы
            result = await session.execute(select(PaintRequest))
            requests_count = len(result.scalars().all())
            print(f"  📊 Заявок в БД: {requests_count}")

            result = await session.execute(select(Price))
            prices_count = len(result.scalars().all())
            print(f"  💰 Позиций в прайсе: {prices_count}")

        return True
    except Exception as e:
        print(f"  ❌ Ошибка БД: {e}")
        return False


async def check_file_structure():
    """Проверка структуры файлов"""
    print("\n📁 Проверка структуры проекта...")

    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "README.md",
        "CHANGELOG.md",
        "DEPLOYMENT.md",
        "LICENSE",
        ".env.example",
        ".gitignore",
        "handlers/__init__.py",
        "handlers/user.py",
        "handlers/price.py",
        "database/db.py",
        "database/models.py",
        "fsm/request.py",
    ]

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")


async def main():
    print("🚀 Проверка статуса BezSkolov Bot\n")

    # Проверяем все компоненты
    imports_ok = await check_imports()
    await check_env_template()
    db_ok = await check_database()
    await check_file_structure()

    print("\n" + "=" * 50)
    if imports_ok and db_ok:
        print("🎉 Все основные компоненты работают!")
        print("📝 Следующие шаги:")
        print("   1. Создайте .env файл на основе .env.example")
        print("   2. Укажите корректные токены и ID")
        print("   3. Запустите бота: python main.py")
        print("   4. Протестируйте функции согласно TESTING_PRICE.md")
    else:
        print("⚠️ Обнаружены проблемы. Проверьте ошибки выше.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
