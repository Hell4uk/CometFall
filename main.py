import logging
from src.bot.bot import bootstrap
from src.bot.db.database import init_db, close_db
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
        
    except InterruptedError:
        print("Telegram bot was closed!")

    finally:
        await close_db()

if __name__ == '__main__':
    asyncio.run(main())