import logging
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

class SafePatchMiddleware(BaseMiddleware):
    patched = False
    cache = {}  

    async def __call__(self, handler, event, data):
        if not SafePatchMiddleware.patched:
            self.apply_patches(data["bot"])
            SafePatchMiddleware.patched = True

        return await handler(event, data)

    def apply_patches(self, bot):
        original_edit_text = Message.edit_text
        original_bot_edit = bot.edit_message_text

        async def safe_edit_text(msg: Message, *args, **kwargs):
            new_text = args[0] if args else kwargs.get("text")
            key = (msg.chat.id, msg.message_id)

            if isinstance(new_text, str) and SafePatchMiddleware.cache.get(key) == new_text:
                return None

            try:
                result = await original_edit_text(msg, *args, **kwargs)
                if isinstance(new_text, str):
                    SafePatchMiddleware.cache[key] = new_text
                return result

            except TelegramBadRequest as e:
                if "message is not modified" in str(e).lower():
                    return None
                if "can't" in str(e).lower() or "not found" in str(e).lower():
                    return None
                raise

            except TelegramForbiddenError:
                return None

            except Exception as e:
                logging.error(f"safe_edit_text unexpected: {e}")
                return None

        async def safe_bot_edit(bot, chat_id=None, message_id=None, *args, **kwargs):
            new_text = kwargs.get("text") or (args[2] if len(args) > 2 else None)
            key = (chat_id, message_id)

            if isinstance(new_text, str) and SafePatchMiddleware.cache.get(key) == new_text:
                return None

            try:
                result = await original_bot_edit(bot, chat_id, message_id, *args, **kwargs)
                if isinstance(new_text, str):
                    SafePatchMiddleware.cache[key] = new_text
                return result

            except TelegramBadRequest as e:
                if "message is not modified" in str(e).lower():
                    return None
                if "can't" in str(e).lower() or "not found" in str(e).lower():
                    return None
                return None

            except TelegramForbiddenError:
                return None

            except Exception as e:
                logging.error(f"safe_bot_edit unexpected: {e}")
                return None

        Message.edit_text = safe_edit_text
        bot.edit_message_text = safe_bot_edit

        logging.info("SafePatchMiddleware: monkey patch applied")