"""Сервис управления предметами в системе.

Обрабатывает создание, валидацию и CRUD операции над предметами.
Использует Pydantic-схемы для валидации атрибутов каждого типа предмета.
"""
from typing import Optional, Type, List, Dict, Union

from ...bot.db.models import Items, ItemTypeEnum, ItemRarityEnum
from ...bot.db.schemas.items import ArmorAttributes, BaseAttributes, WeaponAttributes
from pydantic import ValidationError

SCHEMAS_MAP = {
    ItemTypeEnum.WEAPON: WeaponAttributes,
    ItemTypeEnum.ARMOR: ArmorAttributes,
}


class ItemService:
    """Сервис управления предметами.
    
    Валидирует атрибуты через Pydantic-схемы и обеспечивает типобезопасность.
    Поддерживает расширяемость: новые типы предметов добавляются в SCHEMAS_MAP.
    """
    def __init__(self, schemas_map: Optional[Dict[ItemTypeEnum, Type[BaseAttributes]]] = None):
        self.schemas_map = schemas_map or SCHEMAS_MAP

    def _get_schema_class(self, item_type: Union[ItemTypeEnum, int]) -> Type[BaseAttributes]:
        # Accept either ItemTypeEnum or its int value
        if isinstance(item_type, int):
            item_type = ItemTypeEnum(item_type)

        schema_cls = self.schemas_map.get(item_type)
        if not schema_cls:
            raise ValueError(f"Unsupported item type: {item_type}")
        return schema_cls

    def _validate_attributes(self, item_type: Union[ItemTypeEnum, int], attributes: dict) -> dict:
        schema_cls = self._get_schema_class(item_type)
        try:
            validated = schema_cls(**attributes)
            return validated.dict()

        except ValidationError as _ex:
            raise ValueError(f'Invalid attributes for {item_type}: {_ex.errors()}')

    async def create(self, name: str, item_type: ItemTypeEnum, item_rarity: ItemRarityEnum, attributes: dict) -> Items:
        """Создаёт новый предмет или возвращает существующий.
        
        Валидирует атрибуты через соответствующую Pydantic-схему.
        Использует get_or_create → если предмет с таким name существует, возвращает его.
        
        Args:
            name (str): имя предмета
            item_type (ItemTypeEnum): тип (WEAPON, ARMOR и т.д.)
            item_rarity (ItemRarityEnum): редкость (COMMON, RARE, EPIC, LEGENDARY)
            attributes (dict): словарь атрибутов (валидируется схемой)
            
        Returns:
            Items: созданный или найденный предмет
            
        Raises:
            ValueError: если атрибуты не проходят валидацию
        """
        valid_attrs = self._validate_attributes(item_type, attributes)

        item, _created = await Items.get_or_create(name=name, defaults={
            "rarity": item_rarity,
            "type": item_type,
            "attributes": valid_attrs,
        })

        return item

    async def get_by_id(self, item_id: int) -> Optional[Items]:
        item = await Items.get_or_none(id=item_id)
        return item

    async def get_by_name(self, item_name: str) -> Optional[List[Items]]:
        items = await Items.filter(name=item_name).all()
        return items

    async def get_by_type(self, item_type: ItemTypeEnum) -> Optional[List[Items]]:
        items = await Items.filter(type=item_type).all()
        return items

    async def update(self, item_id: int, **updates: any) -> Items:
        """Обновляет предмет (атрибуты, имя, редкость).
        
        Если изменяются атрибуты → валидирует через текущую схему типа предмета.
        
        Args:
            item_id (int): ID предмета
            **updates: ключи 'name', 'rarity', 'attributes'
            
        Returns:
            Items: обновленный предмет
            
        Raises:
            ValueError: если предмет не найден или атрибуты невалидны
        """
        item = await self.get_by_id(item_id)
        if not item:
            raise ValueError("Item not found")

        if "attributes" in updates:
            item.attributes = self._validate_attributes(item.type, updates["attributes"])

        if "name" in updates:
            item.name = updates["name"]

        if "rarity" in updates:
            item.rarity = updates["rarity"]

        await item.save()
        return item

    async def delete(self, item_id: int):
        item = await self.get_by_id(item_id)
        if not item:
            raise ValueError("Item not found")
        await item.delete()