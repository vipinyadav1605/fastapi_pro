from typing import List
from sqlmodel import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from model.models import Product, ProductImage, Review
from schemas import ProductCreate, ProductUpdate
from sqlalchemy.orm import selectinload

async def create_product(product_data: ProductCreate, session: AsyncSession) -> Product:
    image_urls = product_data.image_urls
    db_product = Product.model_validate(product_data.model_dump(exclude={"image_urls"}))
    session.add(db_product)
    await session.flush()
    for index, image_url in enumerate(image_urls):
        if image_url.strip():
            session.add(
                ProductImage(
                    image_url=image_url.strip(),
                    sort_order=index,
                    product_id=db_product.id,
                )
            )
    await session.commit()
    await session.refresh(db_product)
    exec_query = (select(Product).where(
        Product.id == db_product.id).\
            options(selectinload(Product.reviews).selectinload(Review.user)).\
                options(selectinload(Product.category)).\
                options(selectinload(Product.images))
    )
    egar_load = await session.exec(exec_query)
    return egar_load.one()

async def get_all_products(
    session: AsyncSession,
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    brand: str | None = None,
    availability: str | None = None,
    sort_by: str = "newest",
    include_inactive: bool = False,
) -> List[Product]:
    statement = (
        select(Product)
        .options(selectinload(Product.reviews).selectinload(Review.user))
        .options(selectinload(Product.category))
        .options(selectinload(Product.images))
    )

    if not include_inactive:
        statement = statement.where(Product.is_active == True)
    if search:
        search_term = f"%{search}%"
        statement = statement.where(
            or_(Product.name.ilike(search_term), Product.description.ilike(search_term))
        )
    if category_id:
        statement = statement.where(Product.category_id == category_id)
    if min_price is not None:
        statement = statement.where(Product.price >= min_price)
    if max_price is not None:
        statement = statement.where(Product.price <= max_price)
    if brand:
        statement = statement.where(Product.brand.ilike(f"%{brand}%"))
    if availability == "in_stock":
        statement = statement.where(Product.stock > 0)
    if availability == "out_of_stock":
        statement = statement.where(Product.stock == 0)

    sort_options = {
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
        "name": Product.name.asc(),
        "stock": Product.stock.desc(),
        "newest": Product.id.desc(),
    }
    statement = statement.order_by(sort_options.get(sort_by, Product.id.desc()))

    result = await session.exec(statement)
    return result.all()

async def get_product_by_id(product_id: int, session: AsyncSession)-> Product | None:
    statement = (
        select(Product).where(Product.id == product_id)\
        .options(selectinload(Product.reviews).selectinload(Review.user))\
        .options(selectinload(Product.category))\
        .options(selectinload(Product.images))
    )
    result = await session.exec(statement)
    return result.one_or_none()

async def update_product(product: Product, data: ProductUpdate, session: AsyncSession) -> Product:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    session.add(product)
    await session.commit()
    return await get_product_by_id(product.id, session)

async def get_all_products_paginated(skip: int, limit: int, session: AsyncSession) -> List[Product]:
    """
    Retrieves a paginated list of all products from the database.
    """
    statement = (
        select(Product)
        .options(selectinload(Product.reviews).selectinload(Review.user))
        .options(selectinload(Product.category))
        .options(selectinload(Product.images))
        .offset(skip)
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()
