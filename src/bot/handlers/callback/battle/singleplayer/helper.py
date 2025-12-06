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

async def fighting(user: Users, location: Locations):
    await check_available_location(user, location)

    enemy = await enemy_service.spawn(user, location)

    enemy_stats = await enemy_calculator.get_stats(enemy, user)
    enemy_hp = enemy_stats['hp']
    enemy_damage = enemy_stats['damage']

    user_damage = await damage_calculator.calculate_damage(user)
    user_hp = await armor_calculator.calculate_armor(user)

    return {
        "enemy_hp": enemy_hp,
        "enemy_dmg": enemy_damage,
        "user_hp": user_hp,
        "user_dmg": user_damage,
    }