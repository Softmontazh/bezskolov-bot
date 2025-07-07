# handlers/user.py

from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from fsm.request import RequestFSM, AdminFSM, PriceFSM
from database.models import PaintRequest
from database.db import async_session
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

ADMIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Все заявки")],
        [KeyboardButton(text="Поиск по номеру")],
        [KeyboardButton(text="Работа с прайсом")],
        [KeyboardButton(text="Выйти из админки")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

USER_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оформить заявку")],
        [KeyboardButton(text="Мои заявки")],
        [KeyboardButton(text="Посмотреть прайс")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

REQUEST_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отменить заявку")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

router = Router()


@router.message(F.text == "Отменить заявку")
async def cancel_request(message: types.Message, state: FSMContext):
    await message.answer("Заявка отменена.", reply_markup=USER_KB)
    await state.clear()


@router.message(F.text == "Выйти из админки")
async def exit_admin(message: types.Message, state: FSMContext):
    await message.answer(
        "Пока Кать 👋\n\nЗахочешь вернуться введи /start", reply_markup=USER_KB
    )
    await state.clear()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    username = message.from_user.username or message.from_user.first_name
    CREATOR_ID = os.environ.get("CREATOR_ID")
    KATYA_ID = os.environ.get("KATYA_ID")

    # Очищаем состояние при старте
    await state.clear()

    if KATYA_ID and str(message.from_user.id) == str(KATYA_ID):
        await message.answer(
            "Привет, Катюша! 👋\n\nДобро пожаловать в админ-панель.",
            reply_markup=ADMIN_KB,
        )
    elif CREATOR_ID and str(message.from_user.id) == str(CREATOR_ID):
        await message.answer(
            "Привет, Создатель! 👋\n\nДобро пожаловать в админ-панель.",
            reply_markup=ADMIN_KB,
        )
    else:
        await message.answer(
            f"Привет, {username}! 👋\n\n"
            "Добро пожаловать в бот для заказа заводской краски для сколов!\n\n"
            "Выберите действие:",
            reply_markup=USER_KB,
        )


@router.message(RequestFSM.brand)
async def input_brand(message: types.Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("Хорошо!\nВведите модель авто:")
    await state.set_state(RequestFSM.model)


@router.message(RequestFSM.model)
async def input_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Отлично!\n\nТеперь введите код краски:")
    await state.set_state(RequestFSM.color_code)


@router.message(RequestFSM.color_code)
async def input_color_code(message: types.Message, state: FSMContext):
    await state.update_data(color_code=message.text)
    await message.answer("Хорошо!\n\n Если знаете укажите Ваш VIN:")
    await state.set_state(RequestFSM.vin)


@router.message(RequestFSM.vin)
async def input_vin(message: types.Message, state: FSMContext):
    await state.update_data(vin=message.text)
    await message.answer("Пойдет!\n\nВведите год выпуска авто:")
    await state.set_state(RequestFSM.year)


@router.message(RequestFSM.year)
async def input_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer("Отлично!\n\nТеперь загрузите фотографию авто (по желанию):")
    await state.set_state(RequestFSM.image)


@router.message(F.photo, RequestFSM.image)
async def input_image(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await state.update_data(image=None)

    await message.answer(
        "Пойдет!!\n\nТеперь укажите Ваши контакты для связи\n\nВведите номер телефона:"
    )
    await state.set_state(RequestFSM.phone)


@router.message(F.text, RequestFSM.image)
async def skip_image(message: types.Message, state: FSMContext):
    await state.update_data(image=None)
    await message.answer(
        "Пойдет!!\n\nТеперь укажите номер телефона, куда выставить счет\n\nВведите номер телефона:"
    )
    await state.set_state(RequestFSM.phone)


@router.message(RequestFSM.phone)
async def input_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await message.answer("Напишите пожалуйста Ваши данные для доставки:\n\n"
                         "Фамилия Имя\n"
                         "Телефон для связи\n"
                         "Город\n"
                         "Улица\n"
                         "Дом\n"
                         "Квартира\n"
                         "Индекс\n"
                         "ЛИБО АДРЕС НУЖНОГО ПОЧТОВОГО ОТДЕЛЕНИЯ")
    await state.set_state(RequestFSM.address)


@router.message(RequestFSM.address)
async def input_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Дополнительные пожелания или заметки:")
    await state.set_state(RequestFSM.notes)


@router.message(RequestFSM.notes)
async def input_notes(message: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(notes=message.text)

    data = await state.get_data()
    text = (
        "Подтвердите заявку:\n"
        f"Марка: {data['brand']}\n"
        f"Модель: {data['model']}\n"
        f"Код краски: {data['color_code']}\n"
        f"VIN: {data['vin']}\n"
        f"Год выпуска: {data['year']}\n"
        f"Изображение: {'Прикреплено' if data.get('image') else 'Не прикреплено'}\n"
        f"Телефон: {data['phone_number']}\n"
        f"Адрес: {data['address']}\n"
        f"Заметки: {data['notes']}"
    )
    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Отправить", callback_data="confirm_yes"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="confirm_no"),
            ]
        ]
    )
    await message.answer(text + "\n\nОтправить заявку?", reply_markup=confirm_kb)
    await state.set_state(RequestFSM.confirm)


@router.callback_query(F.data == "confirm_yes", RequestFSM.confirm)
async def confirm_yes(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    data = await state.get_data()
    async with async_session() as session:
        request = PaintRequest(
            user_id=callback.from_user.id,
            brand=data["brand"],
            model=data["model"],
            color_code=data["color_code"],
            vin=data["vin"],
            year=data.get("year"),
            image_id=data.get("image"),
            phone_number=data["phone_number"],
            address=data["address"],
            notes=data["notes"],
        )
        session.add(request)
        await session.commit()

    # Уведомление владельцу
    KATYA_ID = os.environ.get("KATYA_ID")
    if KATYA_ID:
        try:
            notification_text = (
                f"🆕 Новая заявка от @{callback.from_user.username or callback.from_user.id}\n\n"
                f"🚗 Марка: {data['brand']}\n"
                f"📋 Модель: {data['model']}\n"
                f"🎨 Код краски: {data['color_code']}\n"
                f"🔢 VIN: {data['vin']}\n"
                f"📅 Год: {data.get('year', 'Не указан')}\n"
                f"📞 Телефон: {data['phone_number']}\n"
                f"📍 Адрес: {data['address']}\n"
                f"📝 Заметки: {data['notes']}"
            )

            if data.get("image"):
                await bot.send_photo(
                    int(KATYA_ID), photo=data["image"], caption=notification_text
                )
            else:
                await bot.send_message(int(KATYA_ID), notification_text)

        except TelegramBadRequest:
            # Владелец не начинал общение с ботом - игнорируем ошибку
            pass
        except Exception as e:
            print(f"Ошибка при отправке уведомления: {e}")

    await callback.message.edit_text(
        "✅ Заявка успешно отправлена!\n\n"
        "Мы свяжемся с вами в ближайшее время для уточнения деталей.",
        reply_markup=None,
    )
    await callback.message.answer("Спасибо за обращение! 🙏", reply_markup=USER_KB)
    await state.clear()


@router.callback_query(F.data == "confirm_no", RequestFSM.confirm)
async def confirm_no(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "❌ Заявка отменена.\n\nВы можете создать новую заявку в любое время.",
        reply_markup=None,
    )
    await callback.message.answer("Главное меню:", reply_markup=USER_KB)
    await state.clear()


# Админские обработчики
@router.message(F.text == "Все заявки")
async def show_all_requests(message: types.Message, state: FSMContext):
    CREATOR_ID = os.environ.get("CREATOR_ID")
    KATYA_ID = os.environ.get("KATYA_ID")

    # Проверяем, что это админ
    if not (
        str(message.from_user.id) == str(KATYA_ID)
        or str(message.from_user.id) == str(CREATOR_ID)
    ):
        await message.answer("У вас нет доступа к этой команде.")
        return

    async with async_session() as session:
        result = await session.execute(
            select(PaintRequest).order_by(PaintRequest.created_at.desc())
        )
        requests = result.scalars().all()

    if not requests:
        await message.answer("📋 Заявок пока нет.", reply_markup=ADMIN_KB)
        return

    # Показываем последние 10 заявок
    for request in requests[:10]:
        status_emoji = {
            "pending": "🟡",
            "in_progress": "🔵",
            "completed": "🟢",
            "cancelled": "🔴",
        }.get(request.status, "⚪")

        text = (
            f"{status_emoji} Заявка #{request.id}\n"
            f"👤 ID пользователя: {request.user_id}\n"
            f"🚗 {request.brand} {request.model}\n"
            f"🎨 Код краски: {request.color_code}\n"
            f"📞 Телефон: {request.phone_number}\n"
            f"📍 Адрес: {request.address}\n"
            f"📅 Создана: {request.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"📊 Статус: {request.status}"
        )

        # Кнопки для изменения статуса
        status_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="� В ожидании",
                        callback_data=f"status_pending_{request.id}",
                    ),
                    InlineKeyboardButton(
                        text="� В работе",
                        callback_data=f"status_in_progress_{request.id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🟢 Выполнено",
                        callback_data=f"status_completed_{request.id}",
                    ),
                    InlineKeyboardButton(
                        text="🔴 Отменено",
                        callback_data=f"status_cancelled_{request.id}",
                    ),
                ],
            ]
        )

        if request.image_id:
            await message.answer_photo(
                photo=request.image_id, caption=text, reply_markup=status_kb
            )
        else:
            await message.answer(text, reply_markup=status_kb)

    if len(requests) > 10:
        await message.answer(
            f"Показано 10 из {len(requests)} заявок.", reply_markup=ADMIN_KB
        )
    else:
        await message.answer("Это все заявки.", reply_markup=ADMIN_KB)


