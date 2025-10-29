from typing import Optional, List
from tortoise.exceptions import DoesNotExist, IntegrityError
from bot.db.models import Inventory, User, Item
from bot.services.item import ItemService


class InventoryService():
    def __init__(self) -> None:
        self.item_service = ItemService()
    

    async def add(self, user: User, item: Item, quantity: int = 1, auto_create: bool = True) -> Inventory:
        try:
            inv = await Inventory.get(user=user, item=item)
            inv.quantity += quantity
            await inv.save()
            return inv

        except DoesNotExist:
            if not auto_create:
                raise ValueError("Item not found in inventory and auto_create=False")
            
        inv = await Inventory.create(user=user, item=item, quantity=quantity)
        return inv

    async def remove(self, user: User, item: Item, quantity: int = 1) -> Inventory:
        inv = await Inventory.get_or_none(user=user, item=item)
        if not inv:
            raise ValueError("Item not found in inventory")
        
        if inv.quantity < quantity:
            raise ValueError("Not enough items to remove")

        inv.quantity -= quantity

        if inv.quantity == 0:
            await inv.delete()
        else:
            await inv.save()

    async def get(self, user: User) -> List[Inventory]:
        inv = await Inventory.filter(user=user).prefetch_related('item')
        return inv
    
    async def clear(self, user: User) -> None:
        await Inventory.filter(user=user).delete()

    async def equip_item(self, user: User, item: Item) -> Inventory:
        inv = await Inventory.get_or_none(user=user, item=item)
        if not inv:
            raise ValueError("Item not found in inventory")

        inv.equipped = True
        await inv.save()

        return inv
    
    async def unequip_item(self, user: User, item: Item) -> Inventory:
        inv = await Inventory.get_or_none(user=user, item=item)
        if not inv:
            raise ValueError("Item not found in inventory")

        inv.equipped = False
        await inv.save()
        return inv
