from aiogram import Router, F
from aiogram.types import CallbackQuery

callback_battle_router = Router()

@callback_battle_router.callback_query(F.data == 'battle')
async def callback_battle(callback: CallbackQuery) -> None:
    pass
