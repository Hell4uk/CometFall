from tortoise import Tortoise, run_async
from tortoise.exceptions import DBConnectionError
import logging, os
from ..config import ConfigService

logger = logging.getLogger(__name__)

TORTOISE_ORM = {
    "connections": {"default": ConfigService.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["src.bot.db.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

async def init_db():
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        logger.info('@ | Database connected and schemas generated successful!')
    
    except DBConnectionError as _ex:
        logger.error(f"@ | Database connected failed: {_ex}")
        raise

async def close_db():
    await Tortoise.close_connections()
