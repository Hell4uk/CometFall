import re

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ....keyboards.inlines.inventory import inventory_item_view_keyboard
from .deps import inventory_router, inv_service, user_service
from .helpers import format_item_detail_text, item_type_slug


@inventory_router.callback_query(F.data.regexp(r"inv_view_(\d+)"))
async def callback_view_inventory_item(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    match = re.match(r"inv_view_(\d+)", callback.data)
    if not match:
        await callback.answer()
        return

    inventory_item_id = int(match.group(1))
    user = await user_service.get_by_telegram_id(callback.from_user.id)
    inv_item = await inv_service.get_inventory_item(user, inventory_item_id)

    if not inv_item:
        await callback.answer("Предмет не найден.", show_alert=True)
        return

    item_slug = item_type_slug(inv_item.item.type)
    await callback.message.edit_text(
        text=format_item_detail_text(inv_item),
        reply_markup=inventory_item_view_keyboard(inv_item.id, item_slug),
    )
    await callback.answer()

