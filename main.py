import logging
from src.bot.bot import bootstrap
from src.bot.db.database import init_db, close_db
import asyncio

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(), 
        logging.FileHandler('bot_logs.log') 
    ]
)

logging.getLogger('tortoise').setLevel(logging.DEBUG)
logging.getLogger('db_client').setLevel(logging.DEBUG) 

async def main() -> None:
    await init_db()
    try:
        await bootstrap()
    finally:
        await close_db()

if __name__ == '__main__':
    asyncio.run(main())