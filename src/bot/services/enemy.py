from .inventory import InventoryService
from ..db.models import Enemies, Items, Users, EnemyTypeEnum
from typing import List, Dict
from ..game.logic.calculation import EnemyCalculator
from random import choice, random
from math import floor

# TODO : Перепроверить все
class EnemyService():
    def __init__(self) -> None:
        self.calc = EnemyCalculator()
        self.inventory = InventoryService()

    async def spawn(self, user: Users) -> Enemies:
        level = max(1, user.lvl)
        rarity = self._get_rarity(level)
        candidates = await Enemies.filter(type=rarity, is_active=True).all()
        if not candidates:
            raise ValueError("No enemies available for this level")
        return choice(candidates)

    async def get_battle_stats(self, enemy: Enemies, user: Users) -> Dict:
        return await self.calc.get_stats(enemy, user)  # await

    async def give_reward(self, user: Users, enemy: Enemies) -> Dict:
        stats = self.calc.get_rewards(enemy, user.lvl)
        user.coins += stats['coin']
        user.exp += stats['exp']
        leveled_up = await self._level_up(user)
        drops = await self._roll_drops(enemy)
        for drop in drops:
            await self.inventory.add(user, drop['item'], drop['quantity'])
        await user.save()
        return {
            "coin": stats['coin'], "exp": stats['exp'],
            'level_up': leveled_up, 'drop': [f"{d['item'].name} x{d['quantity']}" for d in drops]
        }

    def _get_rarity(self, level: int) -> EnemyTypeEnum:
        if level >= 20:
            return choice([EnemyTypeEnum.BOSS] + [EnemyTypeEnum.ELITE] * 3 + [EnemyTypeEnum.COMMON] * 4)
        elif level >= 8:
            return choice([EnemyTypeEnum.ELITE] * 2 + [EnemyTypeEnum.COMMON] * 8)
        return EnemyTypeEnum.COMMON

    async def _roll_drops(self, enemy: Enemies) -> List[Dict]:
        chance = self.calc.get_drop_chance(enemy, 1)  # player_level TODO: from user
        if random() * 100 > chance:
            return []
        drops = []
        drop_items = await enemy.drop_items.all()
        for item in drop_items:
            if random() < 0.75:
                drops.append({"item": item, "quantity": 1})
        return drops

    async def _level_up(self, user: Users) -> bool:
        old_lvl = user.lvl
        required_exp = 65 * (user.lvl + 1)
        while user.exp >= required_exp:
            user.lvl += 1
            user.exp -= required_exp  
            required_exp = 65 * (user.lvl + 1)

        return user.lvl > old_lvl