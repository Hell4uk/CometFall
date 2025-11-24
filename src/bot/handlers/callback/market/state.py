from aiogram.fsm.state import State, StatesGroup

ITEMS_PER_PAGE = 5
LISTINGS_PER_PAGE = 5

RARITY_SEQUENCE = ["all", "common", "rare", "epic", "legendary"]
RARITY_LABELS = {
    "all": "все",
    "common": "обычн.",
    "rare": "редк.",
    "epic": "эпич.",
    "legendary": "легенд.",
}


class MarketFilterState(StatesGroup):
    waiting_for_search = State()
    waiting_for_min_price = State()
    waiting_for_max_price = State()

