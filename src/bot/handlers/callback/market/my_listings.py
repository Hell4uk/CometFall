import re

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ....db.models import MarketItem
from ....keyboards.inlines.market import market_main_keyboard, market_my_listing_view_keyboard, market_my_listings_keyboard
from .deps import market_router, market_service, user_service
from .filters import get_filters
from .helpers import format_item_description
from .state import LISTINGS_PER_PAGE, RARITY_LABELS


@market_router.callback_query(F.data == "market_my_listings")
async def callback_market_my_listings(callback: CallbackQuery, state: FSMContext):
    user = await user_service.get_by_telegram_id(callback.from_user.id)
    listings = await market_service.get_player_listings(user)

    total_pages = (len(listings) + LISTINGS_PER_PAGE - 1) // LISTINGS_PER_PAGE if listings else 0
    await state.update_data(market_my_page=0)

    if not listings:
        filters = await get_filters(state)
        await callback.message.edit_text(
            text="У вас нет активных лотов. Используйте инвентарь, чтобы выставить предметы.",
            reply_markup=market_main_keyboard(RARITY_LABELS.get(filters.get("rarity"), "все")),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        text="Ваши активные лоты:",
        reply_markup=market_my_listings_keyboard(listings, 0, total_pages),
    )
    await callback.answer()


@market_router.callback_query(F.data.regexp(r"market_my_page_(\d+)"))
async def callback_market_my_page(callback: CallbackQuery, state: FSMContext):
    match = re.match(r"market_my_page_(\d+)", callback.data)
    if not match:
        await callback.answer()
        return
    page = int(match.group(1))

    user = await user_service.get_by_telegram_id(callback.from_user.id)
    listings = await market_service.get_player_listings(user)
    if not listings:
        await callback.answer("У вас нет активных лотов.", show_alert=True)
        return

    total_pages = (len(listings) + LISTINGS_PER_PAGE - 1) // LISTINGS_PER_PAGE
    page = max(0, min(page, total_pages - 1))
    await state.update_data(market_my_page=page)

    await callback.message.edit_text(
        text="Ваши активные лоты:",
        reply_markup=market_my_listings_keyboard(listings, page, total_pages),
    )
    await callback.answer()


@market_router.callback_query(F.data.regexp(r"market_my_view_(\d+)"))
async def callback_market_my_view(callback: CallbackQuery, state: FSMContext):
    match = re.match(r"market_my_view_(\d+)", callback.data)
    if not match:
        await callback.answer()
        return
    listing_id = int(match.group(1))

    user = await user_service.get_by_telegram_id(callback.from_user.id)
    listing = await MarketItem.filter(id=listing_id, seller=user).prefetch_related("item").first()

    if not listing:
        await callback.answer("Лот не найден.", show_alert=True)
        return

    await callback.message.edit_text(
        text=(
            f"Ваш лот:\n\n"
            f"{format_item_description(listing.item)}\n\n"
            f"Цена: {listing.price} монет."
        ),
        reply_markup=market_my_listing_view_keyboard(listing.id),
    )
    await callback.answer()


@market_router.callback_query(F.data.regexp(r"market_my_remove_(\d+)"))
async def callback_market_my_remove(callback: CallbackQuery, state: FSMContext):
    match = re.match(r"market_my_remove_(\d+)", callback.data)
    if not match:
        await callback.answer()
        return
    listing_id = int(match.group(1))

    user = await user_service.get_by_telegram_id(callback.from_user.id)
    removed = await market_service.remove_listing(listing_id, user)
    if not removed:
        await callback.answer("Лот не найден.", show_alert=True)
        return

    listings = await market_service.get_player_listings(user)
    total_pages = (len(listings) + LISTINGS_PER_PAGE - 1) // LISTINGS_PER_PAGE if listings else 0
    data = await state.get_data()
    page = min(data.get("market_my_page", 0), max(total_pages - 1, 0)) if listings else 0

    if not listings:
        filters = await get_filters(state)
        await callback.message.edit_text(
            text="Вы сняли последний лот. Рынок ждёт новых предложений!",
            reply_markup=market_main_keyboard(RARITY_LABELS.get(filters.get("rarity"), "все")),
        )
        await callback.answer("Лот снят с продажи.")
        return

    await state.update_data(market_my_page=page)
    await callback.message.edit_text(
        text="Ваши активные лоты:",
        reply_markup=market_my_listings_keyboard(listings, page, total_pages),
    )
    await callback.answer("Лот снят с продажи.")

