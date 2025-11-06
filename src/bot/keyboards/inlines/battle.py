from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# TODO: Привязать локации из бд
async def battle_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    return kb.adjust(1).as_markup()
