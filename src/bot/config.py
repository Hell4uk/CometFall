from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv
from aiogram.types import Message, CallbackQuery

load_dotenv()

@dataclass
class ConfigService:
    BOT_API_KEY = getenv("BOT_API_KEY")
    DATABASE_URL = getenv("DATABASE_URL")

@dataclass
class TelegramTextMap:
    @staticmethod
    async def GREETING_TEXT(ctx: Message | CallbackQuery):
        return f"Привет, {ctx.from_user.first_name}"
    
    @staticmethod
    async def MAINMENU_TEXT(ctx: Message | CallbackQuery):
        return f"{ctx.from_user.first_name}, выбери действие:"