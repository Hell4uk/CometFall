from typing import Dict
from ...db.models import InventoryItems, ItemRarityEnum, ItemTypeEnum, Users, Enemies, EnemyTypeEnum
from ...services.inventory import InventoryService
from ...db.schemas.items import WeaponAttributes, ArmorAttributes
from random import random, gauss, randint
from math import floor

# TODO: Сделать классы для обработки общего урона-брони для используемых предметов

class BaseCalculation:
    def __init__(self) -> None:
        self.inventory_service = InventoryService()

class DamageCalculation(BaseCalculation):
    async def calculate_damage(self, user: Users) -> int:
        equipped_item = await self.inventory_service.get_equipped_item(user, ItemTypeEnum.WEAPON)
        if not equipped_item:
            return 0

        weapon_attributes = equipped_item.item.attributes
        
        damage = gauss(weapon_attributes.get("min_damage"), weapon_attributes.get("max_damage"))
        if random() < weapon_attributes.get("critical_chance"):
            damage *= weapon_attributes.get("critical_multiplier")
        
        damage *= weapon_attributes.get("attack_speed")
        damage *= 1 + (weapon_attributes.get("item_level") * 0.02) 
        damage = floor(damage)

        return damage


class ArmorCalculation(BaseCalculation):
    async def calculate_armor(self, user: Users) -> float:
        equipped_item = await self.inventory_service.get_equipped_item(user, ItemTypeEnum.ARMOR)
        if not equipped_item:
            return 0

        armor_attributes = equipped_item.item.attributes

        armor = armor_attributes.get("defense")
        armor *= 1 + (armor_attributes.get("health_bonus") * random())
        armor *= 1 + (armor_attributes.get("item_level") * 0.02)
        armor = floor(armor)

        return armor


# TODO : Сделать рандомным, подключить userservice и сделать получение lvl.
# ! : Есть критические ошибки в данном сегменте!
class EnemyCalculator:
    RARITY_BONUS = {
        EnemyTypeEnum.COMMON: 1.0,
        EnemyTypeEnum.ELITE:  2.3,
        EnemyTypeEnum.BOSS:   8.0,
    }

    async def get_stats(self, enemy: Enemies, user: Users) -> Dict[str, int]:
        bonus = self.RARITY_BONUS.get(enemy.type, 1.0)

        user_damage = await DamageCalculation(user).calculate_damage()
        user_armor = await ArmorCalculation(user).calculate_armor()
        
        hp = floor(
            0
            * enemy.health_multiplier
            * (1+ user_armor) * 0.85
            * bonus * 0.85
        )
        damage = floor(
            0    
            * enemy.damage_multiplier
            * (1 + user_damage) * 0.85
            * bonus * 0.85
        )

        return {
            "hp": max(hp, 1),
            "damage": max(damage, 1),
        }

    def get_rewards(self, enemy: Enemies, player_level: int) -> Dict[str, int]:
        rarity_bonus = self.RARITY_BONUS.get(enemy.type.value, 1.0)

        coin = floor(
            enemy.coin_reward_multiplier
            * self.BASE_COIN
            * rarity_bonus
        )   
        exp = floor(
            enemy.exp_reward_multiplier
            * self.BASE_EXP
            * rarity_bonus
        )

        return {
            "coin": max(coin, 1),
            "exp": max(exp, 1),
        }
    
    def get_drop_chance(self, enemy: Enemies, player_level: int) -> float:
        bonus = min(player_level // 10, 5)  # +5% за каждые 10 уровней
        return min(100.0, enemy.drop_chance + bonus)