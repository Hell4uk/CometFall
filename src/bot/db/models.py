from email.policy import default
from enum import unique
import re
from statistics import quantiles
from tortoise import fields
from tortoise.models import Model
from enum import Enum

class ItemTypeEnum(Enum):
    WEAPON = 'weapon'
    ARMOR = 'armor'

class ItemRarityEnum(Enum):
    COMMON = 'common'


class User(Model):
    id = fields.BigIntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)

    username = fields.CharField(max_length=255, null=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} ({self.username})>"

class Item(Model):
    id = fields.BigIntField(pk=True)

    name = fields.CharField(max_length=225, null=False)
    description = fields.CharField(max_length=512, null=True)
    type = fields.CharEnumField(ItemTypeEnum)
    attributes = fields.JSONField(default=dict)
    rarity = fields.CharEnumField(ItemRarityEnum, default=ItemRarityEnum.COMMON)

    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"<Item id={self.id} ({self.name})>"

class InventoryItem(Model):
    id = fields.BigIntField(pk=True)

    user = fields.ForeignKeyField('models.User', related_name="inventory_items")
    item = fields.ForeignKeyField('models.item', related_name='instances')
    quantity = fields.IntField(default=1)
    equipped = fields.BooleanField(default=True)
    
    acquired_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"<Item id={self.id} x{self.quantity}>"
