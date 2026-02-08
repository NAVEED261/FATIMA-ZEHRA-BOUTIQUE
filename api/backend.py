"""
Fatima Zehra Boutique — Unified Netlify Serverless Backend
All 4 microservices (users, products, orders, chat) in one FastAPI app.
Wrapped by Mangum for Netlify Functions.
"""

import os
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine, select, func, Column
from sqlalchemy import Numeric
from mangum import Mangum
from openai import AsyncOpenAI

# ---------------------------------------------------------------------------
# CONFIG — load from env (Vercel may not populate at module load time)
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/learnflow")

JWT_SECRET = os.getenv("JWT_SECRET", "your-random-32-character-secret-key-fatima-zehra-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ---------------------------------------------------------------------------
# DATABASE ENGINE — NullPool for serverless (no persistent connections)
# ---------------------------------------------------------------------------
from sqlalchemy.pool import NullPool

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"connect_timeout": 10},
)


def get_session():
    with Session(engine) as session:
        yield session


# ---------------------------------------------------------------------------
# TABLE MODELS
# ---------------------------------------------------------------------------
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Category(SQLModel, table=True):
    __tablename__ = "categories"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    description: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None, max_length=500)
    products: list["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: Optional[str] = Field(default=None)
    price: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    original_price: Optional[Decimal] = Field(default=None, sa_column=Column("original_price", Numeric(precision=10, scale=2), nullable=True))
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    image_url: Optional[str] = Field(default=None, max_length=500)
    material: Optional[str] = Field(default=None, max_length=100)
    rating: Optional[float] = Field(default=None)
    reviews: Optional[int] = Field(default=0)
    details: Optional[str] = Field(default=None)
    sizes: Optional[str] = Field(default=None)       # JSON array stored as text
    colors: Optional[str] = Field(default=None)     # JSON array stored as text
    stock_quantity: int = Field(default=100)
    is_active: bool = Field(default=True, index=True)
    featured: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    category: Optional[Category] = Relationship(back_populates="products")


class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    items: list["CartItem"] = Relationship(back_populates="cart", cascade_delete=True)


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="carts.id", index=True)
    product_id: int = Field(index=True)
    quantity: int = Field(default=1, ge=1)
    price: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    cart: Optional[Cart] = Relationship(back_populates="items")


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    status: str = Field(default="pending", max_length=50, index=True)
    total_amount: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    shipping_address: str
    payment_status: str = Field(default="pending", max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    items: list["OrderItem"] = Relationship(back_populates="order", cascade_delete=True)


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    product_id: int = Field(index=True)
    product_name: str = Field(max_length=255)
    quantity: int = Field(ge=1)
    price: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    order: Optional[Order] = Relationship(back_populates="items")


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, index=True)
    session_id: str = Field(index=True, max_length=100)
    role: str = Field(max_length=20)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


# ---------------------------------------------------------------------------
# REQUEST / RESPONSE SCHEMAS
# ---------------------------------------------------------------------------
class UserCreate(SQLModel):
    email: str
    password: str
    full_name: str


class UserLogin(SQLModel):
    email: str
    password: str


class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserResponse(SQLModel):
    id: int
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class CategoryResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProductResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    original_price: Optional[Decimal] = None
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    image_url: Optional[str] = None
    material: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    details: Optional[str] = None
    sizes: Optional[list[str]] = None
    colors: Optional[list[str]] = None
    stock_quantity: int
    is_active: bool
    featured: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(SQLModel):
    products: list[ProductResponse]
    total: int
    skip: int
    limit: int


class AddToCartRequest(SQLModel):
    product_id: int
    quantity: int = 1
    price: Decimal


class UpdateCartItemRequest(SQLModel):
    quantity: int


class CheckoutRequest(SQLModel):
    shipping_address: str


class CartItemResponse(SQLModel):
    id: int
    product_id: int
    quantity: int
    price: Decimal

    class Config:
        from_attributes = True


class CartResponse(SQLModel):
    id: int
    user_id: int
    items: list[CartItemResponse]
    total_amount: Decimal
    item_count: int


class OrderItemResponse(SQLModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: Decimal

    class Config:
        from_attributes = True


class OrderResponse(SQLModel):
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    shipping_address: str
    payment_status: str
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageRequest(SQLModel):
    text: str
    session_id: str
    user_id: Optional[int] = None


class ChatMessageResponse(SQLModel):
    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(SQLModel):
    messages: list[ChatMessageResponse]
    total: int
    session_id: str


# ---------------------------------------------------------------------------
# AUTH UTILITIES
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode(), password_hash.encode())
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=JWT_EXPIRATION_HOURS))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# SHARED DEPENDENCIES
# ---------------------------------------------------------------------------
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    email = payload.get("sub")
    user_id = payload.get("id")
    if email is None or user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token data", headers={"WWW-Authenticate": "Bearer"})
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None or user.email != email:
        raise HTTPException(status_code=401, detail="User not found", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    return user


async def get_user_id_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """Decode JWT and return user_id — fixes the broken stub in order-service."""
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    user_id = payload.get("id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token data", headers={"WWW-Authenticate": "Bearer"})
    return user_id


# ---------------------------------------------------------------------------
# HELPER: parse JSON arrays stored in Product text columns
# ---------------------------------------------------------------------------
def _parse_product(p: Product) -> dict:
    """Convert a Product row into a dict suitable for ProductResponse."""
    data = {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "original_price": p.original_price,
        "category_id": p.category_id,
        "category": {"id": p.category.id, "name": p.category.name, "description": p.category.description, "image_url": p.category.image_url} if p.category else None,
        "image_url": p.image_url,
        "material": p.material,
        "rating": p.rating,
        "reviews": p.reviews,
        "details": p.details,
        "sizes": json.loads(p.sizes) if p.sizes else None,
        "colors": json.loads(p.colors) if p.colors else None,
        "stock_quantity": p.stock_quantity,
        "is_active": p.is_active,
        "featured": p.featured,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }
    return data


# ---------------------------------------------------------------------------
# USER ROUTES
# ---------------------------------------------------------------------------
user_router = APIRouter(prefix="/api/users", tags=["users"])


@user_router.post("/register", response_model=LoginResponse, status_code=201)
async def register(user_data: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    access_token = create_access_token({"sub": db_user.email, "id": db_user.id})
    return LoginResponse(access_token=access_token, user=UserResponse.model_validate(db_user))


@user_router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == credentials.email)).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    access_token = create_access_token({"sub": user.email, "id": user.id})
    return LoginResponse(access_token=access_token, user=UserResponse.model_validate(user))


@user_router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@user_router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.id == current_user.id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.model_validate(user)


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------
# PRODUCT ROUTES
# ---------------------------------------------------------------------------
product_router = APIRouter(tags=["products"])


@product_router.get("/api/categories", response_model=list[CategoryResponse])
async def list_categories(session: Session = Depends(get_session)):
    categories = session.exec(select(Category)).all()
    return [CategoryResponse.model_validate(c) for c in categories]


@product_router.get("/api/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, session: Session = Depends(get_session)):
    cat = session.exec(select(Category).where(Category.id == category_id)).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(cat)


@product_router.get("/api/products")
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    featured: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    session: Session = Depends(get_session),
):
    query = select(Product).where(Product.is_active == True)
    count_query = select(func.count(Product.id)).where(Product.is_active == True)

    if category_id:
        query = query.where(Product.category_id == category_id)
        count_query = count_query.where(Product.category_id == category_id)
    if featured is not None:
        query = query.where(Product.featured == featured)
        count_query = count_query.where(Product.featured == featured)
    if search:
        term = f"%{search}%"
        cond = (Product.name.ilike(term)) | (Product.description.ilike(term))
        query = query.where(cond)
        count_query = count_query.where(cond)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
        count_query = count_query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
        count_query = count_query.where(Product.price <= max_price)

    total = session.exec(count_query).one()
    products = session.exec(query.offset(skip).limit(limit)).all()

    return {
        "products": [_parse_product(p) for p in products],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@product_router.get("/api/products/{product_id}")
async def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.exec(
        select(Product).where((Product.id == product_id) & (Product.is_active == True))
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _parse_product(product)


# ---------------------------------------------------------------------------
# ORDER ROUTES  (uses proper JWT decode via get_user_id_from_token)
# ---------------------------------------------------------------------------
order_router = APIRouter(tags=["orders"])


@order_router.get("/api/cart", response_model=CartResponse)
async def get_cart(
    user_id: int = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    total = sum(item.price * item.quantity for item in cart.items)
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=[CartItemResponse.model_validate(i) for i in cart.items],
        total_amount=total,
        item_count=len(cart.items),
    )


@order_router.post("/api/cart/items", response_model=CartResponse)
async def add_to_cart(
    item_data: AddToCartRequest,
    user_id: int = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)

    existing = session.exec(
        select(CartItem).where((CartItem.cart_id == cart.id) & (CartItem.product_id == item_data.product_id))
    ).first()

    if existing:
        existing.quantity += item_data.quantity
        session.add(existing)
    else:
        session.add(CartItem(cart_id=cart.id, product_id=item_data.product_id, quantity=item_data.quantity, price=item_data.price))

    cart.updated_at = datetime.utcnow()
    session.add(cart)
    session.commit()
    session.refresh(cart)

    total = sum(item.price * item.quantity for item in cart.items)
    return CartResponse(
        id=cart.id, user_id=cart.user_id,
        items=[CartItemResponse.model_validate(i) for i in cart.items],
        total_amount=total, item_count=len(cart.items),
    )


@order_router.put("/api/cart/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: int,
    update_data: UpdateCartItemRequest,
    user_id: int = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    cart_item = session.exec(select(CartItem).where(CartItem.id == item_id)).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    cart = session.exec(select(Cart).where(Cart.id == cart_item.cart_id)).first()
    if cart.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    cart_item.quantity = update_data.quantity
    session.add(cart_item)
    cart.updated_at = datetime.utcnow()
    session.add(cart)
    session.commit()
    session.refresh(cart)
    total = sum(item.price * item.quantity for item in cart.items)
    return CartResponse(
        id=cart.id, user_id=cart.user_id,
        items=[CartItemResponse.model_validate(i) for i in cart.items],
        total_amount=total, item_count=len(cart.items),
    )


@order_router.delete("/api/cart/items/{item_id}", status_code=204)
async def remove_from_cart(
    item_id: int,
    user_id: int = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    cart_item = session.exec(select(CartItem).where(CartItem.id == item_id)).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    cart = session.exec(select(Cart).where(Cart.id == cart_item.cart_id)).first()
    if cart.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    session.delete(cart_item)
    cart.updated_at = datetime.utcnow()
    session.add(cart)
    session.commit()


@order_router.delete("/api/cart", status_code=204)
async def clear_cart(
    user_id: int = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if cart:
        for item in cart.items:
            session.delete(item)
        cart.updated_at = datetime.utcnow()
        session.add(cart)
        session.commit()


@order_router.post("/api/checkout", response_model=OrderResponse, status_code=201)
async def checkout(
    checkout_data: CheckoutRequest,
    user_id: int = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart or len(cart.items) == 0:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = sum(item.price * item.quantity for item in cart.items)
    order = Order(user_id=user_id, status="pending", total_amount=total_amount, shipping_address=checkout_data.shipping_address, payment_status="pending")
    session.add(order)
    session.commit()
    session.refresh(order)

    for ci in cart.items:
        # Try to get product name from DB; fallback to generic
        prod = session.exec(select(Product).where(Product.id == ci.product_id)).first()
        pname = prod.name if prod else f"Product {ci.product_id}"
        session.add(OrderItem(order_id=order.id, product_id=ci.product_id, product_name=pname, quantity=ci.quantity, price=ci.price))

    for ci in cart.items:
        session.delete(ci)
    session.commit()
    session.refresh(order)
    return OrderResponse.model_validate(order)


@order_router.get("/api/orders", response_model=list[OrderResponse])
async def list_orders(
    user_id: int = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    orders = session.exec(select(Order).where(Order.user_id == user_id)).all()
    return [OrderResponse.model_validate(o) for o in orders]


@order_router.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    user_id: int = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    order = session.exec(select(Order).where(Order.id == order_id)).first()
    if not order or order.user_id != user_id:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse.model_validate(order)


# ---------------------------------------------------------------------------
# CHAT ROUTES
# ---------------------------------------------------------------------------
chat_router = APIRouter(prefix="/api/chat", tags=["chat"])

# Lazy initialization of OpenAI client to handle Vercel env vars
_async_openai = None

def get_openai_client():
    """Get or create OpenAI client (lazy initialization for Vercel)"""
    global _async_openai
    if _async_openai is None:
        # Re-read env var in case it was set after module load (Vercel)
        api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        _async_openai = AsyncOpenAI(api_key=api_key)
    return _async_openai

# Keep for backwards compatibility
async_openai = None  # Will be set lazily

SYSTEM_PROMPT = """You are a helpful shopping assistant for Fatima Zehra Boutique, an elegant fashion boutique.

Your role is to:
1. Help customers find and learn about products
2. Provide fashion advice and recommendations
3. Answer questions about products, categories, and services
4. Guide customers through their shopping experience
5. Be friendly, professional, and helpful

When customers ask about products, provide helpful suggestions based on what they're looking for.
Keep responses concise and engaging.
Focus on helping customers find what they need."""


async def stream_chat_response(messages: list[dict], model: str = "gpt-4o"):
    try:
        # Check if API key is available
        api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
        if not api_key or len(api_key) < 10:
            yield f"Error: OpenAI API key not configured (length: {len(api_key) if api_key else 0})"
            return

        client = get_openai_client()  # Get or initialize client
        stream = await client.chat.completions.create(
            model=model, messages=messages, stream=True, temperature=0.7, max_tokens=1000,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"Chat error: {error_detail}", flush=True)
        traceback.print_exc()
        yield f"Error: {error_detail}"


@chat_router.post("/messages")
async def send_message(message_data: ChatMessageRequest, session: Session = Depends(get_session)):
    # Save user message
    user_msg = ChatMessage(
        user_id=message_data.user_id,
        session_id=message_data.session_id,
        role="user",
        content=message_data.text,
    )
    session.add(user_msg)
    session.commit()

    # Get history for context
    history = session.exec(
        select(ChatMessage).where(ChatMessage.session_id == message_data.session_id).order_by(ChatMessage.created_at)
    ).all()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    async def response_generator():
        full_response = ""
        async for chunk in stream_chat_response(messages):
            full_response += chunk
            yield f"data: {chunk}\n\n"

        # Save assistant message
        assistant_msg = ChatMessage(
            user_id=message_data.user_id,
            session_id=message_data.session_id,
            role="assistant",
            content=full_response,
        )
        session.add(assistant_msg)
        session.commit()
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@chat_router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    total = session.exec(select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session_id)).one()
    msgs = session.exec(
        select(ChatMessage).where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc()).limit(limit).offset(offset)
    ).all()
    msgs = list(reversed(msgs))
    return ChatHistoryResponse(
        messages=[ChatMessageResponse.model_validate(m) for m in msgs],
        total=total,
        session_id=session_id,
    )


@chat_router.delete("/history")
async def clear_chat_history(session_id: str, session: Session = Depends(get_session)):
    msgs = session.exec(select(ChatMessage).where(ChatMessage.session_id == session_id)).all()
    for msg in msgs:
        session.delete(msg)
    session.commit()
    return {"message": "Chat history cleared", "session_id": session_id}


# ---------------------------------------------------------------------------
# SEED DATA — 4 categories + 40 products (mirrors frontend lib/products.ts)
# ---------------------------------------------------------------------------
SEED_CATEGORIES = [
    {"name": "Fancy Suits", "description": "Elegant party wear and bridal collection"},
    {"name": "Shalwar Qameez", "description": "Classic traditional Pakistani wear"},
    {"name": "Cotton Suits", "description": "Comfortable everyday cotton suits"},
    {"name": "Designer Brands", "description": "Premium designer brand collections"},
]

SEED_PRODUCTS = [
    # --- Fancy Suits (category index 0 → category_id 1) ---
    {"name":"Royal Embroidered Fancy Suit","description":"Elegant party wear with intricate hand embroidery and premium fabric.","price":"8500","original_price":"12000","image_url":"/images/fancy-suits/fancy-suits-01.jpg","material":"Premium Chiffon","rating":4.8,"reviews":124,"details":"Features hand-embroidered motifs with premium chiffon fabric. Perfect for weddings and special occasions.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Red","Pink","Gold","Purple"],"category_idx":0,"featured":True},
    {"name":"Golden Zari Work Suit","description":"Luxurious golden zari embroidery perfect for weddings and special occasions.","price":"9500","original_price":"13500","image_url":"/images/fancy-suits/fancy-suits-02.jpg","material":"Pure Silk","rating":4.9,"reviews":89,"details":"Luxurious golden zari embroidery perfect for weddings and special occasions.","sizes":None,"colors":None,"category_idx":0,"featured":True},
    {"name":"Pearl Embellished Fancy Dress","description":"Beautiful pearl work with delicate sequins for a sophisticated look.","price":"7800","original_price":"10500","image_url":"/images/fancy-suits/fancy-suits-03.jpg","material":"Organza","rating":4.7,"reviews":156,"details":"Beautiful pearl work with delicate sequins for a sophisticated look.","sizes":["XS","S","M","L","XL","XXL"],"colors":["White","Light Pink","Peach"],"category_idx":0,"featured":True},
    {"name":"Velvet Royal Collection","description":"Premium velvet suit with traditional motifs and modern cuts.","price":"11000","original_price":"15000","image_url":"/images/fancy-suits/fancy-suits-04.jpg","material":"Italian Velvet","rating":4.9,"reviews":67,"details":"Premium velvet suit with traditional motifs and modern cuts.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Maroon","Navy","Black"],"category_idx":0,"featured":True},
    {"name":"Crystal Stone Work Suit","description":"Dazzling crystal stone work for glamorous evening events.","price":"8900","original_price":"12500","image_url":"/images/fancy-suits/fancy-suits-05.jpg","material":"Net with Silk Lining","rating":4.6,"reviews":98,"details":"Dazzling crystal stone work for glamorous evening events.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Silver","Gold","Pink"],"category_idx":0,"featured":False},
    {"name":"Bridal Fancy Ensemble","description":"Exquisite bridal collection with heavy embroidery and dupatta.","price":"15000","original_price":"22000","image_url":"/images/fancy-suits/fancy-suits-06.jpg","material":"Jamawar","rating":5.0,"reviews":45,"details":"Exquisite bridal collection with heavy embroidery and dupatta.","sizes":["XS","S","M","L","XL"],"colors":["Red","Green","Gold"],"category_idx":0,"featured":True},
    {"name":"Mirror Work Designer Suit","description":"Traditional mirror work with contemporary design elements.","price":"7500","original_price":"9800","image_url":"/images/fancy-suits/fancy-suits-07.jpg","material":"Georgette","rating":4.5,"reviews":112,"details":"Traditional mirror work with contemporary design elements.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Pink","Blue","Cream"],"category_idx":0,"featured":False},
    {"name":"Pastel Fancy Collection","description":"Soft pastel shades with delicate threadwork for elegant occasions.","price":"6800","original_price":"8500","image_url":"/images/fancy-suits/fancy-suits-08.jpg","material":"Chiffon","rating":4.7,"reviews":134,"details":"Soft pastel shades with delicate threadwork for elegant occasions.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Lavender","Peach","Mint"],"category_idx":0,"featured":False},
    {"name":"Maroon Festive Suit","description":"Rich maroon color with gold accents for festive celebrations.","price":"8200","original_price":"11000","image_url":"/images/fancy-suits/fancy-suits-09.jpg","material":"Silk Blend","rating":4.8,"reviews":78,"details":"Rich maroon color with gold accents for festive celebrations.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Maroon","Gold"],"category_idx":0,"featured":False},
    {"name":"Navy Blue Sequin Suit","description":"Stunning navy blue with all-over sequin work for party nights.","price":"9200","original_price":"13000","image_url":"/images/fancy-suits/fancy-suits-10.jpg","material":"Premium Net","rating":4.6,"reviews":91,"details":"Stunning navy blue with all-over sequin work for party nights.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Navy","Black","Teal"],"category_idx":0,"featured":False},
    # --- Shalwar Qameez (category index 1 → category_id 2) ---
    {"name":"Classic White Shalwar Qameez","description":"Timeless white with subtle embroidery for everyday elegance.","price":"3500","original_price":"4500","image_url":"/images/shalwar-qameez/shalwar-qameez-01.jpg","material":"Lawn Cotton","rating":4.5,"reviews":234,"details":"Timeless white with subtle embroidery for everyday elegance.","sizes":["XS","S","M","L","XL","XXL"],"colors":["White","Cream","Off-white"],"category_idx":1,"featured":False},
    {"name":"Printed Lawn Collection","description":"Vibrant digital prints for a fresh summer look.","price":"2800","original_price":"3800","image_url":"/images/shalwar-qameez/shalwar-qameez-02.jpg","material":"Digital Lawn","rating":4.4,"reviews":189,"details":"Vibrant digital prints for a fresh summer look.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Multi","Blue","Green"],"category_idx":1,"featured":False},
    {"name":"Embroidered Neck Design","description":"Beautiful neck embroidery with matching trouser and dupatta.","price":"4200","original_price":"5500","image_url":"/images/shalwar-qameez/shalwar-qameez-03.jpg","material":"Cambric","rating":4.6,"reviews":156,"details":"Beautiful neck embroidery with matching trouser and dupatta.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Pink","Green","Purple"],"category_idx":1,"featured":False},
    {"name":"Traditional Block Print","description":"Hand block printed design with traditional patterns.","price":"3200","original_price":"4200","image_url":"/images/shalwar-qameez/shalwar-qameez-04.jpg","material":"Pure Cotton","rating":4.3,"reviews":167,"details":"Hand block printed design with traditional patterns.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Indigo","Brown","Maroon"],"category_idx":1,"featured":False},
    {"name":"Pastel Summer Collection","description":"Light and breezy pastel shades perfect for summer days.","price":"2600","original_price":"3400","image_url":"/images/shalwar-qameez/shalwar-qameez-05.jpg","material":"Lawn","rating":4.5,"reviews":198,"details":"Light and breezy pastel shades perfect for summer days.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Pink","Yellow","Blue"],"category_idx":1,"featured":False},
    {"name":"Chikan Kari Suit","description":"Authentic Lucknowi chikan embroidery on premium fabric.","price":"5500","original_price":"7500","image_url":"/images/shalwar-qameez/shalwar-qameez-06.jpg","material":"Muslin","rating":4.8,"reviews":89,"details":"Authentic Lucknowi chikan embroidery on premium fabric.","sizes":["XS","S","M","L","XL","XXL"],"colors":["White","Beige","Light Green"],"category_idx":1,"featured":False},
    {"name":"Floral Print Daily Wear","description":"Cheerful floral prints for comfortable daily wear.","price":"2400","original_price":"3000","image_url":"/images/shalwar-qameez/shalwar-qameez-07.jpg","material":"Cotton Blend","rating":4.2,"reviews":245,"details":"Cheerful floral prints for comfortable daily wear.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Multi","Pink","Purple"],"category_idx":1,"featured":False},
    {"name":"Geometric Pattern Suit","description":"Modern geometric patterns with contrast borders.","price":"3100","original_price":"4000","image_url":"/images/shalwar-qameez/shalwar-qameez-08.jpg","material":"Lawn Cotton","rating":4.4,"reviews":134,"details":"Modern geometric patterns with contrast borders.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Black","White","Gray"],"category_idx":1,"featured":False},
    {"name":"Eid Special Collection","description":"Special Eid collection with premium finish and dupatta.","price":"4800","original_price":"6500","image_url":"/images/shalwar-qameez/shalwar-qameez-09.jpg","material":"Premium Lawn","rating":4.7,"reviews":78,"details":"Special Eid collection with premium finish and dupatta.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Pink","Green","Gold"],"category_idx":1,"featured":False},
    {"name":"Royal Blue Shalwar Qameez","description":"Elegant royal blue with silver embroidery accents.","price":"3800","original_price":"5000","image_url":"/images/shalwar-qameez/shalwar-qameez-10.jpg","material":"Cambric Cotton","rating":4.6,"reviews":112,"details":"Elegant royal blue with silver embroidery accents.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Royal Blue","Silver"],"category_idx":1,"featured":False},
    # --- Cotton Suits (category index 2 → category_id 3) ---
    {"name":"Pure Cotton Comfort Suit","description":"100% pure cotton for maximum comfort in all seasons.","price":"2200","original_price":"2800","image_url":"/images/cotton-suits/cotton-suits-01.jpg","material":"Pure Cotton","rating":4.5,"reviews":312,"details":"100% pure cotton for maximum comfort in all seasons.","sizes":["XS","S","M","L","XL","XXL"],"colors":["White","Beige","Cream"],"category_idx":2,"featured":False},
    {"name":"Organic Cotton Collection","description":"Eco-friendly organic cotton for conscious fashion.","price":"2800","original_price":"3600","image_url":"/images/cotton-suits/cotton-suits-02.jpg","material":"Organic Cotton","rating":4.6,"reviews":178,"details":"Eco-friendly organic cotton for conscious fashion.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Natural","Green","Brown"],"category_idx":2,"featured":False},
    {"name":"Printed Cotton Daily Wear","description":"Cheerful prints for everyday comfort and style.","price":"1900","original_price":"2400","image_url":"/images/cotton-suits/cotton-suits-03.jpg","material":"Cotton Blend","rating":4.3,"reviews":289,"details":"Cheerful prints for everyday comfort and style.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Multi","Pink","Blue"],"category_idx":2,"featured":False},
    {"name":"Handloom Cotton Suit","description":"Authentic handloom cotton with natural dyes.","price":"3500","original_price":"4800","image_url":"/images/cotton-suits/cotton-suits-04.jpg","material":"Handloom Cotton","rating":4.7,"reviews":94,"details":"Authentic handloom cotton with natural dyes.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Indigo","Red","Brown"],"category_idx":2,"featured":False},
    {"name":"Khadi Cotton Classic","description":"Traditional khadi cotton with modern cuts.","price":"3200","original_price":"4200","image_url":"/images/cotton-suits/cotton-suits-05.jpg","material":"Khadi Cotton","rating":4.5,"reviews":156,"details":"Traditional khadi cotton with modern cuts.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Cream","Khaki","White"],"category_idx":2,"featured":False},
    {"name":"Summer Breathable Suit","description":"Ultra-breathable cotton for hot summer days.","price":"2100","original_price":"2700","image_url":"/images/cotton-suits/cotton-suits-06.jpg","material":"Soft Cotton","rating":4.4,"reviews":234,"details":"Ultra-breathable cotton for hot summer days.","sizes":["XS","S","M","L","XL","XXL"],"colors":["White","Light Blue","Mint"],"category_idx":2,"featured":False},
    {"name":"Stripes Cotton Collection","description":"Classic stripes pattern for a timeless look.","price":"2400","original_price":"3100","image_url":"/images/cotton-suits/cotton-suits-07.jpg","material":"Cotton","rating":4.2,"reviews":198,"details":"Classic stripes pattern for a timeless look.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Blue","Gray","Black"],"category_idx":2,"featured":False},
    {"name":"Linen Cotton Blend","description":"Luxurious linen-cotton blend for special occasions.","price":"3800","original_price":"5000","image_url":"/images/cotton-suits/cotton-suits-08.jpg","material":"Linen Cotton","rating":4.6,"reviews":87,"details":"Luxurious linen-cotton blend for special occasions.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Beige","White","Light Gray"],"category_idx":2,"featured":False},
    {"name":"Embroidered Cotton Suit","description":"Light embroidery on pure cotton for semi-formal wear.","price":"2900","original_price":"3800","image_url":"/images/cotton-suits/cotton-suits-09.jpg","material":"Premium Cotton","rating":4.5,"reviews":145,"details":"Light embroidery on pure cotton for semi-formal wear.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Pink","Blue","Green"],"category_idx":2,"featured":False},
    {"name":"Pastel Cotton Collection","description":"Soft pastel shades in comfortable cotton fabric.","price":"2300","original_price":"2900","image_url":"/images/cotton-suits/cotton-suits-10.jpg","material":"Soft Cotton","rating":4.4,"reviews":212,"details":"Soft pastel shades in comfortable cotton fabric.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Lavender","Peach","Mint"],"category_idx":2,"featured":False},
    # --- Designer Brands (category index 3 → category_id 4) ---
    {"name":"Maria B Premium Collection","description":"Exclusive Maria B designer suit with premium finishing.","price":"12500","original_price":"18000","image_url":"/images/designer-brands/designer-brands-01.jpg","material":"Premium Silk","rating":4.9,"reviews":67,"details":"Exclusive Maria B designer suit with premium finishing.","sizes":["XS","S","M","L","XL"],"colors":["Pink","Gold","Purple"],"category_idx":3,"featured":True},
    {"name":"Sana Safinaz Luxury","description":"Sana Safinaz signature collection with intricate details.","price":"14000","original_price":"20000","image_url":"/images/designer-brands/designer-brands-02.jpg","material":"Pure Chiffon","rating":4.8,"reviews":89,"details":"Sana Safinaz signature collection with intricate details.","sizes":["XS","S","M","L","XL"],"colors":["Multi","Red","Green"],"category_idx":3,"featured":True},
    {"name":"Khaadi Exclusive","description":"Khaadi exclusive print with traditional craftsmanship.","price":"8500","original_price":"11000","image_url":"/images/designer-brands/designer-brands-03.jpg","material":"Khaddar","rating":4.7,"reviews":156,"details":"Khaadi exclusive print with traditional craftsmanship.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Indigo","Gray","Brown"],"category_idx":3,"featured":False},
    {"name":"Gul Ahmed Premium","description":"Gul Ahmed premium lawn with digital embroidery.","price":"7800","original_price":"10500","image_url":"/images/designer-brands/designer-brands-04.jpg","material":"Premium Lawn","rating":4.6,"reviews":198,"details":"Gul Ahmed premium lawn with digital embroidery.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Pink","Green","Blue"],"category_idx":3,"featured":False},
    {"name":"Alkaram Studio","description":"Alkaram Studio festive collection with luxury dupatta.","price":"9200","original_price":"12500","image_url":"/images/designer-brands/designer-brands-05.jpg","material":"Silk Blend","rating":4.7,"reviews":134,"details":"Alkaram Studio festive collection with luxury dupatta.","sizes":["XS","S","M","L","XL"],"colors":["Red","Pink","Green"],"category_idx":3,"featured":False},
    {"name":"Sapphire Designer Suit","description":"Sapphire signature style with modern aesthetics.","price":"6800","original_price":"8500","image_url":"/images/designer-brands/designer-brands-06.jpg","material":"Cotton Silk","rating":4.5,"reviews":178,"details":"Sapphire signature style with modern aesthetics.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Navy","Black","Gray"],"category_idx":3,"featured":False},
    {"name":"Nishat Linen Luxury","description":"Nishat Linen premium collection with exclusive prints.","price":"7200","original_price":"9500","image_url":"/images/designer-brands/designer-brands-07.jpg","material":"Pure Linen","rating":4.6,"reviews":145,"details":"Nishat Linen premium collection with exclusive prints.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Blue","Pink","Green"],"category_idx":3,"featured":False},
    {"name":"Ethnic by Outfitters","description":"Contemporary ethnic wear with fusion elements.","price":"5500","original_price":"7000","image_url":"/images/designer-brands/designer-brands-08.jpg","material":"Lawn Blend","rating":4.4,"reviews":167,"details":"Contemporary ethnic wear with fusion elements.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Multi","Brown","Cream"],"category_idx":3,"featured":False},
    {"name":"Bonanza Satrangi","description":"Bonanza Satrangi vibrant collection for festive season.","price":"6200","original_price":"8000","image_url":"/images/designer-brands/designer-brands-09.jpg","material":"Lawn","rating":4.5,"reviews":123,"details":"Bonanza Satrangi vibrant collection for festive season.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Multi","Pink","Green"],"category_idx":3,"featured":False},
    {"name":"Limelight Designer","description":"Limelight designer suit with premium embellishments.","price":"5800","original_price":"7500","image_url":"/images/designer-brands/designer-brands-10.jpg","material":"Cotton Blend","rating":4.6,"reviews":156,"details":"Limelight designer suit with premium embellishments.","sizes":["XS","S","M","L","XL","XXL"],"colors":["Pink","Gold","Cream"],"category_idx":3,"featured":False},
]


def seed_database():
    """Insert categories + 40 products if tables are empty."""
    with Session(engine) as session:
        # Check if already seeded
        count = session.exec(select(func.count(Category.id))).one()
        if count > 0:
            return  # already seeded

        # Create categories
        cat_objects = []
        for c in SEED_CATEGORIES:
            cat = Category(name=c["name"], description=c["description"])
            session.add(cat)
            cat_objects.append(cat)
        session.commit()

        # Refresh to get IDs
        for c in cat_objects:
            session.refresh(c)
        cat_id_map = {i: cat_objects[i].id for i in range(len(cat_objects))}

        # Create products
        for p in SEED_PRODUCTS:
            product = Product(
                name=p["name"],
                description=p["description"],
                price=Decimal(p["price"]),
                original_price=Decimal(p["original_price"]) if p.get("original_price") else None,
                category_id=cat_id_map[p["category_idx"]],
                image_url=p.get("image_url"),
                material=p.get("material"),
                rating=p.get("rating"),
                reviews=p.get("reviews", 0),
                details=p.get("details"),
                sizes=json.dumps(p["sizes"]) if p.get("sizes") else None,
                colors=json.dumps(p["colors"]) if p.get("colors") else None,
                stock_quantity=100,
                is_active=True,
                featured=p.get("featured", False),
            )
            session.add(product)
        session.commit()


# ---------------------------------------------------------------------------
# APP ASSEMBLY
# ---------------------------------------------------------------------------
app = FastAPI(title="Fatima Zehra Boutique", description="Unified backend for Netlify deployment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(chat_router)


@app.get("/api/health")
async def health():
    # Check environment status
    env_status = {
        "database": "✓" if DATABASE_URL and len(DATABASE_URL) > 10 else "✗",
        "openai": "✓" if (os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY) and len(os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY) > 10 else "✗",
        "jwt_secret": "✓" if JWT_SECRET and len(JWT_SECRET) >= 32 else "✗",
    }
    return {
        "status": "ok",
        "environment": env_status
    }


# ---------------------------------------------------------------------------
# STARTUP: create tables + seed
# ---------------------------------------------------------------------------
# STARTUP: create tables + seed (with error handling for Vercel)
# ---------------------------------------------------------------------------
try:
    SQLModel.metadata.create_all(engine)
    seed_database()
except Exception as e:
    print(f"Warning: Could not initialize database at module load time: {e}")

# ---------------------------------------------------------------------------
# MANGUM HANDLER — entry point for Netlify Functions
# ---------------------------------------------------------------------------
handler = Mangum(app, lifespan="off")
