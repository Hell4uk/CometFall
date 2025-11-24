from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
import logging
import time

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()

        user = data.get("event_from_user") or getattr(event, "from_user", None)
        user_info = f"user_id={user.id}" if user else "unknown_user"
        chat_info = f"chat_id={event.chat.id if hasattr(event, 'chat') else 'none'}"
        event_type = event.__class__.__name__

        logger.debug(f"Входящее событие: {event_type} | {user_info} | {chat_info}")

        try:
            result = await handler(event, data)
            duration = time.time() - start_time
            logger.info(f"Обработано за {duration:.3f}с | {event_type}")
            return result
        except Exception as e:
            logger.error(f"Ошибка в обработчике {event_type}: {e}", exc_info=True)
            raise