from typing import Dict, Optional, Union

from aiogram.fsm.context import FSMContext

from .state import RARITY_LABELS

FilterValue = Optional[Union[str, int]]

DEFAULT_FILTERS: Dict[str, FilterValue] = {
    "search": "",
    "rarity": "all",
    "min_price": 0,
    "max_price": None,
}


def format_filters_text(filters: Dict[str, FilterValue]) -> str:
    search = filters.get("search") or "—"
    rarity = RARITY_LABELS.get(filters.get("rarity"), "все")

    min_price = filters.get("min_price")
    max_price = filters.get("max_price")
    if min_price is None and max_price is None:
        price_text = "—"
    else:
        min_part = str(min_price) if min_price is not None else "0"
        max_part = str(max_price) if max_price is not None else "∞"
        price_text = f"{min_part}-{max_part}"

    return f"Поиск: {search}\nРедкость: {rarity}\nЦена: {price_text}"


async def get_filters(state: FSMContext) -> Dict[str, FilterValue]:
    data = await state.get_data()
    filters = data.get("market_filters")
    if not filters:
        filters = DEFAULT_FILTERS.copy()
        await state.update_data(market_filters=filters)
    return filters


async def set_filters(state: FSMContext, **updates: FilterValue) -> Dict[str, FilterValue]:
    filters = await get_filters(state)
    for key, value in updates.items():
        if key in filters:
            filters[key] = value
    await state.update_data(market_filters=filters)
    return filters


async def reset_filters(state: FSMContext) -> Dict[str, FilterValue]:
    filters = DEFAULT_FILTERS.copy()
    await state.update_data(market_filters=filters)
    return filters

