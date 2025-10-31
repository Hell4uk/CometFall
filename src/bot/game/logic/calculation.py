from typing import Dict
from bot.db.models import InventoryItems, ItemRarityEnum, ItemTypeEnum, Users
from bot.services.inventory import InventoryService
from bot.db.schemas.items import WeaponAttributes, ArmorAttributes

# TODO: Сделать классы для обработки общего урона-брони для используемых предметов