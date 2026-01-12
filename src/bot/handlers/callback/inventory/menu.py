from aiogram import F
from aiogram.types import CallbackQuery

from ....config import TelegramTextMap
from ....keyboards.inlines.inventory import inventory_type_keyboard
from .deps import inventory_router


@inventory_router.callback_query(F.data == "inv")
async def callback_inventory(callback: CallbackQuery):
    await callback.message.edit_text(
        text=await TelegramTextMap.INVENTORY_MENU(callback),
        reply_markup=inventory_type_keyboard(),
    )
    await callback.answer()

