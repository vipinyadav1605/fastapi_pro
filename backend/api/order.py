from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.auth import get_current_user, is_admin
from core.db import get_session
from crud import crud_account, crud_cart, crud_order
from model.models import Coupon, User
from schemas import CheckoutCreate, CheckoutPreview, OrderPublic, OrderStatusUpdate

router = APIRouter()

PAYMENT_METHODS = {"cash_on_delivery", "card", "bank_transfer"}
ORDER_STATUSES = {"placed", "paid", "processing", "shipped", "delivered", "cancelled"}


async def calculate_checkout_totals(
    *,
    cart_items,
    coupon_code: str | None,
    session: AsyncSession,
) -> dict[str, float]:
    subtotal = 0.0
    for item in cart_items:
        if not item.product.is_active or item.product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"{item.product.name} is unavailable or does not have enough stock.",
            )
        subtotal += round(item.quantity * item.product.price, 2)

    discount_amount = 0.0
    if coupon_code:
        result = await session.exec(select(Coupon).where(Coupon.code == coupon_code.upper()))
        coupon = result.one_or_none()
        if not coupon or not coupon.is_active:
            raise HTTPException(status_code=400, detail="Invalid coupon code.")
        if subtotal < coupon.min_order_amount:
            raise HTTPException(status_code=400, detail="Order does not meet coupon minimum amount.")
        discount_amount = round(subtotal * (coupon.discount_percent / 100), 2)

    tax_amount = round((subtotal - discount_amount) * 0.08, 2)
    shipping_amount = 0 if subtotal >= 100 else 8
    total_amount = round(subtotal - discount_amount + tax_amount + shipping_amount, 2)
    return {
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "tax_amount": tax_amount,
        "shipping_amount": shipping_amount,
        "total_amount": total_amount,
    }


@router.post("/checkout/preview", response_model=CheckoutPreview)
async def preview_checkout(
    checkout_data: CheckoutCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    cart_items = await crud_cart.get_user_cart_items(user_id=current_user.id, session=session)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Your cart is empty.")
    return await calculate_checkout_totals(
        cart_items=cart_items,
        coupon_code=checkout_data.coupon_code,
        session=session,
    )


@router.post("/checkout", response_model=OrderPublic, status_code=status.HTTP_201_CREATED)
async def checkout_cart(
    checkout_data: CheckoutCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    if checkout_data.payment_method not in PAYMENT_METHODS:
        raise HTTPException(status_code=400, detail="Unsupported payment method.")

    if checkout_data.payment_method == "card" and not checkout_data.card_last4:
        raise HTTPException(status_code=400, detail="Card last four digits are required.")

    cart_items = await crud_cart.get_user_cart_items(user_id=current_user.id, session=session)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Your cart is empty.")

    order_items = []
    for item in cart_items:
        line_total = round(item.quantity * item.product.price, 2)
        order_items.append(
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.product.price,
                "line_total": line_total,
            }
        )

    totals = await calculate_checkout_totals(
        cart_items=cart_items,
        coupon_code=checkout_data.coupon_code,
        session=session,
    )

    payment_status = "pending" if checkout_data.payment_method == "cash_on_delivery" else "paid"
    order_status = "placed" if payment_status == "pending" else "paid"

    order = await crud_order.create_order(
        user_id=current_user.id,
        shipping_address=checkout_data.shipping_address,
        payment_method=checkout_data.payment_method,
        payment_status=payment_status,
        items=order_items,
        total_amount=totals["total_amount"],
        session=session,
    )
    order.status = order_status
    session.add(order)
    for item in cart_items:
        item.product.stock -= item.quantity
        session.add(item.product)
    await session.commit()

    await crud_cart.clear_cart(user_id=current_user.id, session=session)
    await crud_account.create_notification(
        user_id=current_user.id,
        title="Order placed",
        message=f"Your order #{order.id} was placed successfully.",
        session=session,
    )
    return await crud_order.get_order_by_id(order_id=order.id, user_id=current_user.id, session=session)


@router.get("/my", response_model=List[OrderPublic])
async def get_my_orders(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    return await crud_order.get_user_orders(user_id=current_user.id, session=session)


@router.get("/", response_model=List[OrderPublic], dependencies=[Depends(is_admin())])
async def get_all_orders(session: AsyncSession = Depends(get_session)):
    return await crud_order.get_all_orders(session=session)


@router.get("/{order_id}", response_model=OrderPublic)
async def get_order_details(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    order = await crud_order.get_order_by_id(
        order_id=order_id,
        user_id=None if current_user.role == "admin" else current_user.id,
        session=session,
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


@router.post("/{order_id}/cancel", response_model=OrderPublic)
async def cancel_order(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    order = await crud_order.get_order_by_id(
        order_id=order_id,
        user_id=None if current_user.role == "admin" else current_user.id,
        session=session,
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    try:
        return await crud_order.cancel_order(order=order, session=session)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{order_id}/invoice", response_class=PlainTextResponse)
async def download_invoice(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    order = await crud_order.get_order_by_id(
        order_id=order_id,
        user_id=None if current_user.role == "admin" else current_user.id,
        session=session,
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    lines = [
        "ONLINE STORE INVOICE",
        f"Invoice for order #{order.id}",
        f"Status: {order.status}",
        f"Payment: {order.payment_status} via {order.payment_method}",
        f"Shipping: {order.shipping_address}",
        "",
        "Items:",
    ]
    for item in order.items:
        lines.append(f"- {item.quantity} x {item.product.name} @ ${item.unit_price:.2f} = ${item.line_total:.2f}")
    lines.extend(["", f"Total: ${order.total_amount:.2f}"])
    return "\n".join(lines)


@router.patch("/{order_id}/status", response_model=OrderPublic, dependencies=[Depends(is_admin())])
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    session: AsyncSession = Depends(get_session),
):
    if status_data.status not in ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="Unsupported order status.")

    order = await crud_order.get_order_by_id(order_id=order_id, session=session)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    return await crud_order.update_order_status(
        order=order,
        status=status_data.status,
        session=session,
    )
