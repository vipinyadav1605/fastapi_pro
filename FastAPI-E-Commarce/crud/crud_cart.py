from typing import List

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from model.models import CartItem, Product, Review


async def get_user_cart_items(user_id: int, session: AsyncSession) -> List[CartItem]:
    statement = (
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product).selectinload(Product.category))
        .options(selectinload(CartItem.product).selectinload(Product.reviews).selectinload(Review.user))
    )
    result = await session.exec(statement)
    return result.all()


async def get_cart_item(user_id: int, product_id: int, session: AsyncSession) -> CartItem | None:
    statement = select(CartItem).where(
        CartItem.user_id == user_id,
        CartItem.product_id == product_id,
    )
    result = await session.exec(statement)
    return result.one_or_none()


async def add_or_update_cart_item(
    user_id: int,
    product_id: int,
    quantity: int,
    session: AsyncSession,
) -> CartItem:
    product = await session.get(Product, product_id)
    if not product or not product.is_active or product.stock < quantity:
        raise ValueError("Product is unavailable or does not have enough stock.")

    cart_item = await get_cart_item(user_id=user_id, product_id=product_id, session=session)
    if cart_item:
        if product.stock < cart_item.quantity + quantity:
            raise ValueError("Product does not have enough stock.")
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        session.add(cart_item)

    await session.commit()
    await session.refresh(cart_item)
    return cart_item


async def set_cart_item_quantity(
    user_id: int,
    product_id: int,
    quantity: int,
    session: AsyncSession,
) -> CartItem | None:
    cart_item = await get_cart_item(user_id=user_id, product_id=product_id, session=session)
    if not cart_item:
        return None
    product = await session.get(Product, product_id)
    if not product or product.stock < quantity:
        raise ValueError("Product does not have enough stock.")

    cart_item.quantity = quantity
    session.add(cart_item)
    await session.commit()
    await session.refresh(cart_item)
    return cart_item


async def remove_cart_item(user_id: int, product_id: int, session: AsyncSession) -> bool:
    cart_item = await get_cart_item(user_id=user_id, product_id=product_id, session=session)
    if not cart_item:
        return False

    await session.delete(cart_item)
    await session.commit()
    return True


async def clear_cart(user_id: int, session: AsyncSession) -> None:
    cart_items = await get_user_cart_items(user_id=user_id, session=session)
    for item in cart_items:
        await session.delete(item)
    await session.commit()
