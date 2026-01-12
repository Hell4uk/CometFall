"""Клавиатуры для кейсов."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from src.bot.db.models import Items


def cases_inventory_keyboard(cases: List[Items]) -> InlineKeyboardMarkup:
    """Клавиатура для открытия кейсов из инвентаря.
    
    Args:
        cases: список кейсов в инвентаре
        
    Returns:
        InlineKeyboardMarkup: клавиатура с кнопками открытия кейсов
    """
    buttons = []
    
    for case in cases:
        buttons.append([
            InlineKeyboardButton(
                text=f"🎁 {case.name}",
                callback_data=f"open_case_{case.id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="inventory_menu"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def case_market_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для покупки кейса на рынке.
    
    Args:
        case_id: ID кейса
        
    Returns:
        InlineKeyboardMarkup: клавиатура с кнопкой покупки
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💳 Купить",
                callback_data=f"buy_case_{case_id}"
            ),
            InlineKeyboardButton(
                text="ℹ️ Подробнее",
                callback_data=f"case_info_{case_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="market_menu"
            )
        ]
    ])


def cases_catalog_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для каталога кейсов."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📦 Каталог кейсов",
                callback_data="cases_catalog"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ На рынок",
                callback_data="market_menu"
            )
        ]
    ])
