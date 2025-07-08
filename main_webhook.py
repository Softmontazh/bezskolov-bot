# main_webhook.py - версия для aiogram 3.x

import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from handlers import user, price
from database.db import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://yourdomain.com")
WEBHOOK_PATH = f"/bot/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Веб-сервер настройки
WEB_SERVER_HOST = "0.0.0.0"  # Изменил с 127.0.0.1 на 0.0.0.0 для VPS
WEB_SERVER_PORT = int(os.getenv("WEBHOOK_PORT", 8080))


async def on_startup(bot: Bot) -> None:
    """Действия при запуске бота"""
    try:
        await init_db()
        logger.info("База данных инициализирована")

        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]  # Явно указываем типы updates
        )
        logger.info(f"Webhook установлен: {WEBHOOK_URL}")

        bot_info = await bot.get_me()
        logger.info(f"Бот запущен: @{bot_info.username}")

    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
        raise


async def on_shutdown(bot: Bot) -> None:
    """Действия при остановке бота"""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook удален")
    except Exception as e:
        logger.error(f"Ошибка при остановке: {e}")


def create_app() -> web.Application:
    """Создание и настройка aiohttp приложения"""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")

    if not WEBHOOK_HOST or WEBHOOK_HOST == "https://yourdomain.com":
        raise ValueError("WEBHOOK_HOST должен быть настроен в .env файле")

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(user.router)
    dp.include_router(price.router)

    # Регистрация событий
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    # Важно: регистрируем обработчик правильно
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Добавляем health check
    async def health_check(request):
        return web.json_response({"status": "ok", "bot": "BezSkolov Bot"})

    app.router.add_get("/health", health_check)
    
    # Важно для aiogram 3.x
    setup_application(app, dp, bot=bot)
    
    return app


def main() -> None:
    """Основная функция для запуска webhook сервера"""
    try:
        logger.info("Запуск BezSkolov Bot в webhook режиме...")
        logger.info(f"Сервер: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}")
        logger.info(f"Webhook URL: {WEBHOOK_URL}")

        app = create_app()
        web.run_app(
            app,
            host=WEB_SERVER_HOST,
            port=WEB_SERVER_PORT,
            access_log=logger
        )

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    main()
