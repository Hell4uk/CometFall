from enum import unique
from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.BigIntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)

    username = fields.CharField(max_length=255, null=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} ({self.username})>"