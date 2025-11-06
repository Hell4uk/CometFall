from math import e
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from typing import Callable, Awaitable, Any
import asyncio

class SafeEditMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Any, dict], Awaitable[Any]], event: Message | CallbackQuery, data: dict) -> Any:
        original_message = event.answer if isinstance(event, CallbackQuery) else event.edit_text

        async def safe_edit(*args, **kwargs):
            try:
                return await original_message(*args, **kwargs)
            except TelegramBadRequest as _ex:
                if "message can't be edited" in str(_ex) or 'message is not modified' in str(_ex):
                    if isinstance(event, CallbackQuery):
                        await event.message.answer(kwargs.get("text", "Ошибка"))
                    else:
                        await event.answer("Действие устарело, напишите заново /start")
                else:
                    raise
        
        if isinstance(event, CallbackQuery):
            event.message.edit_text = safe_edit
        else:
            event.edit_text = safe_edit
        
        return await handler(event, data)
