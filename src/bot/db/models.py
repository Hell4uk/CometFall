from tortoise import fields
from tortoise.models import Model
from enum import Enum

class ItemTypeEnum(str, Enum):
    WEAPON = 'weapon'
    ARMOR = 'armor'

class ItemRarityEnum(str, Enum):
    COMMON = 'common'


class Users(Model):
    id = fields.BigIntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)

    username = fields.CharField(max_length=255, null=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'users'
        ordering = ['id', 'username']

    def __str__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} ({self.username})>"

class Items(Model):
    id = fields.BigIntField(pk=True)

    name = fields.CharField(max_length=225, null=False)
    description = fields.TextField(max_length=512, null=True)
    type = fields.CharEnumField(ItemTypeEnum)
    attributes = fields.JSONField(default=dict)
    rarity = fields.CharEnumField(ItemRarityEnum, default=ItemRarityEnum.COMMON)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'items'
        ordering = ['id', 'name']

    def __str__(self) -> str:
        return f"<Item id={self.id} ({self.name})>"

class InventoryItems(Model):
    id = fields.BigIntField(pk=True)

    user = fields.ForeignKeyField('models.Users', related_name="inventory_items")
    item = fields.ForeignKeyField('models.Items', related_name='instances')
    quantity = fields.IntField(default=1)
    equipped = fields.BooleanField(default=True)
    
    acquired_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'inventory_items'
        unique_together = ('user', 'item')

    def __str__(self) -> str:
        return f"<Item id={self.id} x{self.quantity}>"

class Enemies(Model):
    pass