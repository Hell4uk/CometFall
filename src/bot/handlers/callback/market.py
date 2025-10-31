from aiogram import Router, F
from aiogram.types import CallbackQuery

callback_market_router = Router()

@callback_market_router.callback_query(F.data == '')
async def callback_market(callback: CallbackQuery) -> None:
    pass