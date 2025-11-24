from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ...db.models import ItemRarityEnum

RARITY_EMOJI = {
    ItemRarityEnum.COMMON: "⬜",
    ItemRarityEnum.RARE: "🟦",
    ItemRarityEnum.EPIC: "🟪",
    ItemRarityEnum.LEGENDARY: "🟨"
}

def inventory_type_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗡️ Оружие", callback_data="inv_type_weapon")
    kb.button(text="🛡️ Броня", callback_data="inv_type_armor")
    kb.button(text="◀️ Назад", callback_data="mainmenu")
    kb.adjust(2, 1)
    return kb.as_markup()

def inventory_items_keyboard(items: list, page: int = 0, total_pages: int = 1, item_type: str = "armor") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    start = page * 5
    end = start + 5
    page_items = items[start:end]

    for idx, inv_item in enumerate(page_items, start + 1):
        item = inv_item.item
        rarity_emoji = RARITY_EMOJI.get(item.rarity, "⬜")
        equipped = "⚡" if inv_item.equipped else ""
        kb.button(
            text=f"{idx}. {rarity_emoji} | {item.name} (x{inv_item.quantity}) {equipped}",
            callback_data=f"inv_view_{inv_item.id}"
        )

    # Пагинация
    if page > 0:
        kb.button(text="⬅️ Предыдущая", callback_data=f"inv_page_{page-1}_{item_type}")
    if page < total_pages - 1:
        kb.button(text="➡️ Следующая", callback_data=f"inv_page_{page+1}_{item_type}")

    # Нижняя строка
    kb.row(
        InlineKeyboardButton(text="🔍 Фильтр", callback_data=f"inv_filter_{item_type}"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="inv")
    )
    kb.adjust(1, 2)
    return kb.as_markup()


def inventory_item_view_keyboard(item_id: int, item_type: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Продать", callback_data=f"inv_sell_{item_id}")
    kb.button(text="◀️ Назад", callback_data=f"inv_type_{item_type}")
    kb.adjust(1)
    return kb.as_markup()


def inventory_sell_back_keyboard(item_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Назад", callback_data=f"inv_view_{item_id}")
    kb.adjust(1)
    return kb.as_markup()


def inventory_sell_confirmation_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="inv_sell_confirm")
    kb.button(text="◀️ Отмена", callback_data="inv_sell_cancel")
    kb.adjust(2)
    return kb.as_markup()