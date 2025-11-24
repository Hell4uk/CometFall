from tortoise import fields
from tortoise.models import Model
from enum import Enum

class ItemTypeEnum(int, Enum):
    WEAPON = 1
    ARMOR = 2

class ItemRarityEnum(int, Enum):
    COMMON = 1
    RARE = 2
    EPIC = 3
    LEGENDARY = 4
    
class EnemyTypeEnum(int, Enum):
    COMMON = 1
    ELITE = 2
    BOSS = 3

# TODO : Сделать модель для локаций, продаваемых предметов на рынке
class Users(Model):
    id = fields.BigIntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)

    username = fields.CharField(max_length=255, null=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)

    coins = fields.IntField(default=100)
    exp = fields.IntField(default=0)
    lvl = fields.IntField(default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'users'
        ordering = ['id', 'username']

    def __str__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} ({self.username})>"

class Items(Model):
    id = fields.BigIntField(pk=True)

    name = fields.CharField(max_length=225, null=False)
    description = fields.TextField(max_length=512, null=True)
    type = fields.IntEnumField(ItemTypeEnum)
    attributes = fields.JSONField(default=dict)
    rarity = fields.IntEnumField(ItemRarityEnum, default=ItemRarityEnum.COMMON)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

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
    equipped = fields.BooleanField(default=False)
    
    acquired_at = fields.DatetimeField(auto_now_add=True)
    class Meta:
        table = 'inventory_items'
        unique_together = ('user', 'item')

    def __str__(self) -> str:
        return f"<Item id={self.id} x{self.quantity}>"

class Enemies(Model):
    id = fields.BigIntField(pk=True)

    name = fields.CharField(max_length=255, null=False)
    description = fields.TextField(max_length=512, null=True, default='')

    type = fields.IntEnumField(EnemyTypeEnum, default=EnemyTypeEnum.COMMON)

    health_multiplier = fields.FloatField(default=0.5)
    damage_multiplier = fields.FloatField(default=0.5)

    coin_reward_multiplier = fields.FloatField(default=0.5)
    exp_reward_multiplier = fields.FloatField(default=0.5)
    
    drop_chance = fields.FloatField(default=25.0, ge=0.0, le=100.0)
    drop_items = fields.ManyToManyField(
        "models.Items",
        related_name='enemy_drops',
        through='enemy_drop',
        backward_key='enemy_id'
    )

    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'enemies'
        ordering = ["name"]

class Locations(Model):
    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    level_required = fields.IntField(default=1)
    enemies = fields.ManyToManyField("models.Enemies", related_name="locations")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
class MarketItem(Model):
    id = fields.BigIntField(pk=True)

    item = fields.ForeignKeyField("models.Items")
    seller = fields.ForeignKeyField("models.Users")

    price = fields.IntField()    

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)