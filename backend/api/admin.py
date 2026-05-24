from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.auth import is_admin
from core.db import get_session
from crud import crud_review
from model.models import Coupon, Order, OrderItem, Product, Review
from schemas import AnalyticsPublic, CouponCreate, CouponPublic, ReviewPublic

router = APIRouter(dependencies=[Depends(is_admin())])


@router.get("/analytics", response_model=AnalyticsPublic)
async def get_analytics(session: AsyncSession = Depends(get_session)):
    orders = (await session.exec(select(Order))).all()
    products = (await session.exec(select(Product))).all()
    order_items = (await session.exec(select(OrderItem))).all()

    product_sales: dict[int, dict] = {}
    for item in order_items:
        if item.product_id not in product_sales:
            product_sales[item.product_id] = {"product_id": item.product_id, "quantity": 0, "revenue": 0.0}
        product_sales[item.product_id]["quantity"] += item.quantity
        product_sales[item.product_id]["revenue"] += item.line_total

    top_products = sorted(product_sales.values(), key=lambda item: item["quantity"], reverse=True)[:5]
    return AnalyticsPublic(
        total_orders=len(orders),
        total_revenue=round(sum(order.total_amount for order in orders if order.status != "cancelled"), 2),
        total_products=len(products),
        low_stock_products=len([product for product in products if product.stock <= 5]),
        pending_orders=len([order for order in orders if order.status in {"placed", "paid", "processing"}]),
        top_products=top_products,
    )


@router.post("/coupons", response_model=CouponPublic)
async def create_coupon(coupon_data: CouponCreate, session: AsyncSession = Depends(get_session)):
    coupon = Coupon.model_validate(coupon_data, update={"code": coupon_data.code.upper()})
    session.add(coupon)
    await session.commit()
    await session.refresh(coupon)
    return coupon


@router.get("/coupons", response_model=list[CouponPublic])
async def list_coupons(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Coupon).order_by(Coupon.id.desc()))
    return result.all()


@router.get("/reviews", response_model=list[ReviewPublic])
async def list_reviews(session: AsyncSession = Depends(get_session)):
    return await crud_review.get_all_reviews(session=session)


@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(review_id: int, session: AsyncSession = Depends(get_session)):
    review = await session.get(Review, review_id)
    if review:
        await session.delete(review)
        await session.commit()
