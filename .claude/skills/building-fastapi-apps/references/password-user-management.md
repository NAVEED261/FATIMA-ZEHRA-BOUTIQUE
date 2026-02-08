# Password Hashing & User Management

## Password Hashing with Bcrypt

### Setup

```bash
pip install bcrypt passlib[bcrypt] python-jose[cryptography]
```

### Password Utils

```python
# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

# Password validation
def validate_password(password: str) -> bool:
    """
    Validate password strength
    - Min 8 characters
    - At least 1 uppercase
    - At least 1 lowercase
    - At least 1 digit
    - At least 1 special character
    """
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False
    return True
```

## User Management Schemas

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def validate_password_strength(cls, v):
        if not validate_password(v):
            raise ValueError('Password does not meet complexity requirements')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)

    @validator('password', pre=True, always=True)
    def validate_password_on_update(cls, v):
        if v and not validate_password(v):
            raise ValueError('Password does not meet complexity requirements')
        return v

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True
```

## User Model with Password

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def set_password(self, password: str):
        """Set hashed password"""
        from app.core.security import hash_password
        self.hashed_password = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        from app.core.security import verify_password
        return verify_password(password, self.hashed_password)

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
```

## User Registration Endpoint

```python
# app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import user as schemas
from app.models.user import User
from app.core.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Register new user
    """
    # Check if email exists
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username exists
    db_user = db.query(User).filter(User.username == user_in.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name
    )
    user.set_password(user_in.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
```

## User Login Endpoint

```python
@router.post("/login", response_model=dict)
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(deps.get_db)
):
    """
    Login user and return JWT token
    """
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Check password
    if not user.check_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Check if active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    # Update last login
    user.update_last_login()
    db.add(user)
    db.commit()

    # Generate token
    from app.core.security import create_access_token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
```

## Change Password Endpoint

```python
from app.schemas.user import PasswordChange

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_in: PasswordChange,
    current_user: schemas.UserResponse = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Change user password"""
    user = db.query(User).filter(User.id == current_user.id).first()

    # Verify current password
    if not user.check_password(password_in.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Set new password
    user.set_password(password_in.new_password)
    db.add(user)
    db.commit()

    return {"message": "Password changed successfully"}
```

## Password Reset Flow

```python
# Request password reset
@router.post("/forgot-password")
async def forgot_password(
    email: str,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks
):
    """Request password reset"""
    user = db.query(User).filter(User.email == email).first()

    if user:
        # Generate reset token
        from app.core.security import create_access_token
        reset_token = create_access_token(
            data={"sub": user.id, "type": "reset"},
            expires_delta=timedelta(hours=1)
        )

        # Send email in background
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            reset_token
        )

    # Always return success (security)
    return {"message": "If email exists, reset link sent"}

# Reset password with token
from pydantic import BaseModel

class PasswordReset(BaseModel):
    token: str
    new_password: str

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(deps.get_db)
):
    """Reset password with token"""
    try:
        # Verify token
        from app.core.security import verify_token
        payload = verify_token(reset_data.token)

        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Invalid token")

        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update password
        user.set_password(reset_data.new_password)
        db.add(user)
        db.commit()

        return {"message": "Password reset successfully"}

    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
```

## User Profile Update

```python
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    profile_picture_url: Optional[str] = None

@router.put("/profile", response_model=schemas.UserResponse)
async def update_profile(
    profile_in: UserProfileUpdate,
    current_user: schemas.UserResponse = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Update user profile"""
    user = db.query(User).filter(User.id == current_user.id).first()

    update_data = profile_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
```

## User Deletion with Password Confirmation

```python
class DeleteAccountRequest(BaseModel):
    password: str

@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    delete_request: DeleteAccountRequest,
    current_user: schemas.UserResponse = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Delete user account with password confirmation"""
    user = db.query(User).filter(User.id == current_user.id).first()

    # Verify password
    if not user.check_password(delete_request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect"
        )

    # Delete user
    db.delete(user)
    db.commit()
```
