from aiogram.types import CallbackQuery
from aiogram import F
from .deps import statistics_router, user_service, inventory_service
from ....keyboards.inlines.statistics import get_statistic_keyboard
from ....db.models import ItemTypeEnum

@statistics_router.callback_query(F.data == 'stats')
async def view_user_statistics(callback: CallbackQuery):
    user = user_service.get_by_telegram_id(callback.from_user.id)

    equipped_sword = inventory_service.get_equipped_item(user, ItemTypeEnum.WEAPON)
    equipped_armor = inventory_service.get_equipped_item(user, ItemTypeEnum.ARMOR)

    message = f"{callback.from_user.first_name}, ваша статистика:\nМонет: {user.coins}\n"

    await callback.message.edit_text('', reply_markup=await get_statistic_keyboard())