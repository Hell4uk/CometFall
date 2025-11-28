from typing import List, Tuple

from ....db.models import ItemTypeEnum
from ....keyboards.inlines.inventory import inventory_items_keyboard, inventory_type_keyboard
from ....services.inventory import InventoryService

from .state import RARITY_ORDER


def item_type_slug(item_type: ItemTypeEnum) -> str:
    return "weapon" if item_type == ItemTypeEnum.WEAPON else "armor"


def item_type_name(item_type: ItemTypeEnum) -> str:
    return "оружия" if item_type == ItemTypeEnum.WEAPON else "брони"


async def collect_items(user, item_type: ItemTypeEnum, inv_service: InventoryService) -> Tuple[List, int]:
    all_items = await inv_service.get(user)
    filtered = [i for i in all_items if i.item.type == item_type]
    filtered.sort(key=lambda x: RARITY_ORDER.get(x.item.rarity, 99))
    total_pages = (len(filtered) + 4) // 5 if filtered else 0
    return filtered, total_pages


def format_item_detail_text(inv_item) -> str:
    item = inv_item.item
    attributes = item.attributes or {}
    description = item.description or "Описание отсутствует."

    parts = [
        f"{item.name}:",
        "",
        f"Описание: {description}",
        "",
    ]

    if "min_damage" in attributes and "max_damage" in attributes:
        min_damage = attributes.get("min_damage")
        max_damage = attributes.get("max_damage")
        attack_speed = attributes.get("attack_speed")

        avg_damage = None
        if isinstance(min_damage, (int, float)) and isinstance(max_damage, (int, float)):
            avg_damage = (min_damage + max_damage) / 2

        parts += [
            f"Средний урон: {avg_damage:.1f}" if avg_damage is not None else "Средний урон: —",
            f"Скорость атаки: {attack_speed:.2f}" if isinstance(attack_speed, (int, float)) else "Скорость атаки: —",
        ]

    elif "defense" in attributes:
        defense = attributes.get("defense")
        health_bonus = attributes.get("health_bonus", 0)

        parts += [
            f"Защита: {defense}" if isinstance(defense, int) else "Защита: —",
            f"Бонус к здоровью: {health_bonus}" if isinstance(health_bonus, int) else "Бонус к здоровью: —",
        ]

    else:
        parts.append("Характеристики: отсутствуют или неизвестный тип предмета.")

    parts += [
        "",
        "Продать — выставить предмет на рынок и получить монеты.",
    ]

    return "\n".join(parts)


async def send_inventory_overview(message, user, item_type: ItemTypeEnum, item_slug: str, inv_service: InventoryService):
    filtered, total_pages = await collect_items(user, item_type, inv_service)
    display_name = user.first_name or user.username or "Игрок"

    if not filtered:
        await message.answer(
            text=f"{display_name}, у вас нет {item_type_name(item_type)}.",
            reply_markup=inventory_type_keyboard(),
        )
        return

    await message.answer(
        text=f"{display_name}, ваша коллекция {item_type_name(item_type)}:",
        reply_markup=inventory_items_keyboard(filtered, 0, total_pages, item_slug),
    )

