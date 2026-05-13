# api/products.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from core.db import get_session
from crud import crud_product
from schemas import ProductCreate, ProductPublic

from typing import Annotated
from core.auth import get_current_user, is_admin
from model.models import User

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductPublic, dependencies=[Depends(is_admin())])
async def create_new_product(
    product_data: ProductCreate,
    session: AsyncSession = Depends(get_session),

):
    """
    Create a new product.
    """
    new_product = await crud_product.create_product(product_data=product_data, session=session)
    return new_product

@router.get("/", response_model=List[ProductPublic])
async def get_all_products_list(
    session: AsyncSession = Depends(get_session),
    search: str | None = Query(default=None, description="Search product name or description."),
    category_id: int | None = Query(default=None, description="Filter by category id."),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    brand: str | None = Query(default=None),
    availability: str | None = Query(default=None, pattern="^(in_stock|out_of_stock)$"),
    sort_by: str = Query(default="newest", pattern="^(newest|price_asc|price_desc|name|stock)$"),
    include_inactive: bool = Query(default=False),
    *,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get a list of all products.
    """
    products = await crud_product.get_all_products(
        session=session,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        brand=brand,
        availability=availability,
        sort_by=sort_by,
        include_inactive=include_inactive and current_user.role == "admin",
    )
    return products

@router.get( "/paginated" , response_model=List[ProductPublic]) 
async def get_paginated_products (
     skip: int = Query( 0 , ge= 0 , description= "How many items to skip from the beginning." ), 
     limit: int = Query( 10 , ge= 0 , le= 100 , description= "The maximum number of items to return per page." ), 
        session: AsyncSession = Depends(get_session) ):
        """ Get a paginated list of all products. """
        products = await crud_product.get_all_products_paginated(
                skip=skip, limit=limit, session=session)
        return products

@router.get("/{product_id}", response_model=ProductPublic)
async def get_product_details(
    product_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Get details for a specific product by ID.
    """
    product = await crud_product.get_product_by_id(product_id=product_id, session=session)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
    return product


