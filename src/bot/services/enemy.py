"""Сервис управления врагами и боевой логикой.

Обрабатывает спавн врагов по уровню, расчёт наград и выпадение лута.
Интегрирует калькулятор боевых характеристик для расчёта HP и урона врага.
"""
from .inventory import InventoryService
from ..db.models import Enemies, Items, Users, EnemyTypeEnum, Locations
from typing import List, Dict
from ..game.logic.calculation import EnemyCalculator
from random import choice, random
from math import floor

# TODO : Перепроверить все
class EnemyService():
    """Сервис для управления врагами и боевыми наградами.
    
    Функциональность:
    - Выбор врага по уровню игрока и локации
    - Расчёт статистики врага (HP, урон)
    - Выдача наград (монеты, опыт, лут)
    - Система уровней врагов (COMMON, ELITE, BOSS)
    """
    def __init__(self) -> None:
        self.calc = EnemyCalculator()
        self.inventory = InventoryService()

    async def spawn(self, user: Users, location: Locations) -> Enemies:
        """Выбирает случайного врага для боя в локации.
        
        Алгоритм:
        1. Определяет тип врага (COMMON/ELITE/BOSS) на основе уровня
        2. Ищет врагов этого типа в данной локации
        3. Если нет → ищет врагов типа в любой локации
        4. Выбирает случайного из найденных
        
        Args:
            user (Users): игрок (уровень влияет на тип врага)
            location (Locations): локация для боя
            
        Returns:
            Enemies: выбранный враг
            
        Raises:
            ValueError: если нет доступных врагов
        """
        level = max(1, user.lvl)
        rarity = self._get_rarity(level)
        candidates = await Enemies.filter(
            type=rarity,
            is_active=True,
            locations__id=location.id
        ).all()

        if not candidates:
            candidates = await Enemies.filter(type=rarity, is_active=True).all()
        if not candidates:
            raise ValueError("No enemies available for this level")
        return choice(candidates)

    async def get_battle_stats(self, enemy: Enemies, user: Users) -> Dict:
        return await self.calc.get_stats(enemy, user)  # await

    async def give_reward(self, user: Users, enemy: Enemies, exp: int, coins: int) -> Dict:
        """Выдаёт награды за победу над врагом.
        
        Процесс:
        1. Добавляет монеты и опыт к игроку
        2. Проверяет повышение уровня (требуется 65*(level+1) опыта)
        3. Разыгрывает лут (drop_items) с шансом дропа
        4. Добавляет выпавший лут в инвентарь
        5. Сохраняет изменения в БД
        
        Args:
            user (Users): игрок, получающий награду
            enemy (Enemies): враг для расчёта лута
            exp (int): количество опыта
            coins (int): количество монет
            
        Returns:
            Dict: результат с ключами:
                - 'coin', 'exp': выданные награды
                - 'level_up': True если повышен уровень
                - 'drop': список выпавшего лута ['name x qty', ...]
        """
        user.coins += coins
        user.exp += exp
        leveled_up = await self._level_up(user)
        drops = await self._roll_drops(enemy)
        for drop in drops:
            await self.inventory.add(user, drop['item'], drop['quantity'])
        await user.save()
        return {
            "coin": coins, "exp": exp,
            'level_up': leveled_up, 'drop': [f"{d['item'].name} x{d['quantity']}" for d in drops]
        }

    def _get_rarity(self, level: int) -> EnemyTypeEnum:
        """Определяет тип врага на основе уровня игрока (взвешенная вероятность).
        
        Уровень < 8:
            100% COMMON
        
        Уровень 8-19:
            20% ELITE (2 из 10)
            80% COMMON (8 из 10)
        
        Уровень ≥ 20:
            40% BOSS (1 из 2.5)
            30% ELITE (3 из 10)
            30% COMMON (4 из 10)
        
        Args:
            level (int): уровень игрока
            
        Returns:
            EnemyTypeEnum: тип врага (COMMON, ELITE, BOSS)
        """
        if level >= 20:
            return choice([EnemyTypeEnum.BOSS] + [EnemyTypeEnum.ELITE] * 3 + [EnemyTypeEnum.COMMON] * 4)
        elif level >= 8:
            return choice([EnemyTypeEnum.ELITE] * 2 + [EnemyTypeEnum.COMMON] * 8)
        return EnemyTypeEnum.COMMON

    async def _roll_drops(self, enemy: Enemies) -> List[Dict]:
        """Разыгрывает выпадение лута от врага.
        
        Алгоритм:
        1. Рассчитывает шанс дропа (базовый + бонус от уровня)
        2. Проверяет вероятность: если не выпадает → возвращает []
        3. Перебирает drop_items врага; каждый с вероятностью 75% добавляется в лут
        
        Args:
            enemy (Enemies): враг
            
        Returns:
            List[Dict]: список лута, каждый элемент:
                {'item': Items, 'quantity': 1}
        """
        chance = await self.calc.get_drop_chance(enemy, 1)  # player_level TODO: from user
        if random() * 100 > chance:
            return []
        drops = []
        drop_items = await enemy.drop_items.all()
        for item in drop_items:
            if random() < 0.75:
                drops.append({"item": item, "quantity": 1})
        return drops

    async def _level_up(self, user: Users) -> bool:
        """Проверяет и применяет повышение уровня.
        
        Требуемый опыт для уровня N: 65 * (N + 1).
        Пока опыт >= требуемого → повышает уровень, вычитает необходимый опыт.
        
        Args:
            user (Users): игрок
            
        Returns:
            bool: True если уровень повысился, иначе False
        """
        old_lvl = user.lvl
        required_exp = 65 * (user.lvl + 1)
        while user.exp >= required_exp:
            user.lvl += 1
            user.exp -= required_exp  
            required_exp = 65 * (user.lvl + 1)

        return user.lvl > old_lvl