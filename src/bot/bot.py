from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .config import ConfigService

if not ConfigService.BOT_API_KEY:
    raise Exception("You should enter `BOT_API_KEY` in .env")

bot = Bot(token=ConfigService.BOT_API_KEY)

async def bootstrap() -> None:
    from .middlewares.safe_edit import SafePatchMiddleware
    from .middlewares.logging import LoggingMiddleware

    from src.bot.handlers.default import default_router
    from src.bot.handlers.callback.battle.default import callback_menu_battle
    from src.bot.handlers.callback.battle.singleplayer import callback_singleplayer_router
    from src.bot.handlers.callback.inventory import callback_inventory_router
    from src.bot.handlers.callback.market import callback_market_router
    from src.bot.handlers.callback.statistics import callback_statistics_router
    from src.bot.handlers.callback.case import case_router
    
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        default_router,
        callback_market_router,
        callback_menu_battle,
        callback_singleplayer_router,
        callback_inventory_router,
        callback_statistics_router,
        case_router,
    )

    dp.message.outer_middleware(SafePatchMiddleware())
    dp.callback_query.outer_middleware(SafePatchMiddleware())

    dp.message.outer_middleware(LoggingMiddleware())
    dp.callback_query.outer_middleware(LoggingMiddleware())

    await dp.start_polling(bot)