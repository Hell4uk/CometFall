"""Вспомогательные функции для системы боя 1vs1.

Содержит функции поиска локаций, расчёт боя, формулы урона и брони.
"""
from .deps import enemy_service, user_service, inventory_service, enemy_calculator, armor_calculator, damage_calculator
from .....db.models import Users, Items, Locations, Enemies


class LocationNotFound(Exception):
    """Raised when location cannot be found in database."""
    pass


async def find_location_by_name(location_name: str) -> Locations:
    """Ищет локацию по имени.
    
    Args:
        location_name (str): имя локации
        
    Returns:
        Locations: найденная локация
        
    Raises:
        LocationNotFound: если локация не найдена
    """
    location = await Locations.get_or_none(name=location_name)
    if not location:
        raise LocationNotFound(f'Location with name "{location_name}" not found')
    return location

async def find_location_by_id(location_id: int) -> Locations:
    """Ищет локацию по ID.
    
    Args:
        location_id (int): ID локации
        
    Returns:
        Locations: найденная локация
        
    Raises:
        LocationNotFound: если локация не найдена
    """
    location = await Locations.get_or_none(id=location_id)
    if not location:
        raise LocationNotFound(f'Location with id {location_id} not found')
    
    return location

async def check_available_location(user: Users, location: Locations) -> bool:
    """Проверяет, может ли игрок посетить локацию.
    
    Args:
        user (Users): игрок
        location (Locations): локация
        
    Returns:
        bool: True если уровень игрока >= требуемому уровню локации
    """
    # True if user's level >= location's required level
    return user.lvl >= location.level_required

def reduce_damage(raw_damage: float, target_armor: float, k: float = 80.0) -> float:
    """Рассчитывает эффективный урон с учётом брони.
    
    Формула урона брони (Dota-подобная):
        effective_dmg = raw_damage * (1 - armor / (armor + k))
    
    Где k — постоянная, определяющая влияние брони (по умолчанию 80).
    - Чем выше armor → тем ниже effective_damage
    - armor = 0 → 100% урона
    - armor = k → 50% урона
    - armor → ∞ → 0% урона (асимптота)
    
    Args:
        raw_damage (float): исходный урон до брони
        target_armor (float): броня цели
        k (float): константа для расчёта (по умолчанию 80)
        
    Returns:
        float: эффективный урон после учёта брони
    """

async def fighting(user: Users, location: Locations):
    """Симулирует бой между игроком и врагом.
    
    Полный процесс боя:
    1. Проверяет доступность локации (уровень игрока)
    2. Спавнит врага в локации
    3. Получает статистику врага (HP, urón)
    4. Получает статистику игрока (урон оружия, броня)
    5. Рассчитывает эффективный урон (с учётом брони)
    6. Определяет победителя по числу ударов до K.O.
    7. Получает награды и шанс дропа
    
    Победитель = тот, кому требуется меньше ударов чтобы убить противника.
    
    Args:
        user (Users): игрок, начинающий бой
        location (Locations): локация боя
        
    Returns:
        Dict: результат боя с ключами:
            - 'winner': 'user' или 'enemy'
            - 'enemy_hp', 'enemy_dmg': характеристики врага
            - 'user_hp', 'user_dmg': характеристики игрока
            - 'user_effective_dmg', 'enemy_effective_dmg': урон с учётом брони
            - 'hits_to_kill_user', 'hits_to_kill_enemy': удары до смерти
            - 'reward': словарь с coin и exp
            - 'drop_chance': процент дропа (%)
            - 'enemy': объект врага (для получения лута)
            
    Raises:
        ValueError: если локация не доступна или нет врагов
    """
    is_available = await check_available_location(user, location)
    if not is_available:
        raise ValueError(f"Location level {location.level_required} required. Current level: {user.lvl}")

    enemy = await enemy_service.spawn(user, location)

    enemy_stats = await enemy_calculator.get_stats(enemy, user)
    enemy_hp = enemy_stats['hp']
    enemy_damage = enemy_stats['damage']

    user_damage = await damage_calculator.calculate_damage(user)
    user_hp = await armor_calculator.calculate_armor(user)

    user_effective_damage = reduce_damage(user_damage, user_hp)
    enemy_effective_damage = reduce_damage(enemy_damage, enemy_hp)

    hits_to_kill_enemy = enemy_hp / max(user_effective_damage, 0.001)
    hits_to_kill_user = user_hp / max(enemy_effective_damage, 0.001)

    user_wins = hits_to_kill_enemy <= hits_to_kill_user

    rewarding = await enemy_calculator.get_rewards(enemy, user.lvl)
    drop_chance = await enemy_calculator.get_drop_chance(enemy, user.lvl)


    return {
        'winner': 'user' if user_wins else 'enemy',
        "enemy_hp": enemy_hp,
        "enemy_dmg": enemy_damage,
        "user_hp": user_hp,
        "user_dmg": user_damage,
        "user_effective_dmg": user_effective_damage,
        "enemy_effective_dmg": enemy_effective_damage,
        'hits_to_kill_user': hits_to_kill_user,
        'hits_to_kill_enemy': hits_to_kill_enemy,
        "reward": rewarding,
        "drop_chance": drop_chance,
        "enemy": enemy,
    }