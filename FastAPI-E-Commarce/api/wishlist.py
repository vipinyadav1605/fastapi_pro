from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core.auth import get_current_user
from core.db import get_session
from crud import crud_product, crud_wishlist
from model.models import User, WishlistItem
from schemas import WishlistItemCreate, WishlistPublic

router = APIRouter()


def build_wishlist_response(items: list[WishlistItem]) -> WishlistPublic:
    return WishlistPublic(
        items=[{"id": item.id, "product": item.product} for item in items],
        total_items=len(items),
    )


@router.get("/", response_model=WishlistPublic)
async def get_my_wishlist(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    items = await crud_wishlist.get_user_wishlist(user_id=current_user.id, session=session)
    return build_wishlist_response(items)


@router.post("/items", response_model=WishlistPublic, status_code=status.HTTP_201_CREATED)
async def add_item_to_wishlist(
    item_data: WishlistItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    product = await crud_product.get_product_by_id(product_id=item_data.product_id, session=session)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found.")

    await crud_wishlist.add_wishlist_item(
        user_id=current_user.id,
        product_id=item_data.product_id,
        session=session,
    )
    items = await crud_wishlist.get_user_wishlist(user_id=current_user.id, session=session)
    return build_wishlist_response(items)


@router.delete("/items/{product_id}", response_model=WishlistPublic)
async def remove_item_from_wishlist(
    product_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    removed = await crud_wishlist.remove_wishlist_item(
        user_id=current_user.id,
        product_id=product_id,
        session=session,
    )
    if not removed:
        raise HTTPException(status_code=404, detail="Wishlist item not found.")

    items = await crud_wishlist.get_user_wishlist(user_id=current_user.id, session=session)
    return build_wishlist_response(items)
