from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ...config import TelegramTextMap


async def mainmenu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
