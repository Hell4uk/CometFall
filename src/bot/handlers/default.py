from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, Callback

default_router = Router("default_router")

@default_router.message(CommandStart())
async def start_commands(message: Message) -> None:
    await message.reply(text=f'')
