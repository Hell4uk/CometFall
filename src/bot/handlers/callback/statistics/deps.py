from aiogram import Router

from ....services.inventory import InventoryService
from ....services.user import UserService

statistics_router = Router()

user_service = UserService()
inventory_service = InventoryService()