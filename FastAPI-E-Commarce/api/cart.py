from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core.auth import get_current_user
from core.db import get_session
from crud import crud_cart, crud_product
from model.models import CartItem, User
from schemas import CartItemCreate, CartItemUpdate, CartPublic

router = APIRouter()


def build_cart_response(cart_items: list[CartItem]) -> CartPublic:
    items = []
    total_items = 0
    total_amount = 0.0

    for item in cart_items:
        line_total = round(item.quantity * item.product.price, 2)
        total_items += item.quantity
        total_amount += line_total
        items.append(
            {
                "id": item.id,
                "quantity": item.quantity,
                "product": item.product,
                "line_total": line_total,
            }
        )

    return CartPublic(
        items=items,
        total_items=total_items,
        total_amount=round(total_amount, 2),
    )


@router.get("/", response_model=CartPublic)
async def get_my_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    cart_items = await crud_cart.get_user_cart_items(user_id=current_user.id, session=session)
    return build_cart_response(cart_items)


@router.post("/items", response_model=CartPublic, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    item_data: CartItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    if item_data.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1.")

    product = await crud_product.get_product_by_id(product_id=item_data.product_id, session=session)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    try:
        await crud_cart.add_or_update_cart_item(
            user_id=current_user.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    cart_items = await crud_cart.get_user_cart_items(user_id=current_user.id, session=session)
    return build_cart_response(cart_items)


@router.patch("/items/{product_id}", response_model=CartPublic)
async def update_cart_item(
    product_id: int,
    item_data: CartItemUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    if item_data.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1.")

    try:
        cart_item = await crud_cart.set_cart_item_quantity(
            user_id=current_user.id,
            product_id=product_id,
            quantity=item_data.quantity,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found.")

    cart_items = await crud_cart.get_user_cart_items(user_id=current_user.id, session=session)
    return build_cart_response(cart_items)


@router.delete("/items/{product_id}", response_model=CartPublic)
async def remove_item_from_cart(
    product_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    removed = await crud_cart.remove_cart_item(
        user_id=current_user.id,
        product_id=product_id,
        session=session,
    )
    if not removed:
        raise HTTPException(status_code=404, detail="Cart item not found.")

    cart_items = await crud_cart.get_user_cart_items(user_id=current_user.id, session=session)
    return build_cart_response(cart_items)


@router.delete("/", response_model=CartPublic)
async def clear_my_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    await crud_cart.clear_cart(user_id=current_user.id, session=session)
    return CartPublic()
