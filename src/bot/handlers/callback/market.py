from aiogram import Router, F
from aiogram.types import CallbackQuery
from ...config import TelegramTextMap
from ...services.user import UserService

callback_market_router = Router()

@callback_market_router.callback_query(F.data == 'market')
async def callback_market(callback: CallbackQuery) -> None:
    user = UserService().get_by_telegram_id(callback.from_user.id)
    await callback.message.edit_text(text=await TelegramTextMap.MARKET_MENU())