from typing import Optional, List
from tortoise.exceptions import DoesNotExist
from ...bot.db.models import InventoryItems, Users, Items, ItemTypeEnum
from ...bot.services.item import ItemService, SCHEMAS_MAP

# TODO: Сделать методы для получения используемых предметов, сделать копии методов для получения (dict), также улучшить все существующие методы
# TODO: Сделать систему при который можно одеть только один предмет каждого типа
class InventoryService():
    def __init__(self) -> None:
        self.item_service = ItemService(SCHEMAS_MAP)
    
    # ? --- CRUD методы ---
    async def add(self, user: Users, item: Items, quantity: int = 1, auto_create: bool = True) -> InventoryItems:
        try:
            inv = await InventoryItems.get(user=user, item=item)
            inv.quantity += quantity
            await inv.save()
            return inv

        except DoesNotExist:
            if not auto_create:
                raise ValueError("Item not found in inventory and auto_create=False")
            
        inv = await InventoryItems.create(user=user, item=item, quantity=quantity)
        return inv

    async def remove(self, user: Users, item: Items, quantity: int = 1) -> None:
        inv = await InventoryItems.get_or_none(user=user, item=item)
        if not inv:
            raise ValueError("Item not found in inventory")
        
        if inv.quantity < quantity:
            raise ValueError("Not enough items to remove")

        inv.quantity -= quantity

        if inv.quantity == 0:
            await inv.delete()
        else:
            await inv.save()

    async def get(self, user: Users) -> Optional[List[InventoryItems]]:
        inv = await InventoryItems.filter(user=user).prefetch_related('item')
        return inv

    async def get_inventory_dict(self, user: Users) -> dict:
        inv = await InventoryItems.filter(user=user).prefetch_related('item')
        return {str(i.item.name): i.quantity for i in inv}

    
    async def clear(self, user: Users) -> None:
        await InventoryItems.filter(user=user).delete()

    async def equip_item(self, user: Users, item: Items) -> InventoryItems:
        inv = await InventoryItems.get_or_none(user=user, item=item)
        if not inv:
            raise ValueError("Item not found in inventory")

        if inv.equipped:
            raise ValueError("Item is already equipped")

        equipped_same_type = await InventoryItems.filter(
            user=user,
            equipped=True,
            item__type=item.type
        ).first()

        if equipped_same_type:
            raise ValueError(f"You already have an equipped item of type {item.type}")

        inv.equipped = True
        await inv.save()
        return inv

    async def unequip_item(self, user: Users, item: Items) -> None:
        inv = await InventoryItems.get_or_none(user=user, item=item)
        if not inv:
            raise ValueError("Item not found in inventory")

        if not inv.equipped:
            raise ValueError("Item is not equipped")

        inv.equipped = False
        await inv.save()

    async def get_equipped_item(self, user: Users, item_type: ItemTypeEnum) -> Optional[InventoryItems]:
        return await InventoryItems.filter(
            user=user,
            equipped=True,
            item__type=item_type
        ).prefetch_related("item").first()

    async def get_inventory_item(self, user: Users, inventory_item_id: int) -> Optional[InventoryItems]:
        return await InventoryItems.filter(
            user=user,
            id=inventory_item_id
        ).prefetch_related("item").first()