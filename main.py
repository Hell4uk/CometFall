from src.bot.bot import bootstrap
from src.bot.db.database import init_db, close_db
import asyncio


async def main() -> None:
    await init_db()
    try:
        await bootstrap()
    finally:
        await close_db()
    
if __name__ == '__main__':
    asyncio.run(main())