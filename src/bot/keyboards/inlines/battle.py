from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ...db.models import Locations

async def battle_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text='С ботами', callback_data="battle_singleplayer")
    kb.button(text='Дуэль', callback_data="battle_multiplayer")

    kb.button(text='Назад', callback_data="mainmenu")

    return kb.adjust(1).as_markup()

async def singleplayer_menu_location() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    locations = await Locations.all()

    for loc in locations:
        kb.button(text=loc.name, callback_data=f"battle_loc_{loc.id}")

    kb.button(text="Назад", callback_data="battle_menu")
    
    return kb.adjust(1).as_markup()

async def confirm_singleplayer_battle() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text='Да', callback_data='battle_singleplayer:confirm')
    kb.button(text='Нет', callback_data="battle_singleplayer:cancel")

    return kb.adjust(1).as_markup()