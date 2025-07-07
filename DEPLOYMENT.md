# Инструкции по развертыванию BezSkolov Bot

## 🤔 Выбор режима развертывания

### 📡 Polling (main.py) - Для разработки
- Простая настройка, не требует SSL
- Подходит для тестирования и разработки

### 🎯 Webhooks (main_webhook.py) - Для продакшена
- Более эффективен для продакшена
- Требует SSL сертификат и домен
- **📋 Подробные инструкции:** см. `WEBHOOK_SETUP.md`

---

## Быстрый старт (Polling режим)

### 1. Подготовка окружения
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install python3 python3-pip git
```

### 2. Клонирование и настройка
```bash
git clone https://github.com/Softmontazh/bezskolov-bot.git
cd bezskolov-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройка переменных
```bash
cp .env.example .env
nano .env  # Заполните токен и ID
```

### 4. Первый запуск (режим polling)
```bash
python main.py
```

## ⚠️ Важно: Выбор режима работы

### 🔄 Polling режим (main.py)
- ✅ Простая настройка
- ✅ Подходит для разработки и тестирования
- ❌ Постоянные запросы к API
- ❌ Больше нагрузки на сервер

### 🔗 Webhook режим (main_webhook.py)
- ✅ Для продакшена (рекомендуется)
- ✅ Мгновенная доставка сообщений
- ✅ Меньше нагрузки на сервер
- ❌ Требует домен с SSL сертификатом

**📖 Подробные инструкции по настройке webhook: см. [WEBHOOK_SETUP.md](./WEBHOOK_SETUP.md)**

## Развертывание на продакшене

### Systemd сервис (рекомендуется)

1. Создайте файл сервиса:
```bash
sudo nano /etc/systemd/system/bezskolov-bot.service
```

2. Содержимое файла:
```ini
[Unit]
Description=Paint Service Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/bezskolov-bot
Environment=PATH=/home/ubuntu/bezskolov-bot/venv/bin
# Для polling режима:
ExecStart=/home/ubuntu/bezskolov-bot/venv/bin/python main.py
# Для webhook режима (раскомментируйте и закомментируйте строку выше):
# ExecStart=/home/ubuntu/bezskolov-bot/venv/bin/python main_webhook.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Запуск сервиса:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bezskolov-bot
sudo systemctl start bezskolov-bot
sudo systemctl status bezskolov-bot
```

### С использованием screen (альтернатива)
```bash
screen -S bezskolov-bot
cd bezskolov-bot
source venv/bin/activate
python main.py
# Ctrl+A, D для отключения от сессии
```

### Docker (опционально)
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## Мониторинг и логирование

### Просмотр логов systemd
```bash
sudo journalctl -u bezskolov-bot -f
```

### Автоматический перезапуск при падении
Systemd автоматически перезапустит бот если он упадет.

## Обновление

```bash
cd bezskolov-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart bezskolov-bot
```

## Резервное копирование

Регулярно делайте бэкап базы данных:
```bash
cp database.db database_backup_$(date +%Y%m%d_%H%M%S).db
```

## Безопасность

1. Используйте firewall
2. Обновляйте систему
3. Ограничьте SSH доступ
4. Используйте сильные пароли
5. Регулярно меняйте токен бота

## Производительность

- Минимальные требования: 512MB RAM, 1 CPU core
- Рекомендуемые: 1GB RAM, 2 CPU cores
- SSD диск для лучшей производительности базы данных
