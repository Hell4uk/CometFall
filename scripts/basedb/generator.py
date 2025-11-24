import sys
from pathlib import Path
from typing import Iterable, Tuple

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.bot.db.database import close_db, init_db
from src.bot.db.models import ItemRarityEnum, ItemTypeEnum, Items

from .constants import (
    ARMOR_PREFIXES,
    ARMOR_SUFFIXES,
    RARITY_ROTATION,
    TOTAL_ARMORS,
    TOTAL_WEAPONS,
    WEAPON_PREFIXES,
    WEAPON_SUFFIXES,
)

RARITY_MAP = {
    "common": ItemRarityEnum.COMMON,
    "rare": ItemRarityEnum.RARE,
    "epic": ItemRarityEnum.EPIC,
    "legendary": ItemRarityEnum.LEGENDARY,
}


def _cycled_value(values: Iterable[str], index: int) -> str:
    sequence = tuple(values)
    return sequence[index % len(sequence)]


def _rarity_for_index(index: int) -> ItemRarityEnum:
    slug = RARITY_ROTATION[index % len(RARITY_ROTATION)]
    return RARITY_MAP[slug]


async def _ensure_default_items():
    sword = await Items.get_or_none(id=1)
    if sword:
        print("Уже есть", sword.name, "(id=1)")
    else:
        sword = await Items.create(
            id=1,
            name="Деревянный меч",
            type=ItemTypeEnum.WEAPON,
            rarity=ItemRarityEnum.COMMON,
            attributes={
                "item_level": 1,
                "min_damage": 5,
                "max_damage": 12,
                "attack_speed": 1.0,
                "critical_chance": 0.05,
                "critical_multiplier": 1.5,
            },
            description="Простой деревянный меч. Лучше, чем кулаки.",
        )
        print("Создан", sword.name, "(id=1)")

    armor = await Items.get_or_none(id=2)
    if armor:
        print("Уже есть", armor.name, "(id=2)")
    else:
        armor = await Items.create(
            id=2,
            name="Тряпичная броня",
            type=ItemTypeEnum.ARMOR,
            rarity=ItemRarityEnum.COMMON,
            attributes={"item_level": 1, "defense": 8, "health_bonus": 20},
            description="Старая одежда. Немного защищает.",
        )
        print("Создана", armor.name, "(id=2)")


async def _bulk_create_weapons(start_index: int, count: int):
    for offset in range(count):
        sequence_index = start_index + offset
        rarity = _rarity_for_index(sequence_index)
        level = sequence_index + 1
        prefix = _cycled_value(WEAPON_PREFIXES, sequence_index)
        suffix = _cycled_value(WEAPON_SUFFIXES, sequence_index // len(WEAPON_PREFIXES))
        name = f"{prefix} {suffix} {level}"

        min_damage = 6 + sequence_index * 2
        max_damage = min_damage + 6 + (sequence_index % 5)
        attack_speed = round(1.0 + (sequence_index % 7) * 0.05, 2)
        crit_chance = round(0.05 + (sequence_index % 4) * 0.03, 2)
        crit_mult = round(1.4 + (sequence_index % 3) * 0.2, 2)

        defaults = {
            "type": ItemTypeEnum.WEAPON,
            "rarity": rarity,
            "attributes": {
                "item_level": level,
                "min_damage": min_damage,
                "max_damage": max_damage,
                "attack_speed": attack_speed,
                "critical_chance": min(crit_chance, 0.65),
                "critical_multiplier": min(crit_mult, 3.5),
            },
            "description": (
                f"Оружие {rarity.name.lower()} класса, выкованное мастерами Кометопада. "
                f"Номер серии {level}."
            ),
        }

        _, created = await Items.get_or_create(name=name, defaults=defaults)
        if created:
            print("Добавлено оружие:", name)


async def _bulk_create_armors(start_index: int, count: int):
    for offset in range(count):
        sequence_index = start_index + offset
        rarity = _rarity_for_index(sequence_index)
        level = sequence_index + 1
        prefix = _cycled_value(ARMOR_PREFIXES, sequence_index)
        suffix = _cycled_value(ARMOR_SUFFIXES, sequence_index // len(ARMOR_PREFIXES))
        name = f"{prefix} {suffix} {level}"

        defense = 10 + sequence_index * 3
        health_bonus = 25 + sequence_index * 5
        defaults = {
            "type": ItemTypeEnum.ARMOR,
            "rarity": rarity,
            "attributes": {
                "item_level": level,
                "defense": defense,
                "health_bonus": health_bonus,
            },
            "description": (
                f"Броня {rarity.name.lower()} класса, созданная для защитников Кометопада. "
                f"Серия {level}."
            ),
        }

        _, created = await Items.get_or_create(name=name, defaults=defaults)
        if created:
            print("Добавлена броня:", name)


async def create_base_items():
    await init_db()
    try:
        await _ensure_default_items()

        extra_weapons = TOTAL_WEAPONS - 1
        extra_armors = TOTAL_ARMORS - 1

        await _bulk_create_weapons(start_index=1, count=extra_weapons)
        await _bulk_create_armors(start_index=1, count=extra_armors)

        print("Генерация предметов завершена.")
    finally:
        await close_db()


__all__ = ("create_base_items",)

