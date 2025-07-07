# 🚀 Быстрый деплой BezSkolov Bot на Ubuntu 22.04

## 📋 Пошаговая инструкция

### 1. 🔗 Подключение к VPS
```bash
# Подключитесь к своему VPS через SSH
ssh username@your-vps-ip
```

### 2. 📦 Установка зависимостей
```bash
# Обновляем пакеты
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python 3.11+ и необходимые пакеты
sudo apt install python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx -y

# Проверяем версию Python
python3 --version
```

### 3. 📥 Клонирование репозитория
```bash
# Переходим в домашнюю папку
cd ~

# Клонируем репозиторий
git clone https://github.com/Softmontazh/bezskolov-bot.git

# Переходим в папку проекта
cd bezskolov-bot
```

### 4. 🐍 Настройка виртуального окружения
```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 5. ⚙️ Настройка переменных окружения
```bash
# Копируем шаблон
cp .env.example .env

# Редактируем файл (используйте nano или vim)
nano .env
```

**Заполните следующие переменные:**
```env
BOT_TOKEN=your_bot_token_here
CREATOR_ID=your_telegram_id
KATYA_ID=owner_telegram_id

# Для webhook (если нужен)
WEBHOOK_HOST=your-domain.com
WEBHOOK_PORT=8443
WEBHOOK_PATH=/webhook
```

### 6. 🧪 Тестовый запуск
```bash
# Проверяем, что все работает
python3 main.py
```

**Если бот запустился - нажмите Ctrl+C для остановки и переходите к следующему шагу.**

### 7. 🔧 Создание systemd сервиса
```bash
# Создаем файл сервиса
sudo nano /etc/systemd/system/bezskolov-bot.service
```

**Вставьте следующий конфиг (замените пути на свои):**
```ini
[Unit]
Description=BezSkolov Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bezskolov-bot
Environment=PATH=/home/ubuntu/bezskolov-bot/venv/bin
ExecStart=/home/ubuntu/bezskolov-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 8. 🚀 Запуск сервиса
```bash
# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable bezskolov-bot

# Запускаем сервис
sudo systemctl start bezskolov-bot

# Проверяем статус
sudo systemctl status bezskolov-bot
```

### 9. 📊 Мониторинг
```bash
# Просмотр логов в реальном времени
sudo journalctl -u bezskolov-bot -f

# Перезапуск при необходимости
sudo systemctl restart bezskolov-bot

# Остановка
sudo systemctl stop bezskolov-bot
```

## 🌐 Опционально: Настройка Webhook

Если у вас есть домен и нужен webhook режим:

### 1. Настройка Nginx
```bash
sudo nano /etc/nginx/sites-available/bezskolov-bot
```

### 2. Получение SSL сертификата
```bash
sudo certbot --nginx -d your-domain.com
```

### 3. Переключение на webhook
```bash
sudo systemctl stop bezskolov-bot
# Измените ExecStart в сервисе на main_webhook.py
sudo systemctl start bezskolov-bot
```

## ✅ Готово!

Ваш BezSkolov Bot теперь работает на VPS в режиме 24/7!

## 🔍 Полезные команды
```bash
# Обновление бота
cd ~/bezskolov-bot
git pull
sudo systemctl restart bezskolov-bot

# Проверка работы
curl -s https://api.telegram.org/bot<BOT_TOKEN>/getMe

# Очистка логов
sudo journalctl --vacuum-time=7d
```
