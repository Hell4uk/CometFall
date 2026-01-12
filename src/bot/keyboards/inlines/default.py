from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ...config import TelegramTextMap


async def mainmenu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text='Начать сражение', callback_data='battle_menu')
    kb.button(text='Инвентарь', callback_data='inv')
    kb.button(text='Рынок', callback_data='market')
    kb.button(text='Статистика', callback_data='stats')

    return kb.adjust(1).as_markup()