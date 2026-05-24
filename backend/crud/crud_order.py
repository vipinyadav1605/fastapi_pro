from typing import List

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from model.models import Order, OrderItem, Product, Review


ORDER_LOAD_OPTIONS = (
    selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.category),
    selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.reviews).selectinload(Review.user),
)


async def create_order(
    *,
    user_id: int,
    shipping_address: str,
    payment_method: str,
    payment_status: str,
    items: list[dict],
    total_amount: float,
    session: AsyncSession,
) -> Order:
    order = Order(
        user_id=user_id,
        shipping_address=shipping_address,
        payment_method=payment_method,
        payment_status=payment_status,
        total_amount=total_amount,
    )
    session.add(order)
    await session.flush()

    for item in items:
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                line_total=item["line_total"],
            )
        )

    await session.commit()
    return await get_order_by_id(order_id=order.id, user_id=user_id, session=session)


async def get_user_orders(user_id: int, session: AsyncSession) -> List[Order]:
    statement = (
        select(Order)
        .where(Order.user_id == user_id)
        .options(*ORDER_LOAD_OPTIONS)
        .order_by(Order.created_at.desc())
    )
    result = await session.exec(statement)
    return result.all()


async def get_all_orders(session: AsyncSession) -> List[Order]:
    statement = select(Order).options(*ORDER_LOAD_OPTIONS).order_by(Order.created_at.desc())
    result = await session.exec(statement)
    return result.all()


async def get_order_by_id(
    order_id: int,
    session: AsyncSession,
    user_id: int | None = None,
) -> Order | None:
    statement = select(Order).where(Order.id == order_id).options(*ORDER_LOAD_OPTIONS)
    if user_id is not None:
        statement = statement.where(Order.user_id == user_id)
    result = await session.exec(statement)
    return result.one_or_none()


async def update_order_status(order: Order, status: str, session: AsyncSession) -> Order:
    order.status = status
    if status in {"paid", "processing", "shipped", "delivered"} and order.payment_method != "cash_on_delivery":
        order.payment_status = "paid"
    if status == "cancelled":
        order.payment_status = "cancelled"

    session.add(order)
    await session.commit()
    return await get_order_by_id(order_id=order.id, session=session)


async def cancel_order(order: Order, session: AsyncSession) -> Order:
    if order.status in {"shipped", "delivered"}:
        raise ValueError("Shipped or delivered orders cannot be cancelled.")
    order.status = "cancelled"
    order.payment_status = "refunded" if order.payment_status == "paid" else "cancelled"
    for item in order.items:
        item.product.stock += item.quantity
        session.add(item.product)
    session.add(order)
    await session.commit()
    return await get_order_by_id(order_id=order.id, session=session)
