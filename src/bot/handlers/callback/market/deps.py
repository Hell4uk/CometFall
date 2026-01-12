from aiogram import Router

from ....services.market import MarketService
from ....services.user import UserService

market_router = Router()
market_service = MarketService()
user_service = UserService()

