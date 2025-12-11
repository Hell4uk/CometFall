from .deps import enemy_service, user_service, inventory_service, enemy_calculator, armor_calculator, damage_calculator
from .....db.models import Users, Items, Locations, Enemies


async def find_location_by_name(location_name: str) -> Locations:
    location = await Locations.get_or_none(name=location_name)
    if not location:
        raise Exception('Location not founded')

    return location

async def check_available_location(user: Users, location: Locations) -> bool:
    if user.lvl < location.level_required:
        return True
    else:
        return False

async def reduce_damage(raw_damage: float, target_armor: float, k: float = 80.0) -> float:
    return raw_damage * (1 - target_armor / (target_armor + k))

async def fighting(user: Users, location: Locations):
    await check_available_location(user, location)

    enemy = await enemy_service.spawn(user, location)

    enemy_stats = await enemy_calculator.get_stats(enemy, user)
    enemy_hp = enemy_stats['hp']
    enemy_damage = enemy_stats['damage']

    user_damage = await damage_calculator.calculate_damage(user)
    user_hp = await armor_calculator.calculate_armor(user)

    user_effective_damage = await reduce_damage(user_damage, user_hp)
    enemy_effective_damage = await reduce_damage(enemy_damage, enemy_hp)

    hits_to_kill_enemy = enemy_hp / max(user_effective_damage, 0.001)
    hits_to_kill_user = user_hp / max(enemy_effective_damage, 0.001)

    user_wins = hits_to_kill_enemy <= hits_to_kill_user

    rewarding = await enemy_calculator.get_rewards(enemy, user.lvl)
    drop_chance = await enemy_calculator.get_drop_chance(enemy, user.lvl)


    return {
        'winner': 'user' if user_wins else 'emeny',
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