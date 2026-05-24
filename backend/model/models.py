# models.py
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    role: str = "customer"

    # This relationship is named "reviews"
    reviews: List["Review"] = Relationship(back_populates="user")
    cart_items: List["CartItem"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")
    wishlist_items: List["WishlistItem"] = Relationship(back_populates="user")
    addresses: List["Address"] = Relationship(back_populates="user")
    saved_payment_methods: List["SavedPaymentMethod"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    # This relationship is named "products"
    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    price: float
    stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = None
    brand: Optional[str] = Field(default=None, index=True)
    sku: Optional[str] = Field(default=None, index=True, unique=True)
    tags: Optional[str] = None
    status: str = Field(default="published", index=True)
    is_active: bool = Field(default=True, index=True)
    category_id: int = Field(foreign_key="category.id")
    
    # Corrected: back_populates now points to "products" in the Category model
    category: Category = Relationship(back_populates="products") 
    
    # This relationship is named "reviews"
    reviews: List["Review"] = Relationship(back_populates="products")
    cart_items: List["CartItem"] = Relationship(back_populates="product")
    order_items: List["OrderItem"] = Relationship(back_populates="product")
    wishlist_items: List["WishlistItem"] = Relationship(back_populates="product")
    images: List["ProductImage"] = Relationship(back_populates="product")


class ProductImage(SQLModel, table=True):
    __tablename__ = "product_images"

    id: Optional[int] = Field(default=None, primary_key=True)
    image_url: str
    sort_order: int = Field(default=0)
    product_id: int = Field(foreign_key="product.id")

    product: Product = Relationship(back_populates="images")

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    rating: int

    user_id: int = Field(foreign_key="user.id")
    # Corrected: back_populates now points to "reviews" in the User model
    user: User = Relationship(back_populates="reviews")

    product_id: int = Field(foreign_key="product.id")
    # Corrected: back_populates now points to "reviews" in the Product model
    products: Product = Relationship(back_populates="reviews")


class ProductOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str
    item: str
    status: str = Field(default="Order Is Placed")


class CartItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(default=1, ge=1)

    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")

    user: User = Relationship(back_populates="cart_items")
    product: Product = Relationship(back_populates="cart_items")


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="placed", index=True)
    total_amount: float
    payment_method: str
    payment_status: str = Field(default="pending")
    shipping_address: str
    created_at: datetime = Field(default_factory=utc_now_naive)

    user_id: int = Field(foreign_key="user.id")

    user: User = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(default=1, ge=1)
    unit_price: float
    line_total: float

    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="product.id")

    order: Order = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="order_items")


class WishlistItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")

    user: User = Relationship(back_populates="wishlist_items")
    product: Product = Relationship(back_populates="wishlist_items")


class Address(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    label: str = "Home"
    full_name: str
    phone: str
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "Sri Lanka"
    is_default: bool = False

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="addresses")


class SavedPaymentMethod(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider: str = "card"
    brand: str = "Card"
    last4: str
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    is_default: bool = False

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="saved_payment_methods")


class Coupon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    discount_percent: float = Field(default=0)
    is_active: bool = Field(default=True, index=True)
    min_order_amount: float = Field(default=0)


class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    message: str
    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utc_now_naive)

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="notifications")
