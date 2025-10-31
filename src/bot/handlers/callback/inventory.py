from aiogram import F, Router
from aiogram.types import CallbackQuery

callback_inventory_router = Router("callback_inventory_router")

@callback_inventory_router.callback_query(F.data == '')
async def callback_inventory():
    pass