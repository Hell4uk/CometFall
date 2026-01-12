import re

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ....keyboards.inlines.inventory import (
    inventory_item_view_keyboard,
    inventory_sell_back_keyboard,
    inventory_sell_confirmation_keyboard,
)
from .deps import inventory_router, inv_service, market_service, user_service
from .helpers import format_item_detail_text, item_type_slug, send_inventory_overview
from .state import SellItemState


@inventory_router.callback_query(F.data.regexp(r"inv_sell_(\d+)"))
async def callback_sell_inventory_item(callback: CallbackQuery, state: FSMContext):
    match = re.match(r"inv_sell_(\d+)", callback.data)
    if not match:
        await callback.answer()
        return

    inventory_item_id = int(match.group(1))
    user = await user_service.get_by_telegram_id(callback.from_user.id)
    inv_item = await inv_service.get_inventory_item(user, inventory_item_id)

    if not inv_item:
        await callback.answer("Предмет не найден.", show_alert=True)
        return

    min_price = await market_service.get_min_price(inv_item.item)
    min_price_text = f"{min_price} мон." if min_price is not None else "нет предложений"
    item_slug = item_type_slug(inv_item.item.type)

    await state.set_state(SellItemState.waiting_for_price)
    await state.update_data(inventory_item_id=inv_item.id, item_slug=item_slug)

    await callback.message.answer(
        text=(
            f"Вы продаёте {inv_item.item.name}.\n"
            f"Минимальная цена на рынке: {min_price_text}\n\n"
            "Введите желаемую цену сообщением (целое число)."
        ),
        reply_markup=inventory_sell_back_keyboard(inv_item.id),
    )
    await callback.answer()


@inventory_router.message(SellItemState.waiting_for_price)
async def inventory_sell_price_input(message: Message, state: FSMContext):
    data = await state.get_data()
    inventory_item_id = data.get("inventory_item_id")

    if not inventory_item_id:
        await message.answer("Не удалось найти предмет. Попробуйте снова.")
        await state.clear()
        return

    user = await user_service.get_by_telegram_id(message.from_user.id)
    inv_item = await inv_service.get_inventory_item(user, inventory_item_id)

    if not inv_item:
        await message.answer("Предмет больше недоступен.")
        await state.clear()
        return

    price_text = (message.text or "").strip().replace(" ", "")
    if not price_text.isdigit():
        await message.answer("Цена должна быть положительным числом. Попробуйте снова.")
        return

    price = int(price_text)
    if price <= 0:
        await message.answer("Цена должна быть больше нуля. Попробуйте снова.")
        return

    min_price = await market_service.get_min_price(inv_item.item)
    min_price_text = f"{min_price} мон." if min_price is not None else "нет предложений"

    await state.update_data(price=price)
    await state.set_state(SellItemState.waiting_for_confirmation)

    await message.answer(
        text=(
            f"Выставить {inv_item.item.name} за {price} монет?\n"
            f"Минимальная цена на рынке: {min_price_text}\n\n"
            "Подтвердите или отмените сделку."
        ),
        reply_markup=inventory_sell_confirmation_keyboard(),
    )


@inventory_router.callback_query(F.data == "inv_sell_cancel")
async def callback_cancel_inventory_sale(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    inventory_item_id = data.get("inventory_item_id")
    await state.clear()

    if inventory_item_id:
        user = await user_service.get_by_telegram_id(callback.from_user.id)
        inv_item = await inv_service.get_inventory_item(user, inventory_item_id)
        if inv_item:
            item_slug = item_type_slug(inv_item.item.type)
            await callback.message.edit_text(
                text=format_item_detail_text(inv_item),
                reply_markup=inventory_item_view_keyboard(inv_item.id, item_slug),
            )
            await callback.answer("Продажа отменена.")
            return

    await callback.message.edit_text("Продажа отменена.")
    await callback.answer()


@inventory_router.callback_query(F.data == "inv_sell_confirm")
async def callback_confirm_inventory_sale(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    inventory_item_id = data.get("inventory_item_id")
    price = data.get("price")
    item_slug = data.get("item_slug")

    if not all([inventory_item_id, price, item_slug]):
        await callback.answer("Нет активной продажи.", show_alert=True)
        await state.clear()
        return

    user = await user_service.get_by_telegram_id(callback.from_user.id)
    inv_item = await inv_service.get_inventory_item(user, inventory_item_id)

    if not inv_item:
        await callback.answer("Предмет больше недоступен.", show_alert=True)
        await state.clear()
        return

    await market_service.list_item(inv_item.item, user, price)
    await inv_service.remove(user, inv_item.item, quantity=1)
    await state.clear()

    await callback.message.edit_text(
        text=f"{inv_item.item.name} выставлен на рынок за {price} монет."
    )

    await send_inventory_overview(
        callback.message,
        user,
        inv_item.item.type,
        item_slug,
        inv_service,
    )
    await callback.answer("Предмет размещён на рынке.")

