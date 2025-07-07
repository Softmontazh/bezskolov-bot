# 🔗 Настройка Webhook для продакшена

## 📋 Зачем использовать webhook?

**Polling (текущий режим):**
- ✅ Простота настройки
- ❌ Постоянные запросы к Telegram API
- ❌ Больше нагрузки на сервер
- ❌ Задержки в получении сообщений

**Webhook (для продакшена):**
- ✅ Мгновенная доставка сообщений
- ✅ Меньше нагрузки на сервер
- ✅ Более эффективное использование ресурсов
- ❌ Требует SSL сертификат и домен

## 🚀 Настройка webhook

### 1. Подготовка

**Требования:**
- Домен с SSL сертификатом (https://)
- Порт 80, 88, 443 или 8443
- Nginx или Apache для проксирования

### 2. Обновление main.py для webhook

Создайте файл `main_webhook.py`:

```python
# main_webhook.py - версия для webhook

import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from handlers import user, price
from database.db import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)

load_dotenv()

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://yourdomain.com")  # Ваш домен
WEBHOOK_PATH = f"/bot/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Для локального тестирования
WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8080

async def on_startup(bot: Bot) -> None:
    """Действия при запуске"""
    await init_db()
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(bot: Bot) -> None:
    """Действия при остановке"""
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Webhook удален")

def main() -> None:
    """Основная функция для webhook режима"""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрируем роутеры
    dp.include_router(user.router)
    dp.include_router(price.router)
    
    # Регистрируем события
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Создаем обработчик запросов
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_requests_handler.register(dp, path=WEBHOOK_PATH)
    
    # Настраиваем aiohttp приложение
    app = setup_application(dp, bot)
    
    # Запускаем веб-сервер
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    main()
```

### 3. Обновление .env файла

Добавьте в `.env`:
```env
# Основные настройки
BOT_TOKEN=your_bot_token_here
CREATOR_ID=your_telegram_id
KATYA_ID=katya_telegram_id

# Webhook настройки (только для продакшена)
WEBHOOK_HOST=https://yourdomain.com
WEBHOOK_PORT=8080
```

### 4. Настройка Nginx

Создайте файл `/etc/nginx/sites-available/bezskolov-bot`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL сертификаты (получите через Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Безопасность
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Проксирование к боту
    location /bot/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Заглушка для других запросов
    location / {
        return 404;
    }
}
```

### 5. Получение SSL сертификата

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d yourdomain.com

# Проверка автоматического обновления
sudo certbot renew --dry-run
```

### 6. Обновление systemd сервиса

Создайте `/etc/systemd/system/bezskolov-bot-webhook.service`:

```ini
[Unit]
Description=BezSkolov Bot (Webhook Mode)
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/bezskolov-bot
Environment=PATH=/home/ubuntu/bezskolov-bot/venv/bin
ExecStart=/home/ubuntu/bezskolov-bot/venv/bin/python main_webhook.py
Restart=always
RestartSec=10

# Безопасность
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/ubuntu/bezskolov-bot

[Install]
WantedBy=multi-user.target
```

### 7. Запуск webhook режима

```bash
# Активация Nginx конфига
sudo ln -s /etc/nginx/sites-available/bezskolov-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Запуск бота в webhook режиме
sudo systemctl enable bezskolov-bot-webhook
sudo systemctl start bezskolov-bot-webhook

# Проверка статуса
sudo systemctl status bezskolov-bot-webhook
sudo journalctl -u bezskolov-bot-webhook -f
```

## 🔧 Переключение между режимами

### Polling → Webhook:
```bash
# Остановить polling режим
sudo systemctl stop bezskolov-bot
sudo systemctl disable bezskolov-bot

# Запустить webhook режим
sudo systemctl enable bezskolov-bot-webhook
sudo systemctl start bezskolov-bot-webhook
```

### Webhook → Polling:
```bash
# Остановить webhook режим
sudo systemctl stop bezskolov-bot-webhook
sudo systemctl disable bezskolov-bot-webhook

# Запустить polling режим
sudo systemctl enable bezskolov-bot
sudo systemctl start bezskolov-bot
```

## 🛠️ Отладка webhook

### Проверка webhook:
```bash
# Проверить установлен ли webhook
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"

# Удалить webhook (если нужно)
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
```

### Логи для отладки:
```bash
# Логи бота
sudo journalctl -u bezskolov-bot-webhook -f

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 📋 Рекомендации

- **Для разработки:** используйте polling режим (`main.py`)
- **Для продакшена:** используйте webhook режим (`main_webhook.py`)
- **Домен:** желательно выделенный поддомен (например: `bot.yourdomain.com`)
- **Безопасность:** используйте только HTTPS
- **Мониторинг:** настройте мониторинг доступности webhook URL

---
**© 2025 ТОО "СОФТМОНТАЖ" | Webhook Guide**
