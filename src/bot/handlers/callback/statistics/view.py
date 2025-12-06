from aiogram.types import CallbackQuery
from aiogram import F
from .deps import statistics_router, user_service, inventory_service
from ....keyboards.inlines.statistics import get_statistic_keyboard
from ....db.models import ItemTypeEnum, ItemRarityEnum

RARITY_NAMES = {
    ItemRarityEnum.COMMON: "Обычное",
    ItemRarityEnum.RARE: "Редкое",
    ItemRarityEnum.EPIC: "Эпическое",
    ItemRarityEnum.LEGENDARY: "Легендарное",
}

@statistics_router.callback_query(F.data == 'stats')
async def view_user_statistics(callback: CallbackQuery):
    user = await user_service.get_by_telegram_id(callback.from_user.id)

    equipped_sword = await inventory_service.get_equipped_item(user, ItemTypeEnum.WEAPON)
    equipped_armor = await inventory_service.get_equipped_item(user, ItemTypeEnum.ARMOR)

    sword_info = f"{RARITY_NAMES.get(equipped_sword.item.rarity, 'Неизвестно')} | {equipped_sword.item.name}" if equipped_sword else "Не экипировано"
    armor_info = f"{RARITY_NAMES.get(equipped_armor.item.rarity, 'Неизвестно')} | {equipped_armor.item.name}" if equipped_armor else "Не экипировано"

    message = f"""
{callback.from_user.first_name}, ваша статистика:
===========================
Монет: {user.coins}
Уровень: {user.lvl}
Опыт: {user.exp}
===========================
Побед (в режиме приключений): {user.sp_wins}
Поражений (в режиме приключений): {user.sp_loses}
===========================
ELO: {user.elo}
Побед (в режиме дуэль): {user.mp_wins}
Поражений (в режиме дуэль): {user.mp_loses}
===========================
Ваше оружие: {sword_info}
Ваша броня: {armor_info}
"""

    await callback.message.edit_text(message, reply_markup=await get_statistic_keyboard())
    await callback.answer()