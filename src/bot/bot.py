from aiogram import Bot, Dispatcher
from .config import ConfigService
from .middlewares.safe_edit import SafeEditMiddleware

if not ConfigService.BOT_API_KEY:
    raise Exception("You should enter `BOT_API_KEY` in .env")

bot = Bot(token=ConfigService.BOT_API_KEY)

async def bootstrap() -> None:
    from src.bot.handlers.default import default_router
    from src.bot.handlers.callback.battle import callback_battle_router
    from src.bot.handlers.callback.inventory import callback_inventory_router
    from src.bot.handlers.callback.market import callback_market_router
    
    dp = Dispatcher()

    dp.include_routers(
        default_router,
        callback_market_router,
        callback_battle_router,
        callback_inventory_router,
    )

    dp.message.outer_middleware(SafeEditMiddleware())
    dp.callback_query.outer_middleware(SafeEditMiddleware())

    await dp.start_polling(bot)