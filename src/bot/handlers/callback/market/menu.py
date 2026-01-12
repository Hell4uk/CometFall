from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ....keyboards.inlines.market import market_main_keyboard
from .deps import market_router
from .filters import format_filters_text, get_filters, reset_filters, set_filters
from .helpers import next_rarity_slug
from .state import RARITY_LABELS


async def send_market_menu(message: Message, filters: dict) -> None:
    await message.answer(
        text=(
            "🏪 Рынок Кометопада\n\n"
            "Настройки фильтров:\n"
            f"{format_filters_text(filters)}\n\n"
            "Выберите категорию или обновите фильтры:"
        ),
        reply_markup=market_main_keyboard(RARITY_LABELS.get(filters.get("rarity"), "все")),
    )


async def edit_market_menu(callback: CallbackQuery, filters: dict) -> None:
    await callback.message.edit_text(
        text=(
            f"{callback.from_user.first_name}, добро пожаловать на рынок.\n\n"
            "Текущие фильтры:\n"
            f"{format_filters_text(filters)}\n\n"
            "Выберите действие:"
        ),
        reply_markup=market_main_keyboard(RARITY_LABELS.get(filters.get("rarity"), "все")),
    )


@market_router.callback_query(F.data == "market")
async def callback_market_entry(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    filters = await reset_filters(state)
    await edit_market_menu(callback, filters)
    await callback.answer()


@market_router.callback_query(F.data == "market_menu")
async def callback_market_menu(callback: CallbackQuery, state: FSMContext):
    filters = await get_filters(state)
    await edit_market_menu(callback, filters)
    await callback.answer()


@market_router.callback_query(F.data == "market_cycle_rarity")
async def callback_market_cycle_rarity(callback: CallbackQuery, state: FSMContext):
    filters = await get_filters(state)
    next_slug = next_rarity_slug(filters.get("rarity", "all"))
    filters = await set_filters(state, rarity=next_slug)
    await edit_market_menu(callback, filters)
    await callback.answer("Редкость обновлена.")


@market_router.callback_query(F.data == "market_filters_reset")
async def callback_market_filters_reset(callback: CallbackQuery, state: FSMContext):
    filters = await reset_filters(state)
    await edit_market_menu(callback, filters)
    await callback.answer("Фильтры сброшены.")

