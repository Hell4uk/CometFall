from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...db.models import ItemRarityEnum

RARITY_EMOJI = {
    ItemRarityEnum.COMMON: "⬜",
    ItemRarityEnum.RARE: "🟦",
    ItemRarityEnum.EPIC: "🟪",
    ItemRarityEnum.LEGENDARY: "🟨",
}


def market_main_keyboard(rarity_label: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗡️ Список оружия", callback_data="market_type_weapon")
    kb.button(text="🛡️ Список брони", callback_data="market_type_armor")
    kb.button(text="🔍 Поиск", callback_data="market_search")
    kb.button(text=f"🎯 Редкость: {rarity_label}", callback_data="market_cycle_rarity")
    kb.button(text="💵 Мин. цена", callback_data="market_set_min_price")
    kb.button(text="💵 Макс. цена", callback_data="market_set_max_price")
    kb.button(text="🧹 Сброс фильтров", callback_data="market_filters_reset")
    kb.button(text="📦 Мои лоты", callback_data="market_my_listings")
    kb.button(text="◀️ Назад", callback_data="mainmenu")
    kb.adjust(2, 2, 2, 2, 1)
    return kb.as_markup()


def market_items_keyboard(items: list, min_prices: dict, page: int, total_pages: int, item_type_slug: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    start = page * 5
    end = start + 5
    page_items = items[start:end]

    for idx, item in enumerate(page_items, start + 1):
        rarity_emoji = RARITY_EMOJI.get(item.rarity, "⬜")
        price = min_prices.get(item.id)
        price_text = f"от {price} мон." if price is not None else "нет лотов"
        kb.button(
            text=f"{idx}. {rarity_emoji} {item.name} — {price_text}",
            callback_data=f"market_view_item_{item.id}"
        )

    if total_pages > 0:
        if page > 0:
            kb.button(text="⬅️ Предыдущая", callback_data=f"market_page_{page-1}_{item_type_slug}")
        if page < total_pages - 1:
            kb.button(text="➡️ Следующая", callback_data=f"market_page_{page+1}_{item_type_slug}")

    kb.row(
        InlineKeyboardButton(text="⚙️ Меню", callback_data="market_menu"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="mainmenu")
    )
    kb.adjust(1, 2)
    return kb.as_markup()


def market_item_view_keyboard(item_id: int, item_type_slug: str, min_price: int | None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if min_price is not None:
        kb.button(text=f"💰 Купить за {min_price}", callback_data=f"market_buy_item_{item_id}")
    kb.button(text="◀️ К списку", callback_data=f"market_back_{item_type_slug}")
    kb.button(text="⚙️ Меню", callback_data="market_menu")
    kb.adjust(1)
    return kb.as_markup()


def market_my_listings_keyboard(listings: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    start = page * 5
    end = start + 5
    page_listings = listings[start:end]

    for idx, listing in enumerate(page_listings, start + 1):
        rarity_emoji = RARITY_EMOJI.get(listing.item.rarity, "⬜")
        kb.button(
            text=f"{idx}. {rarity_emoji} {listing.item.name} — {listing.price} мон.",
            callback_data=f"market_my_view_{listing.id}"
        )

    if total_pages > 0:
        if page > 0:
            kb.button(text="⬅️ Предыдущая", callback_data=f"market_my_page_{page-1}")
        if page < total_pages - 1:
            kb.button(text="➡️ Следующая", callback_data=f"market_my_page_{page+1}")

    kb.row(
        InlineKeyboardButton(text="⚙️ Меню", callback_data="market_menu"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="mainmenu")
    )
    kb.adjust(1, 2)
    return kb.as_markup()


def market_my_listing_view_keyboard(listing_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑️ Снять с продажи", callback_data=f"market_my_remove_{listing_id}")
    kb.button(text="◀️ Назад", callback_data="market_my_listings")
    kb.adjust(1)
    return kb.as_markup()

