# Complete Pytest Testing for FastAPI

## Test Setup

### Installation

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
```

### Conftest Configuration

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_db
from app.models.base import Base

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture(scope="function")
def db():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db: Session):
    """Create test client with overridden DB dependency"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()
```

## Test Fixtures

### User Fixtures

```python
# tests/fixtures/user.py
import pytest
from app.models.user import User
from app.core.security import hash_password
from sqlalchemy.orm import Session

@pytest.fixture
def user(db: Session):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User"
    )
    user.set_password("TestPassword123!")
    user.is_active = True

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def admin_user(db: Session):
    """Create admin user"""
    user = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        is_admin=True
    )
    user.set_password("AdminPassword123!")
    user.is_active = True

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def token(user: User):
    """Create JWT token for user"""
    from app.core.security import create_access_token

    token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    return token

@pytest.fixture
def auth_headers(token: str):
    """Return Authorization headers"""
    return {"Authorization": f"Bearer {token}"}
```

## CRUD Operation Tests

### Create Tests

```python
# tests/api/test_users_create.py
import pytest
from fastapi import status

def test_create_user_success(client, db):
    """Test successful user creation"""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "password" not in data  # Password should not be returned

def test_create_user_duplicate_email(client, user):
    """Test duplicate email rejection"""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": user.email,
            "username": "different",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"]

@pytest.mark.parametrize("invalid_input,error_field", [
    ({"username": "user", "password": "pass"}, "email"),
    ({"email": "invalid", "password": "pass"}, "email"),
    ({"email": "user@example.com", "username": "u"}, "username"),
    ({"email": "user@example.com", "username": "user", "password": "short"}, "password"),
])
def test_create_user_validation(client, invalid_input):
    """Test input validation"""
    response = client.post("/api/v1/users/", json=invalid_input)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

### Read Tests

```python
# tests/api/test_users_read.py
def test_get_user_success(client, user):
    """Test getting user by ID"""
    response = client.get(f"/api/v1/users/{user.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == user.email

def test_get_user_not_found(client):
    """Test getting non-existent user"""
    response = client.get("/api/v1/users/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_users(client, db):
    """Test listing users"""
    # Create multiple users
    for i in range(5):
        from app.models.user import User
        user = User(email=f"user{i}@example.com", username=f"user{i}")
        user.set_password("password")
        db.add(user)
    db.commit()

    response = client.get("/api/v1/users/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 5

def test_list_users_pagination(client, db):
    """Test pagination"""
    # Create users
    for i in range(15):
        from app.models.user import User
        user = User(email=f"user{i}@example.com", username=f"user{i}")
        user.set_password("password")
        db.add(user)
    db.commit()

    # Get first page
    response = client.get("/api/v1/users/?skip=0&limit=10")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 10

    # Get second page
    response = client.get("/api/v1/users/?skip=10&limit=10")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 5

def test_list_users_filter(client, db):
    """Test filtering"""
    response = client.get("/api/v1/users/?is_active=true")
    assert response.status_code == status.HTTP_200_OK
```

### Update Tests

```python
# tests/api/test_users_update.py
def test_update_user_success(client, user, auth_headers):
    """Test updating user"""
    response = client.put(
        f"/api/v1/users/{user.id}",
        headers=auth_headers,
        json={"full_name": "Updated Name"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "Updated Name"

def test_update_user_unauthorized(client, user):
    """Test update without auth"""
    response = client.put(
        f"/api/v1/users/{user.id}",
        json={"full_name": "Updated Name"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_user_forbidden(client, user, db):
    """Test update by different user"""
    # Create another user and get their token
    from app.models.user import User
    other_user = User(email="other@example.com", username="other")
    other_user.set_password("password")
    db.add(other_user)
    db.commit()

    from app.core.security import create_access_token
    other_token = create_access_token(
        data={"sub": other_user.id, "email": other_user.email}
    )

    response = client.put(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"full_name": "Updated Name"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_partial_update_user(client, user, auth_headers):
    """Test PATCH partial update"""
    response = client.patch(
        f"/api/v1/users/{user.id}",
        headers=auth_headers,
        json={"full_name": "New Name"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == "New Name"
```

### Delete Tests

```python
# tests/api/test_users_delete.py
def test_delete_user_success(client, user, auth_headers, db):
    """Test deleting user"""
    response = client.delete(
        f"/api/v1/users/{user.id}",
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deleted
    from app.models.user import User
    deleted = db.query(User).filter(User.id == user.id).first()
    assert deleted is None

def test_delete_user_not_found(client, auth_headers):
    """Test deleting non-existent user"""
    response = client.delete(
        "/api/v1/users/9999",
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
```

## Authentication Tests

```python
# tests/api/test_auth.py
def test_login_success(client, user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "email": user.email,
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_refresh_token(client, user):
    """Test token refresh"""
    # Login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        data={"email": user.email, "password": "TestPassword123!"}
    )

    refresh_token = login_response.json()["refresh_token"]

    # Refresh
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
```

## Error Handling Tests

```python
# tests/api/test_errors.py
def test_validation_error_response(client):
    """Test validation error format"""
    response = client.post(
        "/api/v1/users/",
        json={"email": "invalid-email"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data

def test_not_found_response(client):
    """Test 404 error format"""
    response = client.get("/api/v1/users/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"

def test_unauthorized_response(client):
    """Test 401 error format"""
    response = client.get("/api/v1/users/protected")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

## Async Test Example

```python
# tests/test_async.py
import pytest

@pytest.mark.asyncio
async def test_async_endpoint(client):
    """Test async endpoint"""
    response = client.get("/api/v1/async-endpoint")
    assert response.status_code == 200
```

## Test Organization

```python
# tests/
# ├── __init__.py
# ├── conftest.py
# ├── fixtures/
# │   ├── __init__.py
# │   ├── user.py
# │   └── database.py
# ├── api/
# │   ├── __init__.py
# │   ├── test_users_create.py
# │   ├── test_users_read.py
# │   ├── test_users_update.py
# │   ├── test_users_delete.py
# │   └── test_auth.py
# ├── models/
# │   ├── __init__.py
# │   └── test_user_model.py
# └── test_main.py
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific file
pytest tests/api/test_users_create.py

# Run specific test
pytest tests/api/test_users_create.py::test_create_user_success

# Run with markers
pytest -m "slow"

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```
