from typing import Dict
from bot.db.models import InventoryItems, ItemRarityEnum, ItemTypeEnum, Users
from bot.services.inventory import InventoryService
from bot.db.schemas.items import WeaponAttributes, ArmorAttributes
from random import random, gauss, gammavariate
from math import sqrt, exp, log10, floor

# TODO: Сделать классы для обработки общего урона-брони для используемых предметов

class BaseCalculation:
    def __init__(self, user: Users) -> None:
        self.user = user
        self.inventory_service = InventoryService()

class DamageCalculation(BaseCalculation):
    def __init__(self, user: Users) -> None:
        super().__init__(user)

    async def calculate_damage(self) -> int:
        equipped_item = await self.inventory_service.get_equipped_item(self.user, ItemTypeEnum.WEAPON)
        if not equipped_item:
            return 0

        weapon_attributes = equipped_item.item.attributes
        
        damage = gauss(weapon_attributes.min_damage, weapon_attributes.max_damage)
        if random() < weapon_attributes.critical_chance:
            damage *= weapon_attributes.critical_multiplier
        
        damage *= weapon_attributes.attack_speed
        damage *= 1 + (weapon_attributes.item_level * 0.02) 
        damage = floor(damage)

        return damage


class ArmorCalculation(BaseCalculation):
    def __init__(self, user: Users) -> None:
        super().__init__(user)

    async def calculate_armor(self) -> float:
        equipped_item = await self.inventory_service.get_equipped_item(self.user, ItemTypeEnum.ARMOR)
        if not equipped_item:
            return 0

        armor_attributes = equipped_item.item.attributes

        armor = armor_attributes.defense
        armor *= 1 + (armor_attributes.health_bonus * random())
        armor *= 1 + (armor_attributes.item_level * 0.02)
        armor = floor(armor)

        return armor