# Complete CRUD Operations in FastAPI

## Overview

Full CRUD (Create, Read, Update, Delete) patterns with SQLAlchemy ORM, Pydantic validation, and best practices.

## 1. CREATE Operations

### Basic Create

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import user as schemas
from app.models.user import User as UserModel
from app.crud import user as crud_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Create new user with validation
    """
    # Check if user exists
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = crud_user.create_user(db, obj_in=user_in)
    return user
```

### Create with Relationships

```python
@router.post("/with-profile/", response_model=schemas.UserWithProfile)
async def create_user_with_profile(
    user_data: schemas.UserWithProfileCreate,
    db: Session = Depends(deps.get_db)
):
    """Create user with profile in transaction"""
    try:
        # Create user
        user = UserModel(
            email=user_data.email,
            username=user_data.username
        )
        db.add(user)
        db.flush()  # Get ID without commit

        # Create associated profile
        profile = ProfileModel(
            user_id=user.id,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        db.add(profile)
        db.commit()
        db.refresh(user)

        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

### Bulk Create

```python
@router.post("/bulk/", response_model=List[schemas.UserResponse])
async def create_multiple_users(
    users_in: List[schemas.UserCreate],
    db: Session = Depends(deps.get_db)
):
    """Create multiple users in batch"""
    created_users = []
    try:
        for user_in in users_in:
            user = UserModel(**user_in.dict())
            db.add(user)
            created_users.append(user)

        db.commit()
        for user in created_users:
            db.refresh(user)

        return created_users
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bulk creation failed"
        )
```

## 2. READ Operations

### Read Single Record

```python
@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(deps.get_db)
):
    """Get user by ID"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
```

### Read with Filtering

```python
@router.get("/", response_model=List[schemas.UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(deps.get_db)
):
    """List users with optional filtering"""
    query = db.query(UserModel)

    # Apply filters
    if email:
        query = query.filter(UserModel.email.contains(email))
    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)

    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    return users
```

### Read with Pagination

```python
from pydantic import BaseModel

class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[schemas.UserResponse]

@router.get("/paginated/", response_model=PaginatedResponse)
async def list_users_paginated(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(deps.get_db)
):
    """Get paginated users"""
    total = db.query(UserModel).count()
    users = db.query(UserModel).offset(skip).limit(limit).all()

    return PaginatedResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=users
    )
```

### Read with Sorting

```python
@router.get("/sorted/", response_model=List[schemas.UserResponse])
async def list_users_sorted(
    sort_by: str = Query("created_at", regex="^(created_at|email|username)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(deps.get_db)
):
    """Get users sorted"""
    column = getattr(UserModel, sort_by)

    if order == "desc":
        query = db.query(UserModel).order_by(column.desc())
    else:
        query = db.query(UserModel).order_by(column.asc())

    return query.all()
```

## 3. UPDATE Operations

### Full Update

```python
@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: schemas.UserResponse = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Update entire user"""
    # Authorization check
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    # Get user
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    update_data = user_in.dict(exclude_unset=False)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
```

### Partial Update (PATCH)

```python
@router.patch("/{user_id}", response_model=schemas.UserResponse)
async def partial_update_user(
    user_id: int,
    user_in: schemas.UserPartialUpdate,  # All fields optional
    current_user: schemas.UserResponse = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Update only provided fields"""
    # Authorization
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only update fields that were provided
    update_data = user_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
```

## 4. DELETE Operations

### Simple Delete

```python
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: schemas.UserResponse = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Delete user"""
    # Authorization
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
```

### Soft Delete

```python
@router.delete("/{user_id}/soft", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_user(
    user_id: int,
    current_user: schemas.UserResponse = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Soft delete (mark as inactive)"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    user.deleted_at = datetime.utcnow()

    db.add(user)
    db.commit()
```

## CRUD Helper Functions

```python
# app/crud/user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, obj_in: UserCreate):
    db_obj = User(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_user(db: Session, db_obj: User, obj_in: UserUpdate):
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_user(db: Session, user_id: int):
    db_obj = db.query(User).filter(User.id == user_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
```

## Error Handling for CRUD

```python
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

@router.post("/", response_model=schemas.UserResponse)
async def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db)
):
    """Create user with proper error handling"""
    try:
        user = UserModel(**user_in.dict())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate entry (email already exists)"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```