@router.message(F.text == "Поиск по номеру")
async def search_by_phone_start(message: types.Message, state: FSMContext):
    CREATOR_ID = os.environ.get("CREATOR_ID")
    KATYA_ID = os.environ.get("KATYA_ID")

    # Проверяем, что это админ
    if not (
        str(message.from_user.id) == str(KATYA_ID)
        or str(message.from_user.id) == str(CREATOR_ID)
    ):
        await message.answer("У вас нет доступа к этой команде.")
        return

    await message.answer("📞 Введите номер телефона для поиска:")
    await state.set_state(AdminFSM.search_phone)


@router.message(AdminFSM.search_phone)
async def search_by_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    async with async_session() as session:
        result = await session.execute(
            select(PaintRequest)
            .where(PaintRequest.phone_number.contains(phone))
            .order_by(PaintRequest.created_at.desc())
        )
        requests = result.scalars().all()

    if not requests:
        await message.answer(
            f"📞 Заявок с номером '{phone}' не найдено.", reply_markup=ADMIN_KB
        )
        await state.clear()
        return

    await message.answer(f"📞 Найдено {len(requests)} заявок с номером '{phone}':")

    for request in requests:
        status_emoji = {
            "pending": "🟡",
            "in_progress": "🔵",
            "completed": "🟢",
            "cancelled": "🔴",
        }.get(request.status, "⚪")

        text = (
            f"{status_emoji} Заявка #{request.id}\n"
            f"👤 ID пользователя: {request.user_id}\n"
            f"🚗 {request.brand} {request.model}\n"
            f"🎨 Код краски: {request.color_code}\n"
            f"🔢 VIN: {request.vin or 'Не указан'}\n"
            f"📅 Год: {request.year or 'Не указан'}\n"
            f"📞 Телефон: {request.phone_number}\n"
            f"📍 Адрес: {request.address}\n"
            f"📝 Заметки: {request.notes or 'Нет'}\n"
            f"📅 Создана: {request.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"📊 Статус: {request.status}"
        )

        # Кнопки для изменения статуса
        status_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="� В ожидании",
                        callback_data=f"status_pending_{request.id}",
                    ),
                    InlineKeyboardButton(
                        text="� В работе",
                        callback_data=f"status_in_progress_{request.id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🟢 Выполнено",
                        callback_data=f"status_completed_{request.id}",
                    ),
                    InlineKeyboardButton(
                        text="🔴 Отменено",
                        callback_data=f"status_cancelled_{request.id}",
                    ),
                ],
            ]
        )

        if request.image_id:
            await message.answer_photo(
                photo=request.image_id, caption=text, reply_markup=status_kb
            )
        else:
            await message.answer(text, reply_markup=status_kb)

    await message.answer("Поиск завершен.", reply_markup=ADMIN_KB)
    await state.clear()


