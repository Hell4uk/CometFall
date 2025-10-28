from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ConfigService:
    BOT_API_KEY = getenv("BOT_API_KEY")
    DATABASE_URL = getenv("DATABASE_URL")