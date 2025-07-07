# Инструкции по развертыванию Paint Service Bot

## Быстрый старт

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
git clone https://github.com/your-username/paint-service-bot.git
cd paint-service-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройка переменных
```bash
cp .env.example .env
nano .env  # Заполните токен и ID
```

### 4. Первый запуск
```bash
python main.py
```

## Развертывание на продакшене

### Systemd сервис (рекомендуется)

1. Создайте файл сервиса:
```bash
sudo nano /etc/systemd/system/paint-bot.service
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
WorkingDirectory=/home/ubuntu/paint-service-bot
Environment=PATH=/home/ubuntu/paint-service-bot/venv/bin
ExecStart=/home/ubuntu/paint-service-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Запуск сервиса:
```bash
sudo systemctl daemon-reload
sudo systemctl enable paint-bot
sudo systemctl start paint-bot
sudo systemctl status paint-bot
```

### С использованием screen (альтернатива)
```bash
screen -S paint-bot
cd paint-service-bot
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
sudo journalctl -u paint-bot -f
```

### Автоматический перезапуск при падении
Systemd автоматически перезапустит бот если он упадет.

## Обновление

```bash
cd paint-service-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart paint-bot
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
