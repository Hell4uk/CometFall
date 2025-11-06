from aiogram import Router, F
from aiogram.types import CallbackQuery
from ...services.user import UserService

callback_battle_router = Router()

@callback_battle_router.callback_query(F.data == 'battle')
async def callback_battle(callback: CallbackQuery) -> None:
    user = UserService().get_by_telegram_id(callback.from_user.id)