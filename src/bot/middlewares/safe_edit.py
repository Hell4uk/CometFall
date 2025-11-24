# src/bot/middlewares/safe_edit.py
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
from typing import Callable, Dict, Any, Awaitable
import logging

class SafeEditMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        bot = data['bot']

        async def safe_edit_message(*args, **kwargs) -> Any:
            try:
                if isinstance(event, CallbackQuery):
                    if event.message:
                        return await event.message.edit_text(*args, **kwargs)
                    elif event.inline_message_id:
                        return await bot.edit_message_text(inline_message_id=event.inline_message_id, *args, **kwargs)
                    else:
                        raise ValueError("No message to edit in CallbackQuery")
                
                elif isinstance(event, Message):
                    return await event.edit_text(*args, **kwargs)
                
                else:
                    raise ValueError(f"Unsupported event type for safe_edit: {type(event)}")
            
            except TelegramBadRequest as e:
                if "message is not modified" in str(e).lower():
                    return None  
                else:
                    raise  
            
            except Exception as e:
                raise

        data['safe_edit_message'] = safe_edit_message

        return await handler(event, data)