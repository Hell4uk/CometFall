from aiogram import Router

from .....services.enemy import EnemyService
from .....services.inventory import InventoryService
from .....services.user import UserService

from .....game.logic.calculation import EnemyCalculator, EnemyTypeEnum, ArmorCalculation, DamageCalculation

singleplayer_router = Router()

user_service = UserService()
inventory_service = InventoryService()
enemy_service = EnemyService()

enemy_calculator = EnemyCalculator()
armor_calculator = ArmorCalculation()
damage_calculator = DamageCalculation()