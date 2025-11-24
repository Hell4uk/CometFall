from typing import Dict, List, Optional

from tortoise.functions import Min
from tortoise.transactions import in_transaction

from ...bot.db.models import Items, MarketItem, Users, ItemTypeEnum, ItemRarityEnum
from .inventory import InventoryService


class MarketService:
    def __init__(self, inventory_service: Optional[InventoryService] = None) -> None:
        self.inventory_service = inventory_service or InventoryService()

    async def get_min_price(self, item: Items) -> Optional[int]:
        record = await MarketItem.filter(item=item).order_by("price").first()
        return record.price if record else None

    async def get_min_price_map(self, item_ids: List[int]) -> Dict[int, int]:
        if not item_ids:
            return {}

        rows = await MarketItem.filter(item_id__in=item_ids)\
            .annotate(min_price=Min("price"))\
            .group_by("item_id")\
            .values("item_id", "min_price")

        return {row["item_id"]: row["min_price"] for row in rows}

    async def list_item(self, item: Items, seller: Users, price: int) -> MarketItem:
        return await MarketItem.create(item=item, seller=seller, price=price)

    async def get_items(
        self,
        item_type: ItemTypeEnum,
        rarity: Optional[ItemRarityEnum] = None,
        search: Optional[str] = None
    ) -> List[Items]:
        qs = Items.filter(type=item_type)
        if rarity:
            qs = qs.filter(rarity=rarity)
        if search:
            qs = qs.filter(name__icontains=search)

        return await qs.order_by("rarity", "name").all()

    async def get_player_listings(self, user: Users) -> List[MarketItem]:
        return await MarketItem.filter(seller=user).prefetch_related("item").order_by("price", "id")

    async def remove_listing(self, listing_id: int, user: Users) -> bool:
        listing = await MarketItem.get_or_none(id=listing_id, seller=user)
        if not listing:
            return False
        await listing.delete()
        return True

    async def buy_cheapest_listing(self, item: Items, buyer: Users) -> int:
        listing = await MarketItem.filter(item=item).select_related("seller", "item").order_by("price", "id").first()
        if not listing:
            raise ValueError("Нет доступных лотов.")

        await buyer.refresh_from_db()
        if listing.seller_id == buyer.id:
            raise ValueError("Нельзя купить собственный лот.")

        if buyer.coins < listing.price:
            raise ValueError("Недостаточно монет.")

        seller = listing.seller
        await seller.refresh_from_db()

        async with in_transaction():
            buyer.coins -= listing.price
            await buyer.save()

            seller.coins += listing.price
            await seller.save()

            await self.inventory_service.add(buyer, listing.item)
            await listing.delete()

        return listing.price

