from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from ..services.user import UserService
from ..config import TelegramTextMap
from ..keyboards.inlines.default import mainmenu_keyboard

default_router = Router()

@default_router.message(CommandStart())
async def command_start(message: Message) -> None:
    user = await UserService().create(telegram_id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name, last_name=message.from_user.last_name)
    await message.reply(text=await TelegramTextMap.GREETING_TEXT(message), reply_markup=await mainmenu_keyboard())

@default_router.callback_query(F.data == "mainmenu")
async def callback_mainmenu(callback: CallbackQuery) -> None:
    user = await UserService().get_by_telegram_id(callback.from_user.id)
    await callback.message.edit_text(text=await TelegramTextMap.MAINMENU_TEXT(callback), reply_markup=await mainmenu_keyboard())
      