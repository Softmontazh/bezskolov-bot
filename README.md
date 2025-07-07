# 🎨 Paint Service Bot

Профессиональный Telegram бот для приема заявок на покраску автомобилей. Полнофункциональная система управления заказами с админ-панелью.

## 🚀 Возможности

### 👥 Для клиентов:
- 📝 Пошаговое оформление заявки на покраску
- 📷 Загрузка фотографий автомобиля
- 📋 Просмотр истории своих заявок
- 🔔 Уведомления об изменении статуса заказа

### 🔧 Для администраторов:
- 📊 Просмотр всех заявок с фильтрацией
- 🔍 Поиск заявок по номеру телефона
- ⚡ Быстрое изменение статусов заявок
- 📱 Автоматические уведомления клиентов

### 📋 Информация в заявке:
- 🚗 Марка и модель автомобиля
- 🎨 Код краски
- 🔢 VIN-номер (опционально)
- 📅 Год выпуска
- 📷 Фотография автомобиля (опционально)
- 📞 Контактный телефон
- 📍 Адрес доставки
- 📝 Дополнительные заметки

## 🛠 Технический стек

- **Python 3.12+**
- **aiogram 3.x** - современная асинхронная библиотека для Telegram Bot API
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **SQLite** - легковесная база данных
- **aiosqlite** - асинхронный драйвер для SQLite
- **python-dotenv** - управление переменными окружения

## 📦 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/paint-service-bot.git
cd paint-service-bot
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
```bash
cp .env.example .env
```

Отредактируйте файл `.env` и заполните необходимые значения:
```env
BOT_TOKEN=your_bot_token_from_botfather
CREATOR_ID=your_telegram_id
KATYA_ID=owner_telegram_id
```

### 5. Запуск бота
```bash
python main.py
```

## 🔧 Настройка

### Получение токена бота:
1. Откройте [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен в `.env`

### Получение Telegram ID:
1. Запустите бота
2. Отправьте команду `/start`
3. Отправьте команду `/id`
4. Скопируйте ID в `.env`

## 📁 Структура проекта

```
paint-service-bot/
├── main.py                 # Точка входа приложения
├── config.py              # Конфигурация
├── requirements.txt       # Зависимости Python
├── .env.example          # Шаблон переменных окружения
├── .gitignore           # Игнорируемые файлы для Git
├── database/
│   ├── __init__.py
│   ├── db.py           # Настройка базы данных
│   └── models.py       # Модели SQLAlchemy
├── fsm/
│   ├── __init__.py
│   └── request.py      # Состояния FSM
└── handlers/
    ├── __init__.py
    └── user.py         # Обработчики сообщений
```

## 🔄 Статусы заявок

- 🟡 **pending** - В ожидании (новая заявка)
- 🔵 **in_progress** - В работе
- 🟢 **completed** - Выполнено
- 🔴 **cancelled** - Отменено

## 🔒 Безопасность

- ✅ Переменные окружения для конфиденциальной информации
- ✅ Проверка прав доступа к админ-функциям
- ✅ Валидация входящих данных
- ✅ Обработка ошибок и исключений
- ✅ Логирование важных событий

## 📞 Поддержка

При возникновении вопросов или проблем:
1. Проверьте логи в консоли
2. Убедитесь в правильности настройки `.env`
3. Проверьте корректность токена бота

## 📄 Лицензия

Этот проект является коммерческим продуктом. Все права защищены.

## 🚀 Развертывание

### На VPS/сервере:
```bash
# Клонирование и настройка
git clone https://your-repo.git
cd paint-service-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создание systemd сервиса (Linux)
sudo nano /etc/systemd/system/paint-bot.service
```

### Пример systemd сервиса:
```ini
[Unit]
Description=Paint Service Bot
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/path/to/paint-service-bot
Environment=PATH=/path/to/paint-service-bot/venv/bin
ExecStart=/path/to/paint-service-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

**© 2025 BezSkolov Bot. Коммерческий продукт.**
