# schemas.py
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel

# These models are used for API input/output validation and are distinct from the database models.
# This allows us to control what data is exposed via the API.

# Shared properties for a user
class UserBase(SQLModel):
    username: str
    role: str = "customer"

# Properties for creating a new user (input)
class UserCreate(UserBase):
    password: str

# Properties to return from the API (output), excluding the password
class UserPublic(UserBase):
    id: int

# Shared properties for a category
class CategoryBase(SQLModel):
    name: str

# Properties for creating a new category (input)
class CategoryCreate(CategoryBase):
    pass

# Properties to return from the API (output)
class CategoryPublic(CategoryBase):
    id: int

# Shared properties for a review
class ReviewBase(SQLModel):
    text: str
    rating: int

# Properties for creating a new review (input)
class ReviewCreate(ReviewBase):
    product_id: int
    # user_id will be taken from the current authenticated user in a later part

# Public model for a review, including the user who wrote it
class ReviewPublic(ReviewBase):
    id: int
    user: UserPublic # Nested model to show user details

# Shared properties for a product
class ProductBase(SQLModel):
    name: str
    description: str
    price: float
    stock: int = 0
    image_url: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    tags: Optional[str] = None
    status: str = "published"
    is_active: bool = True

# Properties for creating a new product (input)
class ProductCreate(ProductBase):
    category_id: int

# Public model for a product, including nested category and review info
class ProductPublic(ProductBase):
    id: int
    category: CategoryPublic
    reviews: List[ReviewPublic] = []

# To avoid circular imports, we can create specific models for nested data
# that don't have their own nested relationships.

class CategoryPublicWithProducts(CategoryPublic):
    products: List[ProductPublic] = []

class UserPublicWithReviews(UserPublic):
    reviews: List[ReviewPublic] = []

class OrderCreate(SQLModel):
    customer_name: str
    item: str

class OrderResponse(SQLModel):
    id: int
    customer_name: str
    item: str
    status: str

    class Config:
        orm_mode = True


class CartItemCreate(SQLModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(SQLModel):
    quantity: int


class CartItemPublic(SQLModel):
    id: int
    quantity: int
    product: ProductPublic
    line_total: float


class CartPublic(SQLModel):
    items: List[CartItemPublic] = []
    total_items: int = 0
    total_amount: float = 0


class CheckoutCreate(SQLModel):
    shipping_address: str
    payment_method: str = "cash_on_delivery"
    card_last4: Optional[str] = None
    coupon_code: Optional[str] = None


class OrderItemPublic(SQLModel):
    id: int
    quantity: int
    unit_price: float
    line_total: float
    product: ProductPublic


class OrderPublic(SQLModel):
    id: int
    status: str
    total_amount: float
    payment_method: str
    payment_status: str
    shipping_address: str
    created_at: datetime
    items: List[OrderItemPublic] = []


class OrderStatusUpdate(SQLModel):
    status: str


class WishlistItemCreate(SQLModel):
    product_id: int


class WishlistItemPublic(SQLModel):
    id: int
    product: ProductPublic


class WishlistPublic(SQLModel):
    items: List[WishlistItemPublic] = []
    total_items: int = 0


class AddressBase(SQLModel):
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


class AddressCreate(AddressBase):
    pass


class AddressPublic(AddressBase):
    id: int


class SavedPaymentMethodBase(SQLModel):
    provider: str = "card"
    brand: str = "Card"
    last4: str
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    is_default: bool = False


class SavedPaymentMethodCreate(SavedPaymentMethodBase):
    pass


class SavedPaymentMethodPublic(SavedPaymentMethodBase):
    id: int


class NotificationPublic(SQLModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime


class ProfilePublic(SQLModel):
    user: UserPublic
    addresses: List[AddressPublic] = []
    saved_payment_methods: List[SavedPaymentMethodPublic] = []
    notifications: List[NotificationPublic] = []


class CouponCreate(SQLModel):
    code: str
    discount_percent: float
    min_order_amount: float = 0
    is_active: bool = True


class CouponPublic(CouponCreate):
    id: int


class AnalyticsPublic(SQLModel):
    total_orders: int
    total_revenue: float
    total_products: int
    low_stock_products: int
    pending_orders: int
    top_products: List[dict] = []
