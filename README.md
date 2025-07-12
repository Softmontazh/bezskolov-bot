# 🎨 BezSkolo### 🔧 Для администраторов:
- 📊 Просмотр всех заявок с фильтрацией
- 🔥 **Активные заявки** - быстрый доступ к заявкам в работе (статусы "В ожидании" и "В работе")
- 🔍 Поиск заявок по номеру телефона
- ⚡ Быстрое изменение статусов заявок
- 💰 Управление прайс-листом (добавление, редактирование, удаление позиций)
- 📱 Автоматические уведомления клиентов
Профессиональный Telegram бот для приема заявок на подбор красок и продажу минитюбиков с заводской краской для закрашивания сколов. Полнофункциональная система управления заказами с админ-панелью.

## 🚀 Возможности

### 👥 Для клиентов:
- 📝 Пошаговое оформление заявки на подбор краски
- 📷 Загрузка фотографий поврежденных участков
- 📋 Просмотр истории своих заявок
- 💰 Просмотр актуального прайс-листа
- 🔔 Уведомления об изменении статуса заказа

### 🔧 Для администраторов:
- 📊 Просмотр всех заявок с фильтрацией
- � **Активные заявки** - быстрый доступ к заявкам в работе (статусы "В ожидании" и "В работе")
- �🔍 Поиск заявок по номеру телефона
- ⚡ Быстрое изменение статусов заявок
- 💰 Управление прайс-листом (добавление, редактирование, удаление позиций)
- 📱 Автоматические уведомления клиентов

### 📋 Информация в заявке:
- 🚗 Марка и модель автомобиля
- 🎨 Код краски (если известен)
- 🔢 VIN-номер (опционально)
- 📅 Год выпуска
- 📷 Фотография поврежденного участка (опционально)
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
git clone https://github.com/Softmontazh/bezskolov-bot.git
cd bezskolov-bot
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

**Для разработки (polling режим):**
```bash
python main.py
```

**Для продакшена (webhook режим):**
```bash
# Требует домен с SSL сертификатом
python main_webhook.py
```

> 📖 **Подробные инструкции по webhook:** см. [WEBHOOK_SETUP.md](./WEBHOOK_SETUP.md)

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
bezskolov-bot/
├── main.py                 # Точка входа (polling режим)
├── main_webhook.py         # Точка входа (webhook режим)
├── config.py              # Конфигурация
├── requirements.txt       # Зависимости Python
├── .env.example          # Шаблон переменных окружения
├── .gitignore           # Игнорируемые файлы для Git
├── README.md             # Основная документация
├── WEBHOOK_SETUP.md      # Инструкции по webhook
├── DEPLOYMENT.md         # Инструкции по развертыванию
├── database/
│   ├── __init__.py
│   ├── db.py           # Настройка базы данных
│   └── models.py       # Модели SQLAlchemy
├── fsm/
│   ├── __init__.py
│   └── request.py      # Состояния FSM
└── handlers/
    ├── __init__.py
    ├── user.py         # Основные обработчики
    └── price.py        # Обработчики цен
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

## 🚀 Развертывание

### На VPS/сервере:
```bash
# Клонирование и настройка
git clone https://github.com/Softmontazh/bezskolov-bot.git
cd bezskolov-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создание systemd сервиса (Linux)
sudo nano /etc/systemd/system/bezskolov-bot.service
```

### Пример systemd сервиса:
```ini
[Unit]
Description=BezSkolov Bot
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/path/to/bezskolov-bot
Environment=PATH=/path/to/bezskolov-bot/venv/bin
ExecStart=/path/to/bezskolov-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 👨‍💻 Автор

**Александр Хван** (Alexandr Khvan)  
Telegram: [@bySpecialist](https://t.me/bySpecialist)

## 🏢 Разработчик

**ТОО "СОФТМОНТАЖ"** (LLP "Softmontazh")  
📧 Email: info@softmontazh.kz  
🌐 Website: http://softmontazh.kz

---

**© 2025 ТОО "СОФТМОНТАЖ". Коммерческий продукт.**
