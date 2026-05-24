# api/reviews.py
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core.auth import get_current_user
from core.db import get_session
from crud import crud_review, crud_product
from model.models import User
from schemas import ReviewCreate, ReviewPublic

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReviewPublic)
async def create_new_review(
    review_data: ReviewCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new review for a product.
    """
    # Check if the product exists
    product = await crud_product.get_product_by_id(product_id=review_data.product_id, session=session)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {review_data.product_id} not found."
        )
    
    new_review = await crud_review.create_review(
        review_data=review_data, 
        user_id=current_user.id,
        session=session
    )
    return new_review

@router.get("/product/{product_id}", response_model=List[ReviewPublic])
async def get_reviews_by_product(
    product_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Get all reviews for a specific product.
    """
    reviews = await crud_review.get_reviews_for_product(product_id=product_id, session=session)
    return reviews
