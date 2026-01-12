import re
from typing import Dict, List, Tuple

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ....db.models import Items
from ....keyboards.inlines.market import market_item_view_keyboard, market_items_keyboard, market_main_keyboard
from .deps import market_router, market_service, user_service
from .filters import format_filters_text, get_filters
from .helpers import (
    format_item_description,
    item_type_from_slug,
    price_matches,
    rarity_slug_to_enum,
    slug_from_item_type,
)
from .state import ITEMS_PER_PAGE, RARITY_LABELS


async def _filter_items(item_type, filters: Dict) -> Tuple[List[Items], Dict[int, int]]:
    rarity_enum = rarity_slug_to_enum(filters.get("rarity"))
    search_term = filters.get("search") or None

    items = await market_service.get_items(item_type, rarity=rarity_enum, search=search_term)
    item_ids = [item.id for item in items]
    min_price_map = await market_service.get_min_price_map(item_ids)

    if filters.get("min_price") is not None or filters.get("max_price") is not None:
        items = [item for item in items if price_matches(min_price_map.get(item.id), filters)]

    return items, min_price_map


async def _show_items_list(callback: CallbackQuery, state: FSMContext, item_type_slug: str, page: int = 0):
    filters = await get_filters(state)
    item_type = item_type_from_slug(item_type_slug)
    items, min_price_map = await _filter_items(item_type, filters)
    total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if items else 0

    if not items:
        await callback.message.edit_text(
            text=(
                f"{callback.from_user.first_name}, подходящих предметов не найдено.\n\n"
                f"{format_filters_text(filters)}"
            ),
            reply_markup=market_main_keyboard(RARITY_LABELS.get(filters.get("rarity"), "все")),
        )
        await callback.answer()
        return

    page = max(0, min(page, total_pages - 1))
    await state.update_data(market_current_type=item_type_slug, market_last_page=page)

    await callback.message.edit_text(
        text=(
            f"{callback.from_user.first_name}, рынок ({'оружие' if item_type_slug == 'weapon' else 'броня'}).\n\n"
            f"{format_filters_text(filters)}\n\n"
            "Выберите предмет для подробностей:"
        ),
        reply_markup=market_items_keyboard(items, min_price_map, page, total_pages, item_type_slug),
    )
    await callback.answer()


@market_router.callback_query(F.data == "market_type_weapon")
async def callback_market_weapon(callback: CallbackQuery, state: FSMContext):
    await _show_items_list(callback, state, "weapon", page=0)


@market_router.callback_query(F.data == "market_type_armor")
async def callback_market_armor(callback: CallbackQuery, state: FSMContext):
    await _show_items_list(callback, state, "armor", page=0)


@market_router.callback_query(F.data.regexp(r"market_page_(\d+)_(weapon|armor)"))
async def callback_market_page(callback: CallbackQuery, state: FSMContext):
    match = re.match(r"market_page_(\d+)_(weapon|armor)", callback.data)
    if not match:
        await callback.answer()
        return
    page = int(match.group(1))
    item_type_slug = match.group(2)
    await _show_items_list(callback, state, item_type_slug, page)


@market_router.callback_query(F.data.regexp(r"market_back_(weapon|armor)"))
async def callback_market_back(callback: CallbackQuery, state: FSMContext):
    match = re.match(r"market_back_(weapon|armor)", callback.data)
    if not match:
        await callback.answer()
        return
    item_type_slug = match.group(1)
    data = await state.get_data()
    page = data.get("market_last_page", 0)
    await _show_items_list(callback, state, item_type_slug, page)


@market_router.callback_query(F.data.regexp(r"market_view_item_(\d+)"))
async def callback_market_view_item(callback: CallbackQuery, state: FSMContext):
    match = re.match(r"market_view_item_(\d+)", callback.data)
    if not match:
        await callback.answer()
        return
    item_id = int(match.group(1))
    item = await Items.get_or_none(id=item_id)
    if not item:
        await callback.answer("Предмет не найден.", show_alert=True)
        return

    filters = await get_filters(state)
    min_price = await market_service.get_min_price(item)
    price_text = f"{min_price} мон." if min_price is not None else "нет активных лотов"

    await callback.message.edit_text(
        text=(
            f"{format_item_description(item)}\n\n"
            f"Минимальная цена: {price_text}\n\n"
            f"{format_filters_text(filters)}"
        ),
        reply_markup=market_item_view_keyboard(item.id, slug_from_item_type(item.type), min_price),
    )
    await callback.answer()


@market_router.callback_query(F.data.regexp(r"market_buy_item_(\d+)"))
async def callback_market_buy_item(callback: CallbackQuery, state: FSMContext):
    match = re.match(r"market_buy_item_(\d+)", callback.data)
    if not match:
        await callback.answer()
        return
    item_id = int(match.group(1))
    item = await Items.get_or_none(id=item_id)
    if not item:
        await callback.answer("Предмет не найден.", show_alert=True)
        return

    user = await user_service.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    try:
        price_paid = await market_service.buy_cheapest_listing(item, user)
    except ValueError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    min_price = await market_service.get_min_price(item)
    filters = await get_filters(state)
    min_price_text = min_price if min_price is not None else "нет активных лотов"

    await callback.message.edit_text(
        text=(
            f"Покупка успешна! Вы приобрели {item.name} за {price_paid} монет.\n\n"
            f"{format_item_description(item)}\n\n"
            f"Минимальная цена: {min_price_text}\n\n"
            f"{format_filters_text(filters)}"
        ),
        reply_markup=market_item_view_keyboard(item.id, slug_from_item_type(item.type), min_price),
    )
    await callback.answer("Сделка завершена.")

