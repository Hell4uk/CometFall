"""Сервис управления инвентарём игрока.

Обрабатывает добавление, удаление, экипирование/разоружение предметов.
Гарантирует, что одновременно экипирован только один предмет каждого типа.
"""
from typing import Optional, List
from tortoise.exceptions import DoesNotExist
from ...bot.db.models import InventoryItems, Users, Items, ItemTypeEnum
from ...bot.services.item import ItemService, SCHEMAS_MAP

# TODO: Сделать методы для получения используемых предметов, сделать копии методов для получения (dict), также улучшить все существующие методы
# TODO: Сделать систему при который можно одеть только один предмет каждого типа
class InventoryService():
    """Сервис для управления инвентарём игрока.
    
    Функциональность:
    - Добавление/удаление предметов с проверкой количества
    - Экипирование/разоружение с гарантией одного предмета на тип
    - Получение списка предметов и словаря инвентаря
    - Поиск экипированного предмета по типу
    """
    def __init__(self) -> None:
        self.item_service = ItemService(SCHEMAS_MAP)
    
    # ? --- CRUD методы ---
    async def add(self, user: Users, item: Items, quantity: int = 1, auto_create: bool = True) -> InventoryItems:
        """Добавляет предмет в инвентарь игрока или увеличивает количество.
        
        Если предмет уже в инвентаре → увеличивает quantity.
        Если предмета нет → создаёт новую запись (если auto_create=True).
        
        Args:
            user (Users): игрок, владелец инвентаря
            item (Items): предмет для добавления
            quantity (int): количество добавляемых копий (по умолчанию 1)
            auto_create (bool): создать новую запись, если предмета нет
            
        Returns:
            InventoryItems: обновленная или новая запись инвентаря
            
        Raises:
            ValueError: если предмета нет и auto_create=False
        """
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
        """Удаляет предмет из инвентаря игрока.
        
        Уменьшает количество на quantity. Если quantity = 0 → удаляет запись полностью.
        
        Args:
            user (Users): владелец инвентаря
            item (Items): предмет для удаления
            quantity (int): количество копий для удаления
            
        Raises:
            ValueError: если предмета нет или недостаточно копий
        """
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
        """Экипирует предмет (отмечает его как используемый).
        
        Проверяет:
        1. Предмет есть в инвентаре
        2. Предмет не экипирован (уникальность: один на тип)
        3. Нет другого экипированного предмета того же типа
        
        Если проверки пройдены → устанавливает equipped=True.
        
        Args:
            user (Users): владелец инвентаря
            item (Items): предмет для экипирования
            
        Returns:
            InventoryItems: экипированная запись инвентаря
            
        Raises:
            ValueError: если предмета нет, уже экипирован или занято место типа
        """
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
        """Снимает экипировку с предмета.
        
        Проверяет:
        1. Предмет есть в инвентаре
        2. Предмет экипирован
        
        Если проверки пройдены → устанавливает equipped=False.
        
        Args:
            user (Users): владелец инвентаря
            item (Items): предмет для разоружения
            
        Raises:
            ValueError: если предмета нет или он не экипирован
        """
        inv = await InventoryItems.get_or_none(user=user, item=item)
        if not inv:
            raise ValueError("Item not found in inventory")

        if not inv.equipped:
            raise ValueError("Item is not equipped")

        inv.equipped = False
        await inv.save()

    async def get_equipped_item(self, user: Users, item_type: ItemTypeEnum) -> Optional[InventoryItems]:
        """Получает экипированный предмет заданного типа.
        
        Args:
            user (Users): владелец инвентаря
            item_type (ItemTypeEnum): тип предмета (WEAPON, ARMOR и т.д.)
            
        Returns:
            Optional[InventoryItems]: запись инвентаря с экипированным предметом или None
        """
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