from aiogram import F
from aiogram.types import CallbackQuery
from .deps import user_service, singleplayer_router, inventory_service, enemy_service, finished_singleplayer_fight, battle_menu, singleplayer_menu_location
from .helper import fighting, find_location_by_name, find_location_by_id
import re

@singleplayer_router.callback_query(F.data == 'battle_singleplayer')
async def select_location(callback: CallbackQuery):
    await callback.message.edit_text(text=f'{callback.from_user.first_name}, выберите локацию: ', reply_markup=await singleplayer_menu_location())

@singleplayer_router.callback_query(F.data.regexp(r'battle_singleplayer:start:(\d+)'))
async def start_singleplayer_battle(callback: CallbackQuery):
    match = re.match(r"battle_singleplayer:start:(\d+)", callback.data)
    if not match:
        await callback.answer()
        return

    user = await user_service.get_by_telegram_id(callback.from_user.id)
    location = await find_location_by_id(match.group(1))
    result = await fighting(user, location)
    
    result_fight = 'вы выйграли' if result['winner'] == 'user' else 'вы програли'

    BASE_TEXT = f"""
{callback.from_user.first_name}, {result_fight}. Вам попался: {result['enemy'].name}

Ваш урон: {result['user_dmg']}
Ваша броня: {result['user_hp']}

Урон противника: {result['enemy_dmg']}
Броня противника: {result['enemy_hp']}

За игру вы получили: {result['reward']['coin']} урона, {result['reward']['exp']} опыта
"""
    await enemy_service.give_reward(user, result['enemy'], result['reward']['exp'], result['reward']['coin'])
    await callback.message.edit_text(text=BASE_TEXT, reply_markup=await finished_singleplayer_fight())
    await callback.answer()