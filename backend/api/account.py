from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core.auth import get_current_user
from core.db import get_session
from crud import crud_account
from model.models import User
from schemas import (
    AddressCreate,
    AddressPublic,
    ProfilePublic,
    SavedPaymentMethodCreate,
    SavedPaymentMethodPublic,
)

router = APIRouter()


@router.get("/profile", response_model=ProfilePublic)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    profile = await crud_account.get_profile(user_id=current_user.id, session=session)
    return {
        "user": current_user,
        "addresses": profile.addresses if profile else [],
        "saved_payment_methods": profile.saved_payment_methods if profile else [],
        "notifications": profile.notifications if profile else [],
    }


@router.post("/addresses", response_model=AddressPublic, status_code=status.HTTP_201_CREATED)
async def add_address(
    address_data: AddressCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    return await crud_account.create_address(
        user_id=current_user.id,
        data=address_data,
        session=session,
    )


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    deleted = await crud_account.delete_address(
        user_id=current_user.id,
        address_id=address_id,
        session=session,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Address not found.")


@router.post("/payment-methods", response_model=SavedPaymentMethodPublic, status_code=status.HTTP_201_CREATED)
async def add_payment_method(
    method_data: SavedPaymentMethodCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    return await crud_account.create_payment_method(
        user_id=current_user.id,
        data=method_data,
        session=session,
    )


@router.delete("/payment-methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_method(
    method_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    deleted = await crud_account.delete_payment_method(
        user_id=current_user.id,
        method_id=method_id,
        session=session,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment method not found.")
