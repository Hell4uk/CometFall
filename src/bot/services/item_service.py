from ast import Dict
from typing import Optional, Type

from tortoise.exceptions import DoesNotExist
from bot.db.models import Item, InventoryItem, ItemTypeEnum, ItemEnum, ItemRarityEnum
from bot.db.schemas.items import ArmorAttributes, BaseAttributes, WeaponAttributes
from pydantic import ValidationError

SCHEMAS_MAP = {
    ItemTypeEnum.WEAPON: WeaponAttributes,
    ItemTypeEnum.ARMOR: ArmorAttributes
}

class ItemService():
    def __init__(self, schemas_map: Optional[Dict[str, Type[BaseAttributes]]]):
        self.schemas_map = schemas_map or SCHEMAS_MAP
    
    def _get_schema_class(self, item_type: str) -> Type[BaseAttributes]:
        schema_cls = self.schemas_map.get(item_type)
        if not schema_cls:
            raise ValueError(f"Unsupported item type: {item_type}")
        return schema_cls

    def _validate_attributes(self, item_type: str, attributes: dict) -> dict:
        schema_cls = self._get_schema_class(item_type)
        try:
            validated = schema_cls(**attributes)
            return validated.dict()

        except ValidationError as _ex:
            raise ValueError(f'Invalid attributes for {item_type}: {_ex.errors()}')
        

    async def create(self, name: str, item_type: ItemTypeEnum, item_rarity: ItemRarityEnum, attributes: dict):
        valid_attrs = self._validate_attributes(item_type, attributes)
        
        item = await Item.get_or_create(name=name, rarity=item_rarity, type=item_type, attributes=valid_attrs)
        return item

    async def get_by_id(self, item_id: int) -> Item:
        item = await Item.get_or_none(id=item_id)
        return item

    async def get_by_name(self, item_name: str) -> Optional[Dict[Item]]:
        items = await Item.get(name=item_name)
        return items

    async def update(self, item_id: str, **updates: any) -> Item:
        item = await self.get_item(item_id)

        if "attributes" in updates:
            item.attributes = self._validate_attributes(item.type, updates["attributes"])

        if "name" in updates:
            item.name = updates["name"]

        if "rarity" in updates:
            item.rarity = updates["rarity"]

        await item.save()
        return item
    
    async def delete(self, item_id):
        item = await self.get_by_id(item_id)
        await item.delete()