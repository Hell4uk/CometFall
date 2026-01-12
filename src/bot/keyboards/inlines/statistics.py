from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ...config import TelegramTextMap

async def get_statistic_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text='Назад', callback_data='mainmenu')

    return kb.adjust(1).as_markup()