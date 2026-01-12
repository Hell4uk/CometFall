import re

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ....db.models import ItemTypeEnum
from ....keyboards.inlines.inventory import inventory_items_keyboard, inventory_type_keyboard
from .deps import inventory_router, inv_service, user_service
from .helpers import collect_items, item_type_name
from .state import SellItemState


async def _show_inventory(callback: CallbackQuery, user, item_type: ItemTypeEnum, item_slug: str):
    filtered, total_pages = await collect_items(user, item_type, inv_service)
    display_name = callback.from_user.first_name or callback.from_user.username or "Игрок"

    if not filtered:
        await callback.message.edit_text(
            text=f"{display_name}, у вас нет {item_type_name(item_type)}.",
            reply_markup=inventory_type_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        text=f"{display_name}, ваша коллекция {item_type_name(item_type)}:",
        reply_markup=inventory_items_keyboard(filtered, 0, total_pages, item_slug),
    )
    await callback.answer()


@inventory_router.callback_query(F.data.startswith("inv_type_"))
async def callback_show_inventory(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    item_slug = "weapon" if "weapon" in callback.data else "armor"
    item_type = ItemTypeEnum.WEAPON if item_slug == "weapon" else ItemTypeEnum.ARMOR
    user = await user_service.get_by_telegram_id(callback.from_user.id)
    await _show_inventory(callback, user, item_type, item_slug)


@inventory_router.callback_query(F.data.regexp(r"inv_page_(\d+)_(weapon|armor)"))
async def callback_paginate_inventory(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    match = re.match(r"inv_page_(\d+)_(weapon|armor)", callback.data)
    if not match:
        await callback.answer()
        return

    page = int(match.group(1))
    item_slug = match.group(2)
    item_type = ItemTypeEnum.WEAPON if item_slug == "weapon" else ItemTypeEnum.ARMOR

    user = await user_service.get_by_telegram_id(callback.from_user.id)
    filtered, total_pages = await collect_items(user, item_type, inv_service)
    display_name = callback.from_user.first_name or callback.from_user.username or "Игрок"

    if not filtered:
        await callback.message.edit_text(
            text=f"{display_name}, у вас нет {item_type_name(item_type)}.",
            reply_markup=inventory_type_keyboard(),
        )
        await callback.answer()
        return

    page = max(0, min(page, total_pages - 1))
    await callback.message.edit_text(
        text=f"{display_name}, ваша коллекция {item_type_name(item_type)}:",
        reply_markup=inventory_items_keyboard(filtered, page, total_pages, item_slug),
    )
    await callback.answer()

