from typing import Dict, List, Optional, Tuple

from ....db.models import ItemRarityEnum, ItemTypeEnum, Items

from .state import RARITY_SEQUENCE


def rarity_slug_to_enum(slug: str) -> Optional[ItemRarityEnum]:
    mapping = {
        "common": ItemRarityEnum.COMMON,
        "rare": ItemRarityEnum.RARE,
        "epic": ItemRarityEnum.EPIC,
        "legendary": ItemRarityEnum.LEGENDARY,
    }
    return mapping.get(slug)


def item_type_from_slug(slug: str) -> ItemTypeEnum:
    return ItemTypeEnum.WEAPON if slug == "weapon" else ItemTypeEnum.ARMOR


def slug_from_item_type(item_type: ItemTypeEnum) -> str:
    return "weapon" if item_type == ItemTypeEnum.WEAPON else "armor"


def price_matches(price: Optional[int], filters: Dict[str, Optional[int | str]]) -> bool:
    min_price = filters.get("min_price")
    max_price = filters.get("max_price")

    if min_price is None and max_price is None:
        return True
    if price is None:
        return False
    if min_price is not None and price < min_price:
        return False
    if max_price is not None and price > max_price:
        return False
    return True


def next_rarity_slug(current: str) -> str:
    if current not in RARITY_SEQUENCE:
        return RARITY_SEQUENCE[0]
    idx = RARITY_SEQUENCE.index(current)
    return RARITY_SEQUENCE[(idx + 1) % len(RARITY_SEQUENCE)]


def format_item_description(item: Items) -> str:
    attrs = item.attributes or {}
    min_damage = attrs.get("min_damage")
    max_damage = attrs.get("max_damage")
    attack_speed = attrs.get("attack_speed")

    avg_damage = None
    if isinstance(min_damage, (int, float)) and isinstance(max_damage, (int, float)):
        avg_damage = (min_damage + max_damage) / 2

    avg_damage_text = f"{avg_damage:.1f}" if avg_damage is not None else "—"
    attack_speed_text = f"{attack_speed:.2f}" if isinstance(attack_speed, (int, float)) else "—"
    description = item.description or "Описание отсутствует."

    return (
        f"{item.name}:\n\n"
        f"Описание: {description}\n\n"
        f"Средний урон: {avg_damage_text}\n"
        f"Скорость атаки: {attack_speed_text}"
    )

