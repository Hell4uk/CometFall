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

# src/bot/game/calculate/enemy.py
from math import floor
from bot.db.models import Enemies
from typing import Dict


class EnemyCalculator:
    BASE_HP      = 12
    BASE_DAMAGE  = 9
    BASE_GOLD    = 18
    BASE_EXP     = 25

    RARITY_BONUS = {
        "common": 1.0,
        "elite":  2.3,
        "boss":   8.0,
    }

    def get_stats(self, enemy: Enemies, player_level: int) -> Dict[str, int]:
        rarity_bonus = self.RARITY_BONUS.get(enemy.type.value, 1.0)

        hp = floor(
            player_level
            * enemy.health_multiplier
            * self.BASE_HP
            * rarity_bonus
        )
        damage = floor(
            player_level
            * enemy.damage_multiplier
            * self.BASE_DAMAGE
            * rarity_bonus
        )

        return {
            "hp": max(hp, 1),
            "damage": max(damage, 1),
        }

    def get_rewards(self, enemy: Enemies, player_level: int) -> Dict[str, int]:
        rarity_bonus = self.RARITY_BONUS.get(enemy.type.value, 1.0)

        gold = floor(
            player_level
            * enemy.gold_reward_multiplier
            * self.BASE_GOLD
            * rarity_bonus
        )
        exp = floor(
            player_level
            * enemy.exp_reward_multiplier
            * self.BASE_EXP
            * rarity_bonus
        )

        return {
            "gold": max(gold, 1),
            "exp": max(exp, 1),
        }

    def get_drop_chance(self, enemy: Enemies, player_level: int) -> float:
        bonus = min(player_level // 10, 5)  # +5% за каждые 10 уровней
        return min(100.0, enemy.drop_chance + bonus)