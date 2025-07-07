# handlers/price.py

from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from fsm.request import PriceFSM
from database.models import Price
from database.db import async_session
from aiogram.exceptions import TelegramBadRequest
import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

router = Router()


async def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь администратором"""
    CREATOR_ID = os.environ.get("CREATOR_ID")
    KATYA_ID = os.environ.get("KATYA_ID")
    return str(user_id) == str(KATYA_ID) or str(user_id) == str(CREATOR_ID)


@router.message(F.text == "Работа с прайсом")
async def show_price_list(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой команде.")
        return

    async with async_session() as session:
        result = await session.execute(select(Price).order_by(Price.id))
        prices = result.scalars().all()

    if not prices:
        await message.answer(
            "📋 Прайс-лист пуст.", 
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Добавить позицию", callback_data="add_price_item")]
                ]
            )
        )
        return

    await message.answer("📋 Управление прайс-листом:")
    
    for price in prices:
        price_text = (
            f"📦 {price.title}\n"
            f"💰 Цена: {price.price // 100}.{price.price % 100:02d} тг.\n"
            f"📝 Описание: {price.description or 'Не указано'}"
        )
        
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit_price_{price.id}"),
                    InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_price_{price.id}")
                ]
            ]
        )
        
        await message.answer(price_text, reply_markup=kb)
    
    # Кнопка добавления новой позиции
    await message.answer(
        "Управление прайс-листом:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Добавить позицию", callback_data="add_price_item")]
            ]
        )
    )


@router.message(F.text == "Посмотреть прайс")
async def show_price_for_users(message: types.Message):
    """Показать прайс-лист для обычных пользователей"""
    async with async_session() as session:
        result = await session.execute(select(Price).order_by(Price.id))
        prices = result.scalars().all()

    if not prices:
        await message.answer("📋 Прайс-лист пока пуст.")
        return

    price_text = "💰 **Прайс-лист услуг:**\n\n"
    
    for i, price in enumerate(prices, 1):
        price_text += (
            f"**{i}. {price.title}**\n"
            f"💰 Цена: {price.price // 100}.{price.price % 100:02d} тг.\n"
        )
        if price.description:
            price_text += f"📝 {price.description}\n"
        price_text += "\n"
    
    price_text += "📞 Для заказа оформите заявку!"
    
    await message.answer(price_text, parse_mode="Markdown")


# Обработчики callback для управления прайсом
@router.callback_query(F.data == "add_price_item")
async def add_price_item_start(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещен", show_alert=True)
        return
    
    await callback.answer()
    await callback.message.answer("📦 Введите название позиции:")
    await state.set_state(PriceFSM.add_title)


@router.message(PriceFSM.add_title)
async def add_price_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📝 Введите описание позиции (или отправьте '-' чтобы пропустить):")
    await state.set_state(PriceFSM.add_description)


@router.message(PriceFSM.add_description)
async def add_price_description(message: types.Message, state: FSMContext):
    description = None if message.text == "-" else message.text
    await state.update_data(description=description)
    await message.answer("💰 Введите цену в тенге (например: 1500 или 1500.50):")
    await state.set_state(PriceFSM.add_price)


@router.message(PriceFSM.add_price)
async def add_price_amount(message: types.Message, state: FSMContext):
    try:
        # Конвертируем тенге в тиын
        price_rubles = float(message.text.replace(",", "."))
        price_kopecks = int(price_rubles * 100)
        
        if price_kopecks <= 0:
            await message.answer("❌ Цена должна быть положительной. Попробуйте еще раз:")
            return
        
        data = await state.get_data()
        
        # Сохраняем в базу данных
        async with async_session() as session:
            new_price = Price(
                title=data["title"],
                description=data["description"],
                price=price_kopecks
            )
            session.add(new_price)
            await session.commit()
        
        await message.answer(
            f"✅ Позиция успешно добавлена!\n\n"
            f"📦 {data['title']}\n"
            f"💰 Цена: {price_kopecks // 100}.{price_kopecks % 100:02d} тг.\n"
            f"📝 Описание: {data['description'] or 'Не указано'}"
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите число (например: 1500 или 1500.50):")


@router.callback_query(F.data.startswith("edit_price_"))
async def edit_price_start(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещен", show_alert=True)
        return
    
    price_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        result = await session.execute(select(Price).where(Price.id == price_id))
        price = result.scalar_one_or_none()
        
        if not price:
            await callback.answer("Позиция не найдена", show_alert=True)
            return
    
    await state.update_data(editing_price_id=price_id)
    
    edit_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Изменить название", callback_data=f"edit_title_{price_id}")],
            [InlineKeyboardButton(text="📝 Изменить описание", callback_data=f"edit_desc_{price_id}")],
            [InlineKeyboardButton(text="💰 Изменить цену", callback_data=f"edit_amount_{price_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")]
        ]
    )
    
    await callback.message.edit_text(
        f"Редактирование позиции: {price.title}\n\nВыберите что изменить:",
        reply_markup=edit_kb
    )


@router.callback_query(F.data.startswith("edit_title_"))
async def edit_title_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📦 Введите новое название позиции:")
    await state.set_state(PriceFSM.edit_title)


@router.message(PriceFSM.edit_title)
async def edit_title_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    price_id = data["editing_price_id"]
    
    async with async_session() as session:
        result = await session.execute(select(Price).where(Price.id == price_id))
        price = result.scalar_one_or_none()
        
        if price:
            price.title = message.text
            await session.commit()
            await message.answer(f"✅ Название изменено на: {message.text}")
        else:
            await message.answer("❌ Позиция не найдена")
    
    await state.clear()


@router.callback_query(F.data.startswith("edit_desc_"))
async def edit_description_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📝 Введите новое описание (или '-' чтобы удалить):")
    await state.set_state(PriceFSM.edit_description)


@router.message(PriceFSM.edit_description)
async def edit_description_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    price_id = data["editing_price_id"]
    description = None if message.text == "-" else message.text
    
    async with async_session() as session:
        result = await session.execute(select(Price).where(Price.id == price_id))
        price = result.scalar_one_or_none()
        
        if price:
            price.description = description
            await session.commit()
            await message.answer(f"✅ Описание изменено на: {description or 'Не указано'}")
        else:
            await message.answer("❌ Позиция не найдена")
    
    await state.clear()


@router.callback_query(F.data.startswith("edit_amount_"))
async def edit_amount_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("💰 Введите новую цену в тенге:")
    await state.set_state(PriceFSM.edit_price)


@router.message(PriceFSM.edit_price)
async def edit_amount_finish(message: types.Message, state: FSMContext):
    try:
        price_rubles = float(message.text.replace(",", "."))
        price_kopecks = int(price_rubles * 100)
        
        if price_kopecks <= 0:
            await message.answer("❌ Цена должна быть положительной. Попробуйте еще раз:")
            return
        
        data = await state.get_data()
        price_id = data["editing_price_id"]
        
        async with async_session() as session:
            result = await session.execute(select(Price).where(Price.id == price_id))
            price = result.scalar_one_or_none()
            
            if price:
                price.price = price_kopecks
                await session.commit()
                await message.answer(f"✅ Цена изменена на: {price_kopecks // 100}.{price_kopecks % 100:02d} тг.")
            else:
                await message.answer("❌ Позиция не найдена")
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите число:")


@router.callback_query(F.data.startswith("delete_price_"))
async def delete_price_confirm(callback: types.CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещен", show_alert=True)
        return
    
    price_id = int(callback.data.split("_")[2])
    
    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{price_id}"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")
            ]
        ]
    )
    
    await callback.message.edit_text(
        "⚠️ Вы уверены, что хотите удалить эту позицию?",
        reply_markup=confirm_kb
    )


@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_price_execute(callback: types.CallbackQuery):
    price_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        result = await session.execute(select(Price).where(Price.id == price_id))
        price = result.scalar_one_or_none()
        
        if price:
            title = price.title
            await session.delete(price)
            await session.commit()
            await callback.message.edit_text(f"✅ Позиция '{title}' удалена")
        else:
            await callback.message.edit_text("❌ Позиция не найдена")


@router.callback_query(F.data.in_(["cancel_edit", "cancel_delete"]))
async def cancel_operation(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Операция отменена")
    await state.clear()
