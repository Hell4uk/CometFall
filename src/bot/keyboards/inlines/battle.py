from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ...db.models import Locations

async def battle_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    locations = await Locations.all()

    for loc in locations:
        kb.button(text=loc.name, callback_data=f"battle_loc_{loc.id}")

    kb.button(text="Назад", callback_data="mainmenu")
    
    return kb.adjust(1).as_markup()