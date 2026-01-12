"""Модуль расчётов боевых характеристик: урон, броня, награды.

Содержит калькуляторы для вычисления характеристик игрока и врага на основе
оборудования, уровня и множителей редкости.
"""
from typing import Dict
from ...db.models import InventoryItems, ItemRarityEnum, ItemTypeEnum, Users, Enemies, EnemyTypeEnum
from ...services.inventory import InventoryService
from ...db.schemas.items import WeaponAttributes, ArmorAttributes
from random import random, gauss, randint
from math import floor

# TODO: Сделать классы для обработки общего урона-брони для используемых предметов

class BaseCalculation:
    """Базовый класс для всех калькуляторов боевых характеристик.
    
    Инициализирует сервис инвентаря для получения оборудованного оружия/брони.
    """
    def __init__(self) -> None:
        self.inventory_service = InventoryService()

class DamageCalculation(BaseCalculation):
    """Рассчитывает урон оружия игрока с учётом критов и множителя скорости атаки.
    
    Алгоритм:
    1. Получает оборудованное оружие из инвентаря
    2. Генерирует базовый урон в диапазоне [min_damage, max_damage]
    3. Применяет критический удар с вероятностью critical_chance
    4. Умножает на скорость атаки (attack_speed)
    5. Применяет бонус от уровня предмета (+2% за уровень)
    """
    async def calculate_damage(self, user: Users) -> int:
        """Вычисляет финальный урон оружия игрока.
        
        Args:
            user (Users): объект игрока (содержит уровень)
            
        Returns:
            int: итоговый урон (≥0). Возвращает 0, если оружие не экипировано.
            
        Примеры:
            - Без оружия → 0
            - С оружием урон 10-15, крит 20%, мультипликатор 1.5, скорость 1.0 → ≈12-18
        """
        equipped_item = await self.inventory_service.get_equipped_item(user, ItemTypeEnum.WEAPON)
        if not equipped_item or not equipped_item.item:
            return 0

        weapon_attributes = equipped_item.item.attributes if equipped_item.item.attributes else {}
        
        min_dmg = weapon_attributes.get("min_damage", 1)
        max_dmg = weapon_attributes.get("max_damage", 1)
        damage = randint(int(min_dmg), int(max_dmg))
        
        crit_chance = weapon_attributes.get("critical_chance", 0.0)
        if random() < crit_chance:
            crit_mult = weapon_attributes.get("critical_multiplier", 1.0)
            damage = int(damage * crit_mult)
        
        attack_speed = weapon_attributes.get("attack_speed", 1.0)
        damage = int(damage * attack_speed)
        
        item_level = weapon_attributes.get("item_level", 0)
        if item_level:
            damage = int(damage * (1 + (item_level * 0.02)))
        
        return max(damage, 0)


class ArmorCalculation(BaseCalculation):
    """Рассчитывает броню из экипированной брони с учётом бонусов и уровня.
    
    Формула брони включает:
    - Базовое значение защиты (defense) из предмета
    - Случайный бонус здоровья (health_bonus * random[0, 1])
    - Бонус от уровня предмета (+2% за уровень)
    """
    async def calculate_armor(self, user: Users) -> float:
        """Вычисляет финальную броню игрока.
        
        Args:
            user (Users): объект игрока
            
        Returns:
            float: значение брони (≥0). Возвращает 0, если броня не экипирована.
            
        Примеры:
            - Без брони → 0
            - С бронёй defence=20, health_bonus=5 → 20-25 (с 50% дисперсией)
        """
        equipped_item = await self.inventory_service.get_equipped_item(user, ItemTypeEnum.ARMOR)
        if not equipped_item or not equipped_item.item:
            return 0.0

        armor_attributes = equipped_item.item.attributes if equipped_item.item.attributes else {}

        defense = armor_attributes.get("defense", 1)
        armor = float(defense)
        
        health_bonus = armor_attributes.get("health_bonus", 0)
        armor = armor * (1.0 + (health_bonus * random()))
        
        item_level = armor_attributes.get("item_level", 0)
        if item_level:
            armor = armor * (1.0 + (item_level * 0.02))
        
        return max(armor, 0.0)


# TODO : Сделать рандомным, подключить userservice и сделать получение lvl.
# ! : Есть критические ошибки в данном сегменте!
class EnemyCalculator:
    """Калькулятор статистики врага и наград за бой.
    
    Статистика врага зависит от:
    - Типа врага (обычный, элита, босс) — множитель редкости
    - Уровня игрока — базовый множитель
    - Параметров врага (health_multiplier, damage_multiplier)
    - Параметров игрока (урон оружия, броня) — влияют на расчёты
    
    Множители редкости:
        COMMON: 1.0 (обычный враг)
        ELITE:  2.3 (усиленный враг)
        BOSS:   8.0 (боссовый враг)
    """
    RARITY_BONUS = {
        EnemyTypeEnum.COMMON: 1.0,
        EnemyTypeEnum.ELITE:  2.3,
        EnemyTypeEnum.BOSS:   8.0,
    }
    BASE_COIN = 1
    BASE_EXP = 1

    async def get_stats(self, enemy: Enemies, user: Users) -> Dict[str, int]:
        """Вычисляет статистику врага на основе его типа и параметров игрока.
        
        Формула HP врага:
            hp = floor(user_level * health_multiplier * (1 + user_armor) * 0.85 * rarity_bonus * 0.85)
        
        Формула урона врага:
            damage = floor(user_level * damage_multiplier * (1 + user_damage) * 0.85 * rarity_bonus * 0.85)
        
        Args:
            enemy (Enemies): объект врага из БД (содержит множители)
            user (Users): объект игрока (содержит уровень)
            
        Returns:
            Dict[str, int]: словарь с ключами:
                - 'hp': здоровье врага (≥1)
                - 'damage': урон врага (≥1)
        """
        bonus = self.RARITY_BONUS.get(enemy.type, 1.0)

        user_damage = await DamageCalculation().calculate_damage(user)
        user_armor = await ArmorCalculation().calculate_armor(user)
        
        hp = floor(
            user.lvl
            * enemy.health_multiplier
            * (1 + user_armor) * 0.85
            * bonus * 0.85
        )
        damage = floor(
            user.lvl    
            * enemy.damage_multiplier
            * (1 + user_damage) * 0.85
            * bonus * 0.85
        )

        return {
            "hp": max(hp, 1),
            "damage": max(damage, 1),
        }

    async def get_rewards(self, enemy: Enemies, player_level: int) -> Dict[str, int]:
        """Рассчитывает награды за победу над врагом.
        
        Награда зависит от множителей врага и его редкости.
        
        Формула:
            coin = floor(coin_reward_multiplier * BASE_COIN * rarity_bonus)
            exp = floor(exp_reward_multiplier * BASE_EXP * rarity_bonus)
        
        Args:
            enemy (Enemies): объект врага (содержит множители reward)
            player_level (int): уровень игрока (не используется в текущей версии)
            
        Returns:
            Dict[str, int]: словарь с ключами:
                - 'coin': количество монет (≥1)
                - 'exp': количество опыта (≥1)
                
        Примеры:
            - Обычный враг с coin_reward_multiplier=10 → ≈10 монет
            - Босс (8.0x) с coin_reward_multiplier=5 → ≈40 монет
        """
        rarity_bonus = self.RARITY_BONUS.get(enemy.type, 1.0)

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
    
    async def get_drop_chance(self, enemy: Enemies, player_level: int) -> float:
        """Рассчитывает шанс дропа предметов от врага.
        
        Бонус к шансу дропа зависит от уровня игрока:
        - На каждые 10 уровней + 5% шанса дропа (макс. +25% на уровне 50)
        - Итоговый шанс не превышает 100%
        
        Формула:
            bonus = min(player_level // 10, 5) * 5%
            final_chance = min(100.0, enemy.drop_chance + bonus)
        
        Args:
            enemy (Enemies): объект врага (содержит базовый drop_chance)
            player_level (int): уровень игрока
            
        Returns:
            float: шанс дропа в диапазоне [0.0, 100.0] (%)
            
        Примеры:
            - Враг с drop_chance=25%, уровень игрока 5 → 25% (бонус =0)
            - Враг с drop_chance=25%, уровень игрока 25 → 50% (бонус +25%)
            - Враг с drop_chance=80%, уровень игрока 40 → 100% (ограничение)
        """
        bonus = min(player_level // 10, 5)  # +5% за каждые 10 уровней
        return min(100.0, enemy.drop_chance + bonus)
    