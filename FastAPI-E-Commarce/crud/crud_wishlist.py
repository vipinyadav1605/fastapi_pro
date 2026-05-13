from typing import List

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from model.models import Product, Review, WishlistItem


async def get_user_wishlist(user_id: int, session: AsyncSession) -> List[WishlistItem]:
    statement = (
        select(WishlistItem)
        .where(WishlistItem.user_id == user_id)
        .options(selectinload(WishlistItem.product).selectinload(Product.category))
        .options(selectinload(WishlistItem.product).selectinload(Product.reviews).selectinload(Review.user))
    )
    result = await session.exec(statement)
    return result.all()


async def get_wishlist_item(user_id: int, product_id: int, session: AsyncSession) -> WishlistItem | None:
    statement = select(WishlistItem).where(
        WishlistItem.user_id == user_id,
        WishlistItem.product_id == product_id,
    )
    result = await session.exec(statement)
    return result.one_or_none()


async def add_wishlist_item(user_id: int, product_id: int, session: AsyncSession) -> WishlistItem:
    existing_item = await get_wishlist_item(user_id=user_id, product_id=product_id, session=session)
    if existing_item:
        return existing_item

    item = WishlistItem(user_id=user_id, product_id=product_id)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def remove_wishlist_item(user_id: int, product_id: int, session: AsyncSession) -> bool:
    item = await get_wishlist_item(user_id=user_id, product_id=product_id, session=session)
    if not item:
        return False

    await session.delete(item)
    await session.commit()
    return True
