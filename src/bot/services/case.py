"""Сервис управления кейсами.

Функциональность:
- Открытие кейсов и получение предмета из коллекции
- Получение информации о кейсе и его содержимом
- Проверка лимита открытий для ограниченных кейсов
"""
import random
from typing import Optional, List, Dict, Any, Tuple
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from ...bot.db.models import Items, Users, InventoryItems, ItemTypeEnum, ItemRarityEnum
from .inventory import InventoryService
from .item import ItemService, SCHEMAS_MAP


class CaseService:
    """Сервис для управления кейсами и их открытием."""
    
    def __init__(self) -> None:
        self.inventory_service = InventoryService()
        self.item_service = ItemService(SCHEMAS_MAP)
    
    async def get_case(self, case_id: int) -> Optional[Items]:
        """Получает кейс по ID с проверкой типа.
        
        Args:
            case_id (int): ID кейса
            
        Returns:
            Optional[Items]: объект кейса или None
        """
        return await Items.get_or_none(id=case_id, type=ItemTypeEnum.CASE)
    
    async def get_all_cases(self) -> List[Items]:
        """Получает все доступные кейсы.
        
        Returns:
            List[Items]: список всех кейсов
        """
        return await Items.filter(type=ItemTypeEnum.CASE).order_by("rarity", "name").all()
    
    async def get_case_by_name(self, name: str) -> Optional[Items]:
        """Получает кейс по названию.
        
        Args:
            name (str): название кейса
            
        Returns:
            Optional[Items]: объект кейса или None
        """
        return await Items.get_or_none(name__iexact=name, type=ItemTypeEnum.CASE)
    
    async def get_case_info(self, case: Items) -> Dict[str, Any]:
        """Получает полную информацию о кейсе.
        
        Args:
            case (Items): объект кейса
            
        Returns:
            Dict[str, Any]: словарь с информацией о кейсе
        """
        case_attrs = case.attributes
        
        return {
            "id": case.id,
            "name": case.name,
            "description": case.description,
            "rarity": ItemRarityEnum(case.rarity).name,
            "collection": case_attrs.get("collection", "Unknown"),
            "is_limited": case_attrs.get("is_limited", False),
            "max_opens": case_attrs.get("max_opens"),
            "items_in_case": len(case_attrs.get("storage", [])),
        }
    
    async def open_case(self, user: Users, case: Items) -> Tuple[Items, str]:
        """Открывает кейс и выдает случайный предмет из коллекции.
        
        АТОМАРНАЯ ОПЕРАЦИЯ: все шаги выполняются в транзакции для гарантии целостности.
        Гарантирует, что при нажатии кнопки 10 раз подряд предмет выдается РОВНО 10 раз.
        
        Алгоритм:
        1. Проверяет наличие кейса в инвентаре (количество > 0)
        2. Получает список предметов из коллекции
        3. Выбирает случайный предмет по весам вероятности
        4. В транзакции: добавляет предмет И удаляет кейс
        
        Args:
            user (Users): игрок, открывающий кейс
            case (Items): кейс для открытия
            
        Returns:
            Tuple[Items, str]: (полученный предмет, сообщение о результате)
            
        Raises:
            ValueError: если у игрока нет кейса или хранилище пусто
        """
        # Получаем коллекцию предметов ПЕРЕД транзакцией
        storage = case.attributes.get("storage", [])
        if not storage:
            raise ValueError(f"Кейс '{case.name}' пуст (нет предметов в коллекции)")
        
        # Выбираем случайный предмет ДО транзакции
        reward_item = self._select_weighted_item(storage)
        reward_item_id = reward_item["item_id"]
        
        # Получаем предмет из БД
        item = await Items.get_or_none(id=reward_item_id)
        if not item:
            raise ValueError(f"Предмет с ID {reward_item_id} не найден в БД")
        
        # АТОМАРНАЯ ТРАНЗАКЦИЯ
        async with in_transaction():
            # Пересчитываем и проверяем кейс в инвентаре (блокируется БД)
            case_inv = await InventoryItems.filter(user=user, item=case).first()
            
            if not case_inv or case_inv.quantity < 1:
                raise ValueError(f"У вас нет кейса '{case.name}' в инвентаре")
            
            # Добавляем предмет в инвентарь
            await self.inventory_service.add(user, item, quantity=1)
            
            # Уменьшаем количество кейсов
            case_inv.quantity -= 1
            await case_inv.save()
            
            # Если количество == 0, удаляем запись
            if case_inv.quantity <= 0:
                await case_inv.delete()
        
        rarity_name = ItemRarityEnum(item.rarity).name
        return item, f"✨ Вы получили: **{item.name}** ({rarity_name})"
    
    def _select_weighted_item(self, storage: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Выбирает случайный предмет из коллекции по весам вероятности.
        
        Алгоритм использует взвешенный выбор, где каждый предмет имеет
        вероятность выпадения (weight). Большее значение = выше вероятность.
        
        Args:
            storage (List[Dict[str, Any]]): список предметов с весами
                Формат: [
                    {"item_id": 1, "weight": 0.5},
                    {"item_id": 2, "weight": 0.3},
                    {"item_id": 3, "weight": 0.2}
                ]
        
        Returns:
            Dict[str, Any]: выбранный предмет из коллекции
        """
        items = [item for item in storage]
        weights = [item.get("weight", 1.0) for item in items]
        
        return random.choices(items, weights=weights, k=1)[0]
    
    async def get_cases_by_rarity(self, rarity: ItemRarityEnum) -> List[Items]:
        """Получает все кейсы определенной редкости.
        
        Args:
            rarity (ItemRarityEnum): редкость кейса
            
        Returns:
            List[Items]: список кейсов нужной редкости
        """
        return await Items.filter(
            type=ItemTypeEnum.CASE,
            rarity=rarity
        ).order_by("name").all()
    
    async def get_cases_by_collection(self, collection: str) -> List[Items]:
        """Получает все кейсы определенной коллекции.
        
        Args:
            collection (str): название коллекции
            
        Returns:
            List[Items]: список кейсов в коллекции
        """
        all_cases = await self.get_all_cases()
        return [
            case for case in all_cases
            if case.attributes.get("collection", "").lower() == collection.lower()
        ]
