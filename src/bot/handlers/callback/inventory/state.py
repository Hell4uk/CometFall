from aiogram.fsm.state import State, StatesGroup

from ....db.models import ItemRarityEnum

RARITY_ORDER = {
    ItemRarityEnum.LEGENDARY: 0,
    ItemRarityEnum.EPIC: 1,
    ItemRarityEnum.RARE: 2,
    ItemRarityEnum.COMMON: 3,
}


class SellItemState(StatesGroup):
    waiting_for_price = State()
    waiting_for_confirmation = State()

