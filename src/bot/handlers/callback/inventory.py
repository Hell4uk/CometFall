from aiogram import F, Router
from aiogram.types import CallbackQuery
from ...config import TelegramTextMap
from ...services.user import UserService

callback_inventory_router = Router()

@callback_inventory_router.callback_query(F.data == 'inv')
async def callback_inventory(callback: CallbackQuery):
    user = UserService().get_by_telegram_id(callback.from_user.id)
    await callback.message.edit_text(text=await TelegramTextMap.INVENTORY_MENU())