from aiogram import Router, F
from aiogram.types import CallbackQuery
from ....keyboards.inlines.battle import battle_menu

callback_menu_battle = Router()

@callback_menu_battle.callback_query(F.data == 'battle_menu')
async def battle_menu(callback: CallbackQuery):
    await callback.message.edit_text(text=f'{callback.from_user.first_name}, выберите тип сражения:', reply_markup=await battle_menu())

@callback_menu_battle.callback_query(F.data == 'battle_multiplayer')
async def multiplayer_frame(callback: CallbackQuery):
    await callback.message.edit_text(text=f'{callback.from_user.first_name}, чтобы начать дуэль, вам нужно ответить на любое сообщение игрока командой: /cometfall_duel')

