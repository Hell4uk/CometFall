"""Скрипт для инициализации кейсов в БД.

Добавляет стартовый набор кейсов с разными коллекциями и редкостью.
Каждый кейс содержит случайные предметы с весами вероятности выпадения.

Использование:
    python scripts/init_cases.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tortoise import Tortoise
from src.bot.db.database import close_db, init_db
from src.bot.db.models import Items, ItemTypeEnum, ItemRarityEnum

# Данные для кейсов
CASES = [
    {
        "name": "Обычный кейс",
        "description": "Содержит обычные предметы различных типов",
        "rarity": ItemRarityEnum.COMMON,
        "type": ItemTypeEnum.CASE,
        "attributes": {
            "collection": "Базовая",
            "is_limited": False,
            "max_opens": None,
            "storage": [
                # Оружие (ID 1-10)
                {"item_id": 1, "weight": 0.3},
                {"item_id": 2, "weight": 0.3},
                # Броня (ID 11-20)
                {"item_id": 11, "weight": 0.25},
                {"item_id": 12, "weight": 0.15}
            ]
        }
    },
    {
        "name": "Редкий кейс",
        "description": "Содержит редкие и ценные предметы",
        "rarity": ItemRarityEnum.RARE,
        "type": ItemTypeEnum.CASE,
        "attributes": {
            "collection": "Поиск приключений",
            "is_limited": False,
            "max_opens": None,
            "storage": [
                # Оружие с выше шансом
                {"item_id": 3, "weight": 0.4},
                {"item_id": 4, "weight": 0.35},
                # Броня
                {"item_id": 13, "weight": 0.25}
            ]
        }
    },
    {
        "name": "Эпический кейс",
        "description": "Редкий кейс с мощными артефактами",
        "rarity": ItemRarityEnum.EPIC,
        "type": ItemTypeEnum.CASE,
        "attributes": {
            "collection": "Легенды войны",
            "is_limited": False,
            "max_opens": None,
            "storage": [
                # Легендарное оружие
                {"item_id": 5, "weight": 0.5},
                {"item_id": 6, "weight": 0.5}
            ]
        }
    },
    {
        "name": "Легендарный кейс",
        "description": "Самый редкий кейс. Гарантированно содержит легендарный предмет",
        "rarity": ItemRarityEnum.LEGENDARY,
        "type": ItemTypeEnum.CASE,
        "attributes": {
            "collection": "Сокровища богов",
            "is_limited": True,
            "max_opens": 100,
            "storage": [
                # Только легендарные предметы
                {"item_id": 7, "weight": 0.5},
                {"item_id": 8, "weight": 0.5}
            ]
        }
    },
    {
        "name": "Рождественский кейс",
        "description": "Праздничный кейс с особыми предметами",
        "rarity": ItemRarityEnum.EPIC,
        "type": ItemTypeEnum.CASE,
        "attributes": {
            "collection": "Праздники",
            "is_limited": True,
            "max_opens": 500,
            "storage": [
                {"item_id": 9, "weight": 0.6},
                {"item_id": 14, "weight": 0.4}
            ]
        }
    },
    {
        "name": "Стартовый набор",
        "description": "Идеален для новых игроков. Содержит полезные начальные предметы",
        "rarity": ItemRarityEnum.COMMON,
        "type": ItemTypeEnum.CASE,
        "attributes": {
            "collection": "Начинающий",
            "is_limited": False,
            "max_opens": None,
            "storage": [
                {"item_id": 1, "weight": 0.5},
                {"item_id": 11, "weight": 0.5}
            ]
        }
    }
]


async def create_cases():
    """Создаёт кейсы в БД или обновляет существующие."""
    created_count = 0
    updated_count = 0
    
    for case_data in CASES:
        case, created = await Items.get_or_create(
            name=case_data["name"],
            defaults={
                "description": case_data["description"],
                "type": case_data["type"],
                "rarity": case_data["rarity"],
                "attributes": case_data["attributes"]
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Создан кейс: {case.name} (ID={case.id}, редкость={ItemRarityEnum(case.rarity).name})")
        else:
            # Обновляем существующий кейс
            case.description = case_data["description"]
            case.type = case_data["type"]
            case.rarity = case_data["rarity"]
            case.attributes = case_data["attributes"]
            await case.save()
            updated_count += 1
            print(f"🔄 Обновлен кейс: {case.name} (ID={case.id})")
    
    print(f"\n📊 Итого: создано {created_count}, обновлено {updated_count}")


async def main():
    """Главная функция для инициализации кейсов."""
    await init_db()
    try:
        print("🎁 Инициализация кейсов в БД...\n")
        await create_cases()
        print("\n✅ Кейсы успешно добавлены!")
    except Exception as e:
        print(f"\n❌ Ошибка при инициализации кейсов: {e}")
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
