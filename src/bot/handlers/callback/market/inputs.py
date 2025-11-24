from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .deps import market_router
from .filters import set_filters
from .menu import send_market_menu
from .state import MarketFilterState


@market_router.callback_query(F.data == "market_search")
async def callback_market_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MarketFilterState.waiting_for_search)
    await callback.message.answer("Введите название предмета для поиска или '-' чтобы сбросить.")
    await callback.answer()


@market_router.message(MarketFilterState.waiting_for_search)
async def market_search_input(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    value = "" if text == "-" else text
    filters = await set_filters(state, search=value)
    await state.set_state(None)
    await message.answer("Поиск обновлён.")
    await send_market_menu(message, filters)


@market_router.callback_query(F.data == "market_set_min_price")
async def callback_market_set_min_price(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MarketFilterState.waiting_for_min_price)
    await callback.message.answer("Введите минимальную цену (число) или '-' чтобы очистить.")
    await callback.answer()


@market_router.message(MarketFilterState.waiting_for_min_price)
async def market_min_price_input(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "-":
        filters = await set_filters(state, min_price=None)
    elif text.isdigit():
        filters = await set_filters(state, min_price=int(text))
    else:
        await message.answer("Введите положительное число или '-' для сброса.")
        return

    await state.set_state(None)
    await message.answer("Минимальная цена обновлена.")
    await send_market_menu(message, filters)


@market_router.callback_query(F.data == "market_set_max_price")
async def callback_market_set_max_price(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MarketFilterState.waiting_for_max_price)
    await callback.message.answer("Введите максимальную цену (число) или '-' чтобы очистить.")
    await callback.answer()


@market_router.message(MarketFilterState.waiting_for_max_price)
async def market_max_price_input(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "-":
        filters = await set_filters(state, max_price=None)
    elif text.isdigit():
        filters = await set_filters(state, max_price=int(text))
    else:
        await message.answer("Введите положительное число или '-' для сброса.")
        return

    await state.set_state(None)
    await message.answer("Максимальная цена обновлена.")
    await send_market_menu(message, filters)