# Обработчики изменения статуса заявки
@router.callback_query(F.data.startswith("status_"))
async def change_request_status(callback: types.CallbackQuery, bot: Bot):
    data_parts = callback.data.split("_")
    new_status = data_parts[1]
    request_id = int(data_parts[2])

    async with async_session() as session:
        result = await session.execute(
            select(PaintRequest).where(PaintRequest.id == request_id)
        )
        request = result.scalar_one_or_none()

        if not request:
            await callback.answer("Заявка не найдена", show_alert=True)
            return

        old_status = request.status
        request.status = new_status
        await session.commit()

    status_names = {
        "pending": "В ожидании",
        "in_progress": "В работе",
        "completed": "Выполнено",
        "cancelled": "Отменено",
    }

    await callback.answer(
        f"Статус заявки #{request_id} изменен: {status_names[old_status]} → {status_names[new_status]}"
    )

    # Уведомляем пользователя об изменении статуса
    try:
        status_messages = {
            "in_progress": f"🔵 Ваша заявка #{request_id} принята в работу!\n\nМы уже начали обработку вашего заказа {request.brand} {request.model}.",
            "completed": f"🟢 Ваша заявка #{request_id} выполнена!\n\nКраска {request.brand} {request.model} готова. Спасибо за обращение!",
            "cancelled": f"🔴 Ваша заявка #{request_id} отменена.\n\nПо вопросам обращайтесь к администратору."
        }
        
        if new_status in status_messages:
            await bot.send_message(
                request.user_id,
                status_messages[new_status]
            )
    except Exception as e:
        print(f"Ошибка при отправке уведомления пользователю: {e}")

    # Обновляем сообщение с новым статусом
    status_emoji = {
        "pending": "🟡",
        "in_progress": "🔵",
        "completed": "🟢",
        "cancelled": "🔴",
    }.get(new_status, "⚪")

    # Получаем обновленный текст
    current_text = (
        callback.message.caption if callback.message.photo else callback.message.text
    )
    lines = current_text.split("\n")

    # Обновляем строку со статусом
    for i, line in enumerate(lines):
        if line.startswith("📊 Статус:"):
            lines[i] = f"📊 Статус: {new_status}"
            break

    # Обновляем эмодзи в первой строке
    lines[0] = f"{status_emoji} Заявка #{request_id}"

    updated_text = "\n".join(lines)

    # Кнопки для изменения статуса (обновленные)
    status_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="� В ожидании", callback_data=f"status_pending_{request_id}"
                ),
                InlineKeyboardButton(
                    text="� В работе", callback_data=f"status_in_progress_{request_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🟢 Выполнено", callback_data=f"status_completed_{request_id}"
                ),
                InlineKeyboardButton(
                    text="🔴 Отменено", callback_data=f"status_cancelled_{request_id}"
                ),
            ],
        ]
    )

    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=updated_text, reply_markup=status_kb
            )
        else:
            await callback.message.edit_text(text=updated_text, reply_markup=status_kb)
    except:
        pass  # Игнорируем ошибки редактирования


