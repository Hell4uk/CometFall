from aiogram import Router

from ....services.inventory import InventoryService
from ....services.market import MarketService
from ....services.user import UserService

inventory_router = Router()
inv_service = InventoryService()
market_service = MarketService()
user_service = UserService()

