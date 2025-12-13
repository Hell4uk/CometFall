from aiogram import F
from aiogram.types import CallbackQuery
from .deps import user_service, singleplayer_router, inventory_service, enemy_service, finished_singleplayer_fight, battle_menu
from .helper import fighting, find_location_by_name


@singleplayer_router.callback_query(F.data == 'battle_singleplayer:start')
async def start_singleplayer_battle(callback: CallbackQuery, location_name: str = 'Лес Теней'):
    user = await user_service.get_by_telegram_id(callback.from_user.id)
    location = await find_location_by_name(location_name)
    result = await fighting(user, location)
    
    result_fight = 'вы выйграли' if result['winner'] == 'user' else 'вы програли'

    BASE_TEXT = f"""
{callback.from_user.first_name}, {result_fight}. Вам попался: {result['enemy'].name}

Ваш урон: {result['user_dmg']}
Ваша броня: {result['user_hp']}

Урон противника: {result['enemy_dmg']}
Броня противника: {result['enemy_hp']}

За игру вы получили: {result['reward']['coins']} урона, {result['reward']['exp']} опыта
"""
    await enemy_service.give_reward(user, result['enemy'], result['reward']['exp'], result['reward']['coins'])
    await callback.message.edit_text(text=BASE_TEXT, reply_markup=await finished_singleplayer_fight())
    await callback.answer()