import sys
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).resolve().parents[2]))

from tortoise import Tortoise

from src.bot.db.database import close_db, init_db
from src.bot.db.models import EnemyTypeEnum, Enemies, Locations

from .constants import LOCATIONS, ENEMIES

TYPE_MAP = {
    "COMMON": EnemyTypeEnum.COMMON,
    "ELITE": EnemyTypeEnum.ELITE,
    "BOSS": EnemyTypeEnum.BOSS,
}


async def _reset_sequences():
    """Reset PostgreSQL sequences to match the maximum IDs in tables."""
    # Get the maximum IDs using Tortoise ORM
    max_location = await Locations.all().order_by("-id").first()
    max_enemy = await Enemies.all().order_by("-id").first()
    
    max_location_id = max_location.id if max_location else 0
    max_enemy_id = max_enemy.id if max_enemy else 0
    
    # Reset sequences
    conn = Tortoise.get_connection("default")
    next_location_id = max(max_location_id, 1)
    next_enemy_id = max(max_enemy_id, 1)
    
    await conn.execute_query(f"SELECT setval('locations_id_seq', {next_location_id}, true);")
    await conn.execute_query(f"SELECT setval('enemies_id_seq', {next_enemy_id}, true);")


async def create_locations():
    """Create locations from constants."""
    location_map = {}
    
    for loc_data in LOCATIONS:
        location, created = await Locations.get_or_create(
            name=loc_data["name"],
            defaults={
                "description": loc_data["description"],
                "level_required": loc_data["level_required"],
            }
        )
        
        if created:
            print(f"Создана локация: {location.name} (id={location.id})")
        else:
            print(f"Локация уже существует: {location.name} (id={location.id})")
        
        location_map[location.name] = location
    
    return location_map


async def create_enemies(location_map: Dict[str, Locations]):
    """Create enemies from constants and link them to locations."""
    for enemy_data in ENEMIES:
        enemy, created = await Enemies.get_or_create(
            name=enemy_data["name"],
            defaults={
                "description": enemy_data["description"],
                "type": TYPE_MAP[enemy_data["type"]],
                "health_multiplier": enemy_data["health_multiplier"],
                "damage_multiplier": enemy_data["damage_multiplier"],
                "coin_reward_multiplier": enemy_data["coin_reward_multiplier"],
                "exp_reward_multiplier": enemy_data["exp_reward_multiplier"],
                "drop_chance": enemy_data["drop_chance"],
                "is_active": True,
            }
        )
        
        if created:
            print(f"Создан враг: {enemy.name} (id={enemy.id}, тип={enemy.type.name})")
        else:
            print(f"Враг уже существует: {enemy.name} (id={enemy.id})")
        
        # Связываем врага с локациями
        for location_name in enemy_data["location_names"]:
            if location_name in location_map:
                location = location_map[location_name]
                # Проверяем, не связан ли уже враг с этой локацией
                existing_locations = await enemy.locations.all()
                if location not in existing_locations:
                    await enemy.locations.add(location)
                    print(f"  → Связан с локацией: {location.name}")
            else:
                print(f"  ⚠ Локация '{location_name}' не найдена для врага {enemy.name}")


async def create_game_data():
    """Main function to create all game data (locations and enemies)."""
    await init_db()
    try:
        print("=" * 50)
        print("Создание локаций...")
        print("=" * 50)
        location_map = await create_locations()
        
        print("\n" + "=" * 50)
        print("Создание врагов...")
        print("=" * 50)
        await create_enemies(location_map)
        
        # Reset sequences after creating items with explicit IDs
        await _reset_sequences()
        
        print("\n" + "=" * 50)
        print("Генерация локаций и врагов завершена.")
        print("=" * 50)
    finally:
        await close_db()


__all__ = ("create_game_data",)

