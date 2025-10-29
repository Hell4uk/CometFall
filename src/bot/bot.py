from aiogram import Bot, Dispatcher
from .config import ConfigService


if not ConfigService:
    raise Exception("You should enter `BOT_API_KEY` in .env")

bot = Bot(token=ConfigService.BOT_API_KEY)

async def bootstrap() -> None:
    from handlers.default import default_router
    dp = Dispatcher()

    dp.include_routers(
        default_router
    )

    await dp.start_polling(bot)

