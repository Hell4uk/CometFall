"""Обработчик для открытия кейсов на торговой площадке.

Интеграция:
- Добавление кейсов в каталог торговой площадки
- Покупка кейсов у продавца
- Открытие кейса и получение предмета
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from src.bot.db.models import Users, Items, ItemTypeEnum, MarketItem, InventoryItems
from ....bot.services.case import CaseService
from ....bot.services.market import MarketService
from ....bot.services.user import UserService

case_router = Router()

# Сервисы
case_service = CaseService()
market_service = MarketService()
user_service = UserService()


@case_router.callback_query(F.data.startswith("open_case_"))
async def open_case_callback(callback: CallbackQuery, state: FSMContext):
    """Открытие кейса из инвентаря (ТОЛЬКО по case_id, не inventory_item_id)."""
    try:
        # Извлекаем case_id из callback
        case_id = int(callback.data.split("_")[2])
        
        # Получаем пользователя
        user = await Users.get(telegram_id=callback.from_user.id)
        
        # Получаем кейс по ID
        case = await case_service.get_case(case_id)
        
        if not case:
            await callback.answer("❌ Кейс не найден", show_alert=True)
            return
        
        # Открываем кейс (атомарная операция в сервисе)
        reward_item, message = await case_service.open_case(user, case)
        
        # Отправляем результат
        await callback.message.edit_text(
            text=(
                f"🎁 **Открытие кейса: {case.name}**\n\n"
                f"{message}\n\n"
            ),
            reply_markup=None
        )
        await callback.answer("✨ Кейс открыт!", show_alert=False)
        
    except ValueError as e:
        await callback.answer(f"❌ {str(e)}", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@case_router.callback_query(F.data.startswith("buy_case_"))
async def buy_case_callback(callback: CallbackQuery, state: FSMContext):
    """Покупка кейса на торговой площадке."""
    try:
        listing_id = int(callback.data.split("_")[2])
        user = await Users.get(telegram_id=callback.from_user.id)
        
        # Получаем объявление о продаже
        listing = await MarketItem.get_or_none(id=listing_id)
        if not listing:
            await callback.answer("❌ Объявление не найдено", show_alert=True)
            return
        
        # Проверяем, что это кейс
        if listing.item.type != ItemTypeEnum.CASE:
            await callback.answer("❌ Это не кейс", show_alert=True)
            return
        
        # Проверяем баланс
        if user.coins < listing.price:
            await callback.answer(
                f"❌ Недостаточно монет. Нужно: {listing.price}, У вас: {user.coins}",
                show_alert=True
            )
            return
        
        # Проверяем, что это не сам продавец
        if listing.seller.id == user.id:
            await callback.answer("❌ Вы не можете купить свой собственный предмет", show_alert=True)
            return
        
        # Выполняем покупку (атомарная операция)
        seller = listing.seller
        case = listing.item
        price = listing.price
        
        async with in_transaction():
            # Переводим монеты
            user.coins -= price
            seller.coins += price
            await user.save()
            await seller.save()
            
            # Добавляем кейс в инвентарь покупателя
            await case_service.inventory_service.add(user, case, quantity=1)
            
            # Удаляем объявление
            await listing.delete()
        
        await callback.message.edit_text(
            text=(
                f"✅ **Покупка успешна!**\n\n"
                f"Вы купили: **{case.name}**\n"
                f"Цена: **{price}** 💰\n\n"
                f"Кейс добавлен в ваш инвентарь.\n"
                f"Ваш баланс: {user.coins} 💰"
            ),
            reply_markup=None
        )
        await callback.answer("✅ Кейс куплен!", show_alert=False)
        
    except ValueError as e:
        await callback.answer(f"❌ {str(e)}", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@case_router.callback_query(F.data == "cases_catalog")
async def cases_catalog(callback: CallbackQuery, state: FSMContext):
    """Каталог кейсов на торговой площадке."""
    try:
        # Получаем все доступные кейсы
        cases = await case_service.get_all_cases()
        
        if not cases:
            await callback.message.edit_text(
                text="📦 В каталоге нет кейсов",
                reply_markup=None
            )
            return
        
        # Формируем информацию о кейсах
        cases_info = []
        for case in cases:
            case_info = await case_service.get_case_info(case)
            min_price = await market_service.get_min_price(case)
            
            if min_price:
                cases_info.append(
                    f"📦 **{case_info['name']}** ({case_info['rarity']})\n"
                    f"Коллекция: {case_info['collection']}\n"
                    f"Предметов: {case_info['items_in_case']}\n"
                    f"Минцена: **{min_price}** 💰\n"
                )
        
        if not cases_info:
            await callback.message.edit_text(
                text="📦 На торговой площадке нет выставленных кейсов",
                reply_markup=None
            )
            return
        
        await callback.message.edit_text(
            text="📦 **Каталог кейсов:**\n\n" + "\n".join(cases_info),
            reply_markup=None
        )
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
