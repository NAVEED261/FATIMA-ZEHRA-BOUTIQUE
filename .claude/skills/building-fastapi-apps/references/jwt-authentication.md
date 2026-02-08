# JWT Authentication Complete Guide

## JWT Tokens Setup

```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-min-32-chars")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

bearer_scheme = HTTPBearer()

# Token creation
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

# Token verification
def verify_token(token: str) -> dict:
    """Verify and decode token"""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None

def verify_access_token(token: str) -> dict:
    """Verify access token specifically"""
    payload = verify_token(token)
    if not payload or payload.get("type") != "access":
        return None
    return payload

def verify_refresh_token(token: str) -> dict:
    """Verify refresh token specifically"""
    payload = verify_token(token)
    if not payload or payload.get("type") != "refresh":
        return None
    return payload
```

## Dependency Injection for Authentication

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import (
    bearer_scheme,
    verify_access_token,
    verify_refresh_token
)
from app.models.user import User
from app.schemas.user import UserResponse

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from token
    """
    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    return user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify admin status
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_optional_current_user(
    credentials: Optional[HTTPAuthCredentials] = Depends(bearer_scheme)
) -> Optional[User]:
    """
    Get current user if token provided, otherwise None
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    # This would need db access
    # For now, just return user_id
    return user_id
```

## Login & Token Endpoints

```python
# app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.user import UserResponse, UserCreate
from app.models.user import User
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

@router.post("/login", response_model=TokenResponse)
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(deps.get_db)
):
    """
    Login user and return access + refresh tokens
    """
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not user.check_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Check active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    # Create tokens
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id}
    )

    # Update last login
    user.update_last_login()
    db.add(user)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )

@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token_request: dict,  # {"refresh_token": "..."}
    db: Session = Depends(deps.get_db)
):
    """
    Refresh access token using refresh token
    """
    refresh_token = refresh_token_request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required"
        )

    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new access token
    new_access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Logout user (client should discard token)
    """
    return {"message": "Logged out successfully"}
```

## Token Revocation (Token Blacklist)

```python
# app/core/token_blacklist.py
from datetime import datetime, timedelta
from typing import Set

# In-memory blacklist (use Redis in production)
token_blacklist: Set[str] = set()

def add_token_to_blacklist(token: str, exp_time: datetime):
    """Add token to blacklist"""
    token_blacklist.add(token)

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    return token in token_blacklist

# Use in logout
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    credentials: HTTPAuthCredentials = Depends(bearer_scheme),
    current_user: User = Depends(deps.get_current_user)
):
    """Logout and blacklist token"""
    token = credentials.credentials
    payload = verify_access_token(token)

    if payload:
        exp_time = datetime.fromtimestamp(payload.get("exp"))
        add_token_to_blacklist(token, exp_time)

    return {"message": "Logged out successfully"}

# Check blacklist in dependency
async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials

    # Check blacklist
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    # ... rest of verification
```

## Protected Routes

```python
# app/api/endpoints/users.py
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(deps.get_current_user)
):
    """Get current user info"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Update current user"""
    user = db.query(User).filter(User.id == current_user.id).first()
    update_data = user_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# Admin only
@router.get("/admin/users", response_model=List[UserResponse])
async def list_all_users(
    current_user: User = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
):
    """List all users (admin only)"""
    users = db.query(User).all()
    return users
```

## Token Schemes

```python
# Alternative: Using Authorization header directly
from fastapi.security import HTTPBearer, HTTPAuthCredentialDetails

class JWTBearer(HTTPBearer):
    async def __call__(self, request):
        credentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403,
                    detail="Invalid authentication scheme."
                )
            if not verify_access_token(credentials.credentials):
                raise HTTPException(
                    status_code=403,
                    detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403,
                detail="Invalid authorization code."
            )

# Use in dependency
security = JWTBearer()

@router.get("/protected")
async def protected_route(token: str = Depends(security)):
    return {"token": token}
```

## Multi-tenant Authentication

```python
# Add tenant_id to token
def create_tenant_access_token(
    data: dict,
    tenant_id: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create token with tenant_id"""
    to_encode = data.copy()
    to_encode.update({"tenant_id": tenant_id})

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

# Verify tenant access
async def get_current_tenant_user(
    credentials: HTTPAuthCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")

    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```
