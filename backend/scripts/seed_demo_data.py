import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlmodel import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.db import AsyncSessionFactory
from model.models import (
    Address,
    Category,
    Coupon,
    Notification,
    Order,
    OrderItem,
    Product,
    ProductImage,
    Review,
    SavedPaymentMethod,
    User,
)
from core.security import get_password_hash


CATEGORIES = [
    "Electronics",
    "Home & Living",
    "Fitness",
    "Fashion",
]


PRODUCTS = [
    {
        "name": "Wireless Headphones",
        "description": "Noise-isolating over-ear headphones with 30-hour battery life.",
        "price": 89.99,
        "stock": 18,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
        "images": [
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
            "https://images.unsplash.com/photo-1484704849700-f032a568e944",
            "https://images.unsplash.com/photo-1487215078519-e21cc028cb29",
        ],
        "brand": "SoundPeak",
        "sku": "ELEC-HEAD-001",
        "tags": "audio,wireless,headphones",
        "category": "Electronics",
    },
    {
        "name": "Smart Watch",
        "description": "Fitness tracking, heart-rate monitoring, and message alerts.",
        "price": 129.99,
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
        "images": [
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
            "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9",
            "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1",
        ],
        "brand": "PulseOne",
        "sku": "ELEC-WATCH-002",
        "tags": "wearable,watch,fitness",
        "category": "Electronics",
    },
    {
        "name": "Ceramic Table Lamp",
        "description": "Warm bedside lamp with a textured ceramic base.",
        "price": 44.50,
        "stock": 9,
        "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c",
        "images": [
            "https://images.unsplash.com/photo-1507473885765-e6ed057f782c",
            "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15",
            "https://images.unsplash.com/photo-1540932239986-30128078f3c5",
        ],
        "brand": "Nestora",
        "sku": "HOME-LAMP-003",
        "tags": "lamp,decor,home",
        "category": "Home & Living",
    },
    {
        "name": "Yoga Mat Pro",
        "description": "Non-slip cushioned yoga mat for home and studio sessions.",
        "price": 32.00,
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1603988363607-e1e4a66962c6",
        "images": [
            "https://images.unsplash.com/photo-1603988363607-e1e4a66962c6",
            "https://images.unsplash.com/photo-1518611012118-696072aa579a",
            "https://images.unsplash.com/photo-1599447292180-45fd84092ef4",
        ],
        "brand": "FlexForm",
        "sku": "FIT-YOGA-004",
        "tags": "yoga,fitness,mat",
        "category": "Fitness",
    },
    {
        "name": "Everyday Sneakers",
        "description": "Lightweight sneakers designed for daily comfort.",
        "price": 64.99,
        "stock": 0,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "images": [
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            "https://images.unsplash.com/photo-1549298916-b41d501d3772",
            "https://images.unsplash.com/photo-1543508282-6319a3e2621f",
        ],
        "brand": "StrideLab",
        "sku": "FASH-SHOE-005",
        "tags": "shoes,sneakers,fashion",
        "category": "Fashion",
    },
    {
        "name": "Minimal Backpack",
        "description": "Water-resistant backpack with padded laptop sleeve.",
        "price": 58.75,
        "stock": 14,
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
        "images": [
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
            "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3",
            "https://images.unsplash.com/photo-1581605405669-fcdf81165afa",
        ],
        "brand": "CarryCo",
        "sku": "FASH-BAG-006",
        "tags": "bag,travel,laptop",
        "category": "Fashion",
    },
]