@router.message(F.text == "Оформить заявку")
async def start_new_request(message: types.Message, state: FSMContext):
    await message.answer(
        "Отлично! Давайте оформим заявку по поиску и подбору вашего оригинального цвета.\n\nВведите марку авто:",
        reply_markup=REQUEST_KB,
    )
    await state.set_state(RequestFSM.brand)


@router.message(F.text == "Мои заявки")
async def show_my_requests(message: types.Message):
    user_id = message.from_user.id

    async with async_session() as session:
        result = await session.execute(
            select(PaintRequest)
            .where(PaintRequest.user_id == user_id)
            .order_by(PaintRequest.created_at.desc())
        )
        requests = result.scalars().all()

    if not requests:
        await message.answer("📋 У вас пока нет заявок.", reply_markup=USER_KB)
        return

    await message.answer(f"📋 Ваши заявки ({len(requests)}):")

    for request in requests:
        status_emoji = {
            "pending": "🟡 В ожидании",
            "in_progress": "🔵 В работе",
            "completed": "🟢 Выполнено",
            "cancelled": "🔴 Отменено",
        }.get(request.status, "⚪ Неизвестно")

        text = (
            f"📋 Заявка #{request.id}\n"
            f"🚗 {request.brand} {request.model}\n"
            f"🎨 Код краски: {request.color_code}\n"
            f"📞 Телефон: {request.phone_number}\n"
            f"📍 Адрес: {request.address}\n"
            f"📅 Создана: {request.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"📊 Статус: {status_emoji}"
        )

        await message.answer(text)

    await message.answer("Это все ваши заявки.", reply_markup=USER_KB)
