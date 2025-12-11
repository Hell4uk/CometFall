from aiogram import F
from aiogram.types import CallbackQuery
from .deps import user_service, singleplayer_router, inventory_service, enemy_service
from .helper import fighting, find_location_by_name

@singleplayer_router.callback_query(F.data == 'battle_singleplayer')
async def developer_manage_menu(callback: CallbackQuery, location_name='Лес Теней'):
    user = await user_service.get_by_telegram_id(callback.from_user.id)
    location = await find_location_by_name(location_name)
    results = await fighting(user, location)

    await callback.message.edit_text(text=f'{results}')

@singleplayer_router.callback_query(F.data == 'battle_singleplayer')
async def confirm_menu_battle(callback: CallbackQuery):
    pass

@singleplayer_router.callback_query(F.data == "")
async def start_fighting(callback: CallbackQuery):
    pass

@singleplayer_router.callback_query(F.data == '')
async def func1(callback: CallbackQuery):
    pass