async def seed() -> None:
    async with AsyncSessionFactory() as session:
        demo_users = [
            ("admin_demo", "Admin@123", "admin"),
            ("customer_demo", "Customer@123", "customer"),
        ]
        for username, password, role in demo_users:
            result = await session.exec(select(User).where(User.username == username))
            user = result.one_or_none()
            if user is None:
                session.add(
                    User(
                        username=username,
                        password=get_password_hash(password),
                        role=role,
                    )
                )

        categories_by_name: dict[str, Category] = {}
        for name in CATEGORIES:
            result = await session.exec(select(Category).where(Category.name == name))
            category = result.one_or_none()
            if category is None:
                category = Category(name=name)
                session.add(category)
                await session.flush()
            categories_by_name[name] = category

        products_by_sku: dict[str, Product] = {}
        for data in PRODUCTS:
            result = await session.exec(select(Product).where(Product.sku == data["sku"]))
            product = result.one_or_none()
            payload = {
                key: value
                for key, value in data.items()
                if key not in {"category", "images"}
            }
            payload["category_id"] = categories_by_name[data["category"]].id

            if product is None:
                product = Product(**payload)
                session.add(product)
                await session.flush()
            else:
                for key, value in payload.items():
                    setattr(product, key, value)
                session.add(product)
            products_by_sku[data["sku"]] = product

            image_result = await session.exec(
                select(ProductImage).where(ProductImage.product_id == product.id)
            )
            existing_images = image_result.all()
            if not existing_images:
                for index, image_url in enumerate(data["images"]):
                    session.add(
                        ProductImage(
                            product_id=product.id,
                            image_url=image_url,
                            sort_order=index,
                        )
                    )

        coupon_result = await session.exec(select(Coupon).where(Coupon.code == "WELCOME10"))
        coupon = coupon_result.one_or_none()
        if coupon is None:
            session.add(
                Coupon(
                    code="WELCOME10",
                    discount_percent=10,
                    min_order_amount=50,
                    is_active=True,
                )
            )

        user_result = await session.exec(select(User).where(User.username == "Vipin_yadav"))
        demo_user = user_result.one_or_none()

        if demo_user is not None:
            address_result = await session.exec(
                select(Address).where(
                    Address.user_id == demo_user.id,
                    Address.line1 == "42 Market Street",
                )
            )
            if address_result.one_or_none() is None:
                session.add(
                    Address(
                        user_id=demo_user.id,
                        label="Home",
                        full_name="Vipin Yadav",
                        phone="+94 77 123 4567",
                        line1="42 Market Street",
                        line2="Apartment 5B",
                        city="Colombo",
                        state="Western Province",
                        postal_code="00300",
                        country="Sri Lanka",
                        is_default=True,
                    )
                )

            payment_result = await session.exec(
                select(SavedPaymentMethod).where(
                    SavedPaymentMethod.user_id == demo_user.id,
                    SavedPaymentMethod.last4 == "4242",
                )
            )
            if payment_result.one_or_none() is None:
                session.add(
                    SavedPaymentMethod(
                        user_id=demo_user.id,
                        provider="card",
                        brand="Visa",
                        last4="4242",
                        expiry_month=12,
                        expiry_year=2028,
                        is_default=True,
                    )
                )

            notification_result = await session.exec(
                select(Notification).where(
                    Notification.user_id == demo_user.id,
                    Notification.title == "Welcome to the demo store",
                )
            )
            if notification_result.one_or_none() is None:
                session.add(
                    Notification(
                        user_id=demo_user.id,
                        title="Welcome to the demo store",
                        message="Your sample catalog and account data are ready.",
                    )
                )

            order_result = await session.exec(select(Order).where(Order.user_id == demo_user.id))
            if order_result.first() is None:
                headphones = products_by_sku["ELEC-HEAD-001"]
                yoga_mat = products_by_sku["FIT-YOGA-004"]
                order = Order(
                    user_id=demo_user.id,
                    status="processing",
                    total_amount=131.75,
                    payment_method="card",
                    payment_status="paid",
                    shipping_address="42 Market Street, Apartment 5B, Colombo",
                    created_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )
                session.add(order)
                await session.flush()
                session.add(
                    OrderItem(
                        order_id=order.id,
                        product_id=headphones.id,
                        quantity=1,
                        unit_price=headphones.price,
                        line_total=headphones.price,
                    )
                )
                session.add(
                    OrderItem(
                        order_id=order.id,
                        product_id=yoga_mat.id,
                        quantity=1,
                        unit_price=yoga_mat.price,
                        line_total=yoga_mat.price,
                    )
                )

            review_specs = [
                ("ELEC-HEAD-001", "Excellent sound and very comfortable for long sessions.", 5),
                ("FIT-YOGA-004", "Good grip and enough cushioning for daily practice.", 4),
                ("FASH-BAG-006", "Clean design and the laptop sleeve is genuinely useful.", 5),
            ]
            for sku, text, rating in review_specs:
                product = products_by_sku[sku]
                review_result = await session.exec(
                    select(Review).where(
                        Review.user_id == demo_user.id,
                        Review.product_id == product.id,
                        Review.text == text,
                    )
                )
                if review_result.one_or_none() is None:
                    session.add(
                        Review(
                            user_id=demo_user.id,
                            product_id=product.id,
                            text=text,
                            rating=rating,
                        )
                    )

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
