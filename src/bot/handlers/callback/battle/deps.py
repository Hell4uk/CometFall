from aiogram import Router

from ....services.enemy import EnemyService
from ....services.inventory import InventoryService
from ....services.user import UserService

battle_router = Router()

user_service = UserService()
inventory_service = InventoryService()
enemy_service = EnemyService()