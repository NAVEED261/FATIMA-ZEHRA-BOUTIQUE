"""Order Service Routes - Cart and Order Management"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlmodel import Session, select, func

from .models import (
    Cart, CartItem, Order, OrderItem,
    AddToCartRequest, UpdateCartItemRequest, CheckoutRequest,
    CartResponse, CartItemResponse, OrderResponse, OrderItemResponse
)
from .database import get_session

router = APIRouter(tags=["orders"])


def get_user_id_from_header(authorization: Optional[str] = Header(None)) -> int:
    """Extract user_id from JWT token header (simplified for demo)"""
    # In production, decode JWT token to get user_id
    # For now, we'll use a simple header
    if authorization:
        try:
            parts = authorization.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                # In production: decode JWT from parts[1]
                # For demo: extract from custom header
                return int(parts[1].split("-")[0]) if "-" in parts[1] else 1
        except Exception:
            pass
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authorization header"
    )


# Cart Endpoints
@router.get("/api/cart", response_model=CartResponse)
async def get_cart(
    user_id: int = Depends(get_user_id_from_header),
    session: Session = Depends(get_session)
):
    """Get user's shopping cart"""
    cart = session.exec(
        select(Cart).where(Cart.user_id == user_id)
    ).first()

    if not cart:
        # Create new cart if it doesn't exist
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)

    # Calculate total
    total = Decimal("0")
    for item in cart.items:
        total += item.price * item.quantity

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=[CartItemResponse.from_orm(item) for item in cart.items],
        total_amount=total,
        item_count=len(cart.items)
    )


@router.post("/api/cart/items", response_model=CartResponse)
async def add_to_cart(
    item_data: AddToCartRequest,
    user_id: int = Depends(get_user_id_from_header),
    session: Session = Depends(get_session)
):
    """Add item to cart"""
    # Get or create cart
    cart = session.exec(
        select(Cart).where(Cart.user_id == user_id)
    ).first()

    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)

    # Check if item already in cart
    existing_item = session.exec(
        select(CartItem).where(
            (CartItem.cart_id == cart.id) &
            (CartItem.product_id == item_data.product_id)
        )
    ).first()

    if existing_item:
        # Update quantity
        existing_item.quantity += item_data.quantity
        session.add(existing_item)
    else:
        # Add new item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=item_data.price
        )
        session.add(cart_item)

    cart.updated_at = datetime.utcnow()
    session.add(cart)
    session.commit()
    session.refresh(cart)

    # Return updated cart
    total = Decimal("0")
    for item in cart.items:
        total += item.price * item.quantity

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=[CartItemResponse.from_orm(item) for item in cart.items],
        total_amount=total,
        item_count=len(cart.items)
    )


@router.put("/api/cart/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: int,
    update_data: UpdateCartItemRequest,
    user_id: int = Depends(get_user_id_from_header),
    session: Session = Depends(get_session)
):
    """Update cart item quantity"""
    cart_item = session.exec(
        select(CartItem).where(CartItem.id == item_id)
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    # Verify user owns this cart
    cart = session.exec(
        select(Cart).where(Cart.id == cart_item.cart_id)
    ).first()

    if cart.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    cart_item.quantity = update_data.quantity
    session.add(cart_item)

    cart.updated_at = datetime.utcnow()
    session.add(cart)
    session.commit()
    session.refresh(cart)

    total = Decimal("0")
    for item in cart.items:
        total += item.price * item.quantity

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=[CartItemResponse.from_orm(item) for item in cart.items],
        total_amount=total,
        item_count=len(cart.items)
    )


@router.delete("/api/cart/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    user_id: int = Depends(get_user_id_from_header),
    session: Session = Depends(get_session)
):
    """Remove item from cart"""
    cart_item = session.exec(
        select(CartItem).where(CartItem.id == item_id)
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    # Verify user owns this cart
    cart = session.exec(
        select(Cart).where(Cart.id == cart_item.cart_id)
    ).first()

    if cart.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    session.delete(cart_item)
    cart.updated_at = datetime.utcnow()
    session.add(cart)
    session.commit()


@router.delete("/api/cart", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    user_id: int = Depends(get_user_id_from_header),
    session: Session = Depends(get_session)
):
    """Clear entire cart"""
    cart = session.exec(
        select(Cart).where(Cart.user_id == user_id)
    ).first()

    if cart:
        # Delete all items
        for item in cart.items:
            session.delete(item)
        cart.updated_at = datetime.utcnow()
        session.add(cart)
        session.commit()


# Order Endpoints
@router.post("/api/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def checkout(
    checkout_data: CheckoutRequest,
    user_id: int = Depends(get_user_id_from_header),
    session: Session = Depends(get_session)
):
    """Create order from cart"""
    # Get cart
    cart = session.exec(
        select(Cart).where(Cart.user_id == user_id)
    ).first()

    if not cart or len(cart.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    # Calculate total
    total_amount = Decimal("0")
    for item in cart.items:
        total_amount += item.price * item.quantity

    # Create order
    order = Order(
        user_id=user_id,
        status="pending",
        total_amount=total_amount,
        shipping_address=checkout_data.shipping_address,
        payment_status="pending"
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    # Create order items
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            product_name=f"Product {cart_item.product_id}",
            quantity=cart_item.quantity,
            price=cart_item.price
        )
        session.add(order_item)

    # Clear cart
    for item in cart.items:
        session.delete(item)

    session.commit()
    session.refresh(order)

    return OrderResponse.from_orm(order)


@router.get("/api/orders", response_model=list[OrderResponse])
async def list_orders(
    user_id: int = Depends(get_user_id_from_header),
    session: Session = Depends(get_session)
):
    """Get user's orders"""
    orders = session.exec(
        select(Order).where(Order.user_id == user_id)
    ).all()

    return [OrderResponse.from_orm(order) for order in orders]


@router.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    user_id: int = Depends(get_user_id_from_header),
    session: Session = Depends(get_session)
):
    """Get order details"""
    order = session.exec(
        select(Order).where(Order.id == order_id)
    ).first()

    if not order or order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return OrderResponse.from_orm(order)
