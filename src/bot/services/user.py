from ..db.models import Users, ItemRarityEnum, Items
from tortoise.exceptions import DoesNotExist
from .inventory import InventoryService
from .item import ItemService, SCHEMAS_MAP

# TODO : Создать UserService, сделать выдачу стартового набор, сделать формулу для расчета EXP-LVL, сделать метод на добавление XP
class UserService():
    def __init__(self) -> None:
        self.inventory_service = InventoryService()
        self.item_service = ItemService(SCHEMAS_MAP)

    async def get_by_telegram_id(self, id: int) -> Users:
        user = await Users.get_or_none(telegram_id=id)
        return user
    
    async def create(self, telegram_id: int, username: str = '', first_name: str = '', last_name: str = '', coins: int = 150, exp: int = 0, lvl: int = 0) -> Users:
        user, created = await Users.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "coins": coins,
                "exp": exp,
                "lvl": lvl,
            }
        )

        if created:
            await self.inventory_service.add(user, await self.item_service.get_by_id(1))  
            await self.inventory_service.add(user, await self.item_service.get_by_id(2))
            await self.inventory_service.equip_item(user, await self.item_service.get_by_id(1))
            await self.inventory_service.equip_item(user, await self.item_service.get_by_id(2))

        return user
    
    async def add_exp(self, user: Users, amount: int):
        user.exp += amount

        old_lvl = user.lvl
        required_exp = 65 * (user.lvl + 1)
        while user.exp >= required_exp:
            user.lvl += 1
            user.exp -= required_exp
            required_exp = 65 * (user.lvl + 1)

        return {"exp": user.exp, "lvl": user.lvl}
    