# Fatima Zehra Boutique - Implementation Tasks

**Project**: Fatima Zehra Boutique - Cloud-Native E-Commerce Platform
**Date**: 2026-01-26
**Status**: Planning Phase
**Organized by**: Phase and Component

---

## Phase 1: Foundation (Week 1)

### Task 1.1: Create Project Documentation
**Status**: Pending
**Depends on**: None
**Owner**: TBD

**Description**:
Create project documentation structure.

**Tasks**:
1. [ ] Create CONSTITUTION.md (project standards) ✅
2. [ ] Create specs/spec.md (user stories) ✅
3. [ ] Create specs/plan.md (architecture plan) ✅
4. [ ] Create .env.example files
5. [ ] Create README.md with quick start

**Acceptance Criteria**:
- [ ] All documents created in correct location
- [ ] Markdown formatting correct
- [ ] Links between documents work
- [ ] README has quick start instructions

**Estimated Effort**: 4 hours

---

### Task 1.2: Setup Neon PostgreSQL Database
**Status**: Pending
**Depends on**: None
**Owner**: TBD
**Skill**: `neon-postgres-setup`

**Description**:
Setup Neon PostgreSQL cloud database and run migrations.

**Steps**:
1. [ ] Create Neon project (free tier)
2. [ ] Create database `fatima_zehra_boutique`
3. [ ] Create database user with password
4. [ ] Generate connection string
5. [ ] Run database migrations (SQL files)
6. [ ] Create indexes for performance
7. [ ] Verify connection from localhost
8. [ ] Store connection string in .env

**Database Tables to Create**:
1. users (user_id, email, password_hash, full_name, phone, address, created_at, updated_at)
2. categories (id, name, description, image_url)
3. products (id, name, description, price, category_id, image_url, stock_quantity, featured, created_at, updated_at)
4. carts (id, user_id, created_at, updated_at)
5. cart_items (id, cart_id, product_id, quantity, price)
6. orders (id, user_id, status, total_amount, shipping_address, payment_status, created_at, updated_at)
7. order_items (id, order_id, product_id, product_name, quantity, price)
8. chat_messages (id, user_id, session_id, role, content, metadata, created_at)

**SQL Migration Files**:
- database/migrations/001_create_users.sql
- database/migrations/002_create_categories.sql
- database/migrations/003_create_products.sql
- database/migrations/004_create_carts.sql
- database/migrations/005_create_orders.sql
- database/migrations/006_create_chat_messages.sql
- database/migrations/007_create_indexes.sql

**Acceptance Criteria**:
- [ ] Neon project created
- [ ] All tables exist in database
- [ ] Indexes created for performance
- [ ] Connection string works from localhost
- [ ] Connection string works from Netlify Functions (tested later)
- [ ] Sample data seeded (optional)

**Estimated Effort**: 3 hours

---

### Task 1.3: Setup Docker Compose for Local Development
**Status**: Pending
**Depends on**: Task 1.2 (Neon setup)
**Owner**: TBD
**Skill**: `containerizing-applications`

**Description**:
Create Docker Compose configuration for local development with all services.

**Files to Create**:
1. docker/docker-compose.yml
2. docker/Dockerfile.backend
3. docker/Dockerfile.frontend
4. docker/.env.example
5. scripts/setup-local.sh

**Services**:
1. **user-service** (FastAPI, port 8001)
   - Image: Python 3.11
   - Build: docker/Dockerfile.backend
   - Volumes: backend/user-service:/app
   - Env: NEON_DATABASE_URL

2. **product-service** (FastAPI, port 8002)
   - Image: Python 3.11
   - Build: docker/Dockerfile.backend
   - Volumes: backend/product-service:/app
   - Env: NEON_DATABASE_URL

3. **order-service** (FastAPI, port 8003)
   - Image: Python 3.11
   - Build: docker/Dockerfile.backend
   - Volumes: backend/order-service:/app
   - Env: NEON_DATABASE_URL

4. **frontend** (Next.js, port 3000)
   - Image: Node 20
   - Build: docker/Dockerfile.frontend
   - Volumes: frontend:/app
   - Env: NEXT_PUBLIC_API_URL=http://localhost:8001

**Docker Configuration**:
```yaml
version: '3.8'
services:
  user-service:
    build:
      context: ..
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8001:8000"
    env_file: .env
    environment:
      - SERVICE_NAME=user-service
    volumes:
      - ../backend/user-service:/app

  product-service:
    build:
      context: ..
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8002:8000"
    env_file: .env
    environment:
      - SERVICE_NAME=product-service
    volumes:
      - ../backend/product-service:/app

  order-service:
    build:
      context: ..
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8003:8000"
    env_file: .env
    environment:
      - SERVICE_NAME=order-service
    volumes:
      - ../backend/order-service:/app

  frontend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8001
    volumes:
      - ../frontend:/app
    env_file: .env
```

**Acceptance Criteria**:
- [ ] docker-compose up -d succeeds
- [ ] All 4 services start successfully
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend services accessible at http://localhost:8001/docs, etc.
- [ ] Services can communicate with each other
- [ ] Services can connect to Neon database
- [ ] Logs viewable with docker-compose logs

**Estimated Effort**: 4 hours

---

### Task 1.4: Create Backend Directory Structure
**Status**: Pending
**Depends on**: Task 1.3
**Owner**: TBD

**Description**:
Create directory structure for all 3 backend microservices.

**Directory Structure**:
```
backend/
├── user-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── models.py            # SQLModel User model
│   │   ├── routes.py            # /api/users/* endpoints
│   │   ├── auth.py              # JWT, password hashing
│   │   ├── database.py          # Neon connection
│   │   └── dependencies.py      # get_current_user()
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_routes.py
│   │   └── conftest.py          # pytest fixtures
│   ├── requirements.txt
│   ├── netlify_handler.py       # Mangum wrapper
│   └── .env.example
│
├── product-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py            # Product, Category models
│   │   ├── routes.py            # /api/products/* endpoints
│   │   ├── database.py
│   │   └── dependencies.py
│   ├── tests/
│   │   ├── test_routes.py
│   │   └── conftest.py
│   ├── requirements.txt
│   ├── netlify_handler.py
│   └── .env.example
│
└── order-service/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── models.py            # Cart, Order models
    │   ├── routes.py            # /api/cart/*, /api/orders/* endpoints
    │   ├── database.py
    │   └── dependencies.py
    ├── tests/
    │   ├── test_routes.py
    │   └── conftest.py
    ├── requirements.txt
    ├── netlify_handler.py
    └── .env.example
```

**Acceptance Criteria**:
- [ ] All directories created
- [ ] __init__.py files present
- [ ] All .py files have skeleton structure
- [ ] requirements.txt files created
- [ ] .env.example files created

**Estimated Effort**: 1 hour

---

### Task 1.5: Create Frontend Directory Structure
**Status**: Pending
**Depends on**: Task 1.4
**Owner**: TBD
**Skill**: `building-nextjs-apps`

**Description**:
Create Next.js 16 project structure with App Router.

**Directory Structure**:
```
frontend/
├── app/
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Homepage
│   ├── globals.css              # Tailwind + global styles
│   ├── products/
│   │   ├── page.tsx             # Product listing
│   │   └── [id]/
│   │       └── page.tsx         # Product detail
│   ├── cart/page.tsx
│   ├── checkout/page.tsx
│   ├── orders/page.tsx
│   ├── auth/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   └── dashboard/page.tsx       # User dashboard
│
├── components/
│   ├── ui/                      # Shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── form.tsx
│   │   └── ...
│   ├── Navbar.tsx
│   ├── Footer.tsx
│   ├── Hero.tsx                 # Homepage hero
│   ├── ProductCard.tsx
│   ├── CartSummary.tsx
│   ├── ChatWidget.tsx           # AI chat
│   └── ...
│
├── lib/
│   ├── api.ts                   # API client
│   ├── auth.ts                  # JWT, token management
│   ├── utils.ts
│   └── types.ts                 # TypeScript types
│
├── public/
│   ├── images/
│   │   ├── logo.png
│   │   ├── hero-bg.jpg
│   │   └── products/            # Product images (generated later)
│   └── favicon.ico
│
├── styles/
│   └── globals.css
│
├── next.config.js               # output: 'export'
├── tailwind.config.js           # Design tokens
├── package.json
├── .env.local.example
├── tsconfig.json
└── .eslintrc.json
```

**Acceptance Criteria**:
- [ ] Next.js 16 project structure created
- [ ] All directories present
- [ ] Tailwind CSS configured
- [ ] Shadcn/ui setup ready
- [ ] TypeScript configured
- [ ] .env.example created

**Estimated Effort**: 2 hours

---

### Task 1.6: Create Netlify Functions Directory
**Status**: Pending
**Depends on**: None
**Owner**: TBD

**Description**:
Create Netlify Functions directory structure with Mangum wrappers.

**Directory Structure**:
```
netlify/
├── functions/
│   ├── user-service.py         # Mangum wrapper for user-service
│   ├── product-service.py      # Mangum wrapper for product-service
│   ├── order-service.py        # Mangum wrapper for order-service
│   ├── chat-service.py         # OpenAI chat handler
│   └── requirements.txt        # Python dependencies for functions
│
└── netlify.toml                # Netlify configuration
```

**netlify.toml Configuration**:
```toml
[build]
  command = "echo 'Functions deployed'"
  publish = "."

[functions]
  directory = "netlify/functions"
  node_bundler = "esbuild"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[build.environment]
  PYTHON_VERSION = "3.11"
```

**Acceptance Criteria**:
- [ ] netlify/functions/ directory created
- [ ] All handler files present
- [ ] netlify.toml configured
- [ ] requirements.txt created

**Estimated Effort**: 1 hour

---

## Phase 2: Backend Microservices (Weeks 2-3)

### Task 2.1: Implement User Service - Models & Database
**Status**: Pending
**Depends on**: Task 1.2, 1.4
**Owner**: TBD
**Skill**: `building-fastapi-apps`, `database-integration-patterns`

**Description**:
Create SQLModel User model and database connection for user-service.

**Files to Create/Modify**:
1. backend/user-service/app/models.py
2. backend/user-service/app/database.py
3. backend/user-service/app/dependencies.py

**Models**:
```python
# User Model (SQLModel)
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic models for API
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime
```

**Database Connection**:
```python
# database.py
DATABASE_URL = os.getenv("NEON_DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)
```

**Acceptance Criteria**:
- [ ] SQLModel User model defined
- [ ] Pydantic request/response models defined
- [ ] Database connection working
- [ ] init_db() creates tables
- [ ] Connection pooling configured
- [ ] Tests for models (pytest)

**Estimated Effort**: 3 hours

---

### Task 2.2: Implement User Service - Authentication (JWT)
**Status**: Pending
**Depends on**: Task 2.1
**Owner**: TBD
**Skill**: `building-fastapi-apps`

**Description**:
Implement JWT authentication, password hashing, and token management.

**Files to Create**:
1. backend/user-service/app/auth.py

**Functions to Implement**:
```python
# Password hashing
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# JWT tokens
def create_access_token(data: dict) -> str:
    # Create JWT token with 24h expiration

def verify_access_token(token: str) -> dict:
    # Verify and decode JWT token
    # Raise HTTPException(401) if invalid

# Current user dependency
async def get_current_user(token: str = Depends(HTTPBearer())) -> User:
    # Extract user from token
```

**Acceptance Criteria**:
- [ ] Password hashing working (bcrypt)
- [ ] JWT creation working (24h expiration)
- [ ] JWT verification working
- [ ] get_current_user() dependency working
- [ ] Tests for auth functions (pytest)
- [ ] No hardcoded secrets (use env var JWT_SECRET)

**Estimated Effort**: 3 hours

---

### Task 2.3: Implement User Service - API Endpoints
**Status**: Pending
**Depends on**: Task 2.2
**Owner**: TBD
**Skill**: `building-fastapi-apps`

**Description**:
Implement /api/users/* endpoints (register, login, get profile, update profile).

**Endpoints to Implement**:

1. **POST /api/users/register**
   - Input: UserCreate
   - Validation: Email not used, password strong
   - Response: UserResponse + token
   - Error: 400 if email exists, 422 if invalid

2. **POST /api/users/login**
   - Input: UserLogin
   - Validation: Email exists, password matches
   - Response: {token, user: UserResponse}
   - Error: 401 if credentials invalid

3. **GET /api/users/me**
   - Auth: Bearer token required
   - Response: UserResponse
   - Error: 401 if not authenticated

4. **PUT /api/users/me**
   - Auth: Bearer token required
   - Input: {full_name, phone, address}
   - Response: UserResponse
   - Error: 401, 422

**File to Modify**:
- backend/user-service/app/main.py (Flask-like structure)
- backend/user-service/app/routes.py (Clean separation)

**Acceptance Criteria**:
- [ ] All 4 endpoints implemented
- [ ] Input validation working
- [ ] Error messages clear
- [ ] JWT auth protecting protected endpoints
- [ ] API responses consistent (success/error format)
- [ ] Integration tests passing
- [ ] CORS headers configured

**Estimated Effort**: 4 hours

---

### Task 2.4: Implement User Service - Mangum Wrapper for Netlify
**Status**: Pending
**Depends on**: Task 2.3
**Owner**: TBD

**Description**:
Create Mangum wrapper for FastAPI app to run on Netlify Functions.

**File to Create**:
- backend/user-service/netlify_handler.py

**Content**:
```python
from mangum import Mangum
import sys
sys.path.append('.')

from app.main import app

handler = Mangum(app, lifespan="off")
```

**Netlify Function Wrapper**:
- netlify/functions/user-service.py calls netlify_handler.py

**Acceptance Criteria**:
- [ ] Mangum wrapper created
- [ ] Handler properly wraps FastAPI app
- [ ] Netlify function can call handler
- [ ] Environment variables passed through

**Estimated Effort**: 1 hour

---

### Task 2.5: Implement User Service - Testing
**Status**: Pending
**Depends on**: Task 2.4
**Owner**: TBD
**Skill**: `testing-with-pytest`

**Description**:
Create unit and integration tests for user service.

**Test Files to Create**:
- backend/user-service/tests/conftest.py (pytest fixtures)
- backend/user-service/tests/test_models.py
- backend/user-service/tests/test_auth.py
- backend/user-service/tests/test_routes.py

**Tests to Cover**:
1. **Models**:
   - User model creation
   - User validation (email, password)

2. **Auth**:
   - Password hashing (bcrypt)
   - JWT token creation/verification
   - Token expiration

3. **Routes**:
   - POST /api/users/register (success, email exists, weak password)
   - POST /api/users/login (success, invalid credentials)
   - GET /api/users/me (success, no auth)
   - PUT /api/users/me (success, no auth)

4. **Integration**:
   - Register → Login → Get profile flow
   - Database persistence

**Acceptance Criteria**:
- [ ] 80%+ code coverage
- [ ] All critical paths tested
- [ ] Edge cases covered (empty email, SQL injection attempt)
- [ ] All tests passing
- [ ] No hardcoded test data (use fixtures)

**Estimated Effort**: 4 hours

---

### Task 2.6: Implement Product Service (Similar to User Service)
**Status**: Pending
**Depends on**: Task 2.1-2.5
**Owner**: TBD
**Skill**: `building-fastapi-apps`

**Description**:
Implement Product and Category models, database connection, and API endpoints.

**Models**:
```python
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str]
    image_url: Optional[str]

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str]
    price: Decimal
    category_id: int = Field(foreign_key="category.id")
    image_url: Optional[str]
    stock_quantity: int = Field(default=0)
    is_active: bool = Field(default=True)
    featured: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Endpoints**:
- GET /api/products (with filters: category, search, featured, pagination)
- GET /api/products/:id
- POST /api/products (admin only, Phase 2)
- GET /api/categories
- POST /api/categories (admin only, Phase 2)

**Acceptance Criteria**:
- [ ] All models defined
- [ ] All endpoints implemented
- [ ] Filtering/search working
- [ ] Pagination working (limit, offset)
- [ ] 80%+ test coverage
- [ ] Mangum wrapper created
- [ ] No auth required for GET endpoints

**Estimated Effort**: 6 hours

---

### Task 2.7: Implement Order Service (Cart & Orders)
**Status**: Pending
**Depends on**: Task 2.1-2.5
**Owner**: TBD
**Skill**: `building-fastapi-apps`

**Description**:
Implement Cart, Order models and endpoints for shopping cart and order management.

**Models**:
```python
class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CartItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="cart.id")
    product_id: int
    quantity: int
    price: Decimal

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    status: str = Field(default="pending")  # pending, confirmed, shipped, delivered
    total_amount: Decimal
    shipping_address: str
    payment_status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int
    product_name: str
    quantity: int
    price: Decimal
```

**Endpoints**:
- GET /api/cart (get current user's cart)
- POST /api/cart/items (add item to cart)
- PUT /api/cart/items/:id (update item quantity)
- DELETE /api/cart/items/:id (remove item from cart)
- POST /api/checkout (create order from cart)
- GET /api/orders (list user's orders)
- GET /api/orders/:id (get order details)

**Acceptance Criteria**:
- [ ] All models defined
- [ ] All endpoints implemented
- [ ] Cart persistence working
- [ ] Checkout creates orders
- [ ] Stock validation
- [ ] Auth required for protected endpoints
- [ ] 80%+ test coverage

**Estimated Effort**: 8 hours

---

## Phase 3: Frontend Development (Weeks 4-5)

### Task 3.1: Setup Next.js Project
**Status**: Pending
**Depends on**: Task 1.5
**Owner**: TBD
**Skill**: `building-nextjs-apps`

**Description**:
Initialize Next.js 16 project with Tailwind CSS, Shadcn/ui, and configuration.

**Steps**:
1. [ ] Create next.config.js with `output: 'export'`
2. [ ] Setup Tailwind CSS
3. [ ] Setup Shadcn/ui
4. [ ] Configure TypeScript
5. [ ] Setup ESLint and Prettier
6. [ ] Create design system (colors, fonts)
7. [ ] Setup environment variables

**Acceptance Criteria**:
- [ ] `npm run dev` starts development server
- [ ] `npm run build` successfully builds static site
- [ ] Tailwind CSS working
- [ ] Shadcn/ui components available
- [ ] TypeScript strict mode
- [ ] ESLint passing

**Estimated Effort**: 3 hours

---

### Task 3.2: Implement API Client Library
**Status**: Pending
**Depends on**: Task 3.1
**Owner**: TBD

**Description**:
Create TypeScript API client for calling backend services.

**File to Create**:
- frontend/lib/api.ts

**Features**:
```typescript
// Base API client with:
// - Automatic Bearer token injection
// - Error handling
// - Request retry (3x with exponential backoff)
// - Type-safe responses
// - Environment variable API_URL

class APIClient {
  async fetch<T>(endpoint: string, options?: RequestInit): Promise<T>
  async get<T>(endpoint: string): Promise<T>
  async post<T>(endpoint: string, body: any): Promise<T>
  async put<T>(endpoint: string, body: any): Promise<T>
  async delete<T>(endpoint: string): Promise<T>
}

// User API
export const userAPI = {
  register(email, password, fullName): Promise<{token, user}>,
  login(email, password): Promise<{token, user}>,
  getProfile(): Promise<User>,
  updateProfile(data): Promise<User>
}

// Product API
export const productAPI = {
  getAll(filters): Promise<{products, total}>,
  getById(id): Promise<Product>,
  getCategories(): Promise<Category[]>
}

// Order API
export const orderAPI = {
  getCart(): Promise<Cart>,
  addToCart(productId, quantity): Promise<Cart>,
  removeFromCart(itemId): Promise<Cart>,
  checkout(address): Promise<Order>,
  getOrders(): Promise<Order[]>,
  getOrderById(id): Promise<Order>
}

// Chat API
export const chatAPI = {
  sendMessage(text, sessionId): Promise<Stream>,
  getChatHistory(sessionId): Promise<Message[]>
}
```

**Acceptance Criteria**:
- [ ] All API methods implemented
- [ ] Type-safe responses
- [ ] Error handling working
- [ ] Bearer token injection automatic
- [ ] Retry logic working
- [ ] Unit tests for API client

**Estimated Effort**: 3 hours

---

### Task 3.3: Implement Authentication Context
**Status**: Pending
**Depends on**: Task 3.2
**Owner**: TBD

**Description**:
Create React Context for authentication state management.

**File to Create**:
- frontend/lib/auth.ts or contexts/AuthContext.tsx

**Features**:
```typescript
// Auth Context should provide:
// - user: User | null
// - isLoading: boolean
// - login(email, password): Promise<void>
// - register(email, password, fullName): Promise<void>
// - logout(): void
// - isAuthenticated: boolean

// Token management:
// - Store JWT in localStorage
// - Inject in API requests
// - Auto-refresh on token expiration (if needed)
// - Clear on logout
```

**Protected Route Component**:
```typescript
export function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return <Loading />
  if (!isAuthenticated) return <redirect to="/auth/login" />

  return children
}
```

**Acceptance Criteria**:
- [ ] Auth context created
- [ ] Token stored/retrieved from localStorage
- [ ] Login/register working
- [ ] Logout clearing token
- [ ] Protected routes working
- [ ] useAuth() hook available
- [ ] Tests for auth context

**Estimated Effort**: 3 hours

---

### Task 3.4: Implement Homepage
**Status**: Pending
**Depends on**: Task 3.3
**Owner**: TBD
**Skill**: `styling-with-shadcn`

**Description**:
Create beautiful homepage with hero section and featured products.

**Components**:
1. **Hero Section** (Hero.tsx):
   - Large background image
   - Centered title: "Fatima Zehra Boutique"
   - Subtitle: "Elegant Fashion for Every Occasion"
   - CTA button: "Shop Now"
   - Dark overlay with transparency

2. **Featured Products Section**:
   - Heading: "Featured Collections"
   - Grid of 4-6 featured products
   - Product cards with images, name, price
   - "Shop Collection" button

3. **Categories Section**:
   - Heading: "Browse by Category"
   - 4 category cards (Dresses, Tops, Skirts, Accessories)
   - Category images
   - Link to category page

4. **Newsletter Section**:
   - Email subscription form
   - "Stay Updated" CTA

**File to Create**:
- app/page.tsx (homepage)
- components/Hero.tsx
- components/FeaturedProducts.tsx
- components/Categories.tsx

**Acceptance Criteria**:
- [ ] Homepage loads
- [ ] Hero section looks elegant
- [ ] Featured products load from API
- [ ] Responsive on all devices
- [ ] Mobile-first design
- [ ] No console errors

**Estimated Effort**: 4 hours

---

### Task 3.5: Implement Navbar & Footer
**Status**: Pending
**Depends on**: Task 3.1
**Owner**: TBD

**Description**:
Create responsive navbar and footer with branding.

**Navbar** (components/Navbar.tsx):
- Logo: "Fatima Zehra Boutique" (text or image)
- Menu: Home, Products, About, Contact
- Cart icon with item count
- User dropdown (Login / Profile / Logout)
- Mobile hamburger menu
- Sticky navigation

**Footer** (components/Footer.tsx):
- Links: About, Contact, Privacy, Terms
- Social media icons (Instagram, Facebook, TikTok)
- Newsletter subscription
- Copyright: "© 2026 Fatima Zehra Boutique"
- Responsive grid layout

**Acceptance Criteria**:
- [ ] Navbar visible on all pages
- [ ] Footer visible on all pages
- [ ] Logo/branding consistent
- [ ] Mobile menu working
- [ ] User dropdown working
- [ ] Cart count updating
- [ ] Responsive design

**Estimated Effort**: 3 hours

---

### Task 3.6: Implement Product Listing & Detail Pages
**Status**: Pending
**Depends on**: Task 3.5
**Owner**: TBD

**Description**:
Create product listing page with filters and product detail page.

**Product Listing** (app/products/page.tsx):
- Grid of all products (responsive: 1 col mobile, 3 desktop)
- Filters: Category dropdown, search bar
- Pagination or infinite scroll (20 per page)
- Loading state
- Empty state

**Product Detail** (app/products/[id]/page.tsx):
- Large product image
- Product name, price, description
- Stock status
- Add to Cart button with quantity selector
- Related products (3-4)
- Breadcrumbs
- Responsive layout

**File to Create**:
- app/products/page.tsx
- app/products/[id]/page.tsx
- components/ProductCard.tsx
- components/ProductGallery.tsx

**Acceptance Criteria**:
- [ ] Products load from API
- [ ] Filters working
- [ ] Search working
- [ ] Pagination working
- [ ] Product detail page loading correctly
- [ ] Add to cart button working
- [ ] Responsive design
- [ ] No console errors

**Estimated Effort**: 5 hours

---

### Task 3.7: Implement Cart & Checkout Pages
**Status**: Pending
**Depends on**: Task 3.6
**Owner**: TBD

**Description**:
Create shopping cart and checkout pages.

**Cart Page** (app/cart/page.tsx):
- List of cart items (image, name, quantity, price)
- Quantity controls (+ / - buttons)
- Remove item button
- Cart summary (subtotal, tax, shipping, total)
- Proceed to Checkout button
- Continue Shopping button
- Empty cart message

**Checkout Page** (app/checkout/page.tsx):
- Order summary
- Shipping address form
- Address validation
- Estimated delivery date
- Place Order button
- Success: Order confirmation page with order ID

**File to Create**:
- app/cart/page.tsx
- app/checkout/page.tsx
- components/CartSummary.tsx
- components/ShippingForm.tsx

**Acceptance Criteria**:
- [ ] Cart items display correctly
- [ ] Quantity update working
- [ ] Remove item working
- [ ] Cart total calculating correctly
- [ ] Checkout form validating
- [ ] Order creation working
- [ ] Order confirmation showing
- [ ] Responsive design

**Estimated Effort**: 5 hours

---

### Task 3.8: Implement Authentication Pages (Login & Register)
**Status**: Pending
**Depends on**: Task 3.4
**Owner**: TBD

**Description**:
Create login and registration pages.

**Login Page** (app/auth/login/page.tsx):
- Email input with validation
- Password input
- Login button
- Link to register
- Error messages
- Loading state while authenticating

**Register Page** (app/auth/register/page.tsx):
- Email input with validation (unique check)
- Password input with strength indicator
- Full name input
- Register button
- Link to login
- Error messages
- Success: Redirect to login or dashboard

**File to Create**:
- app/auth/login/page.tsx
- app/auth/register/page.tsx
- components/LoginForm.tsx
- components/RegisterForm.tsx

**Acceptance Criteria**:
- [ ] Login form working
- [ ] Register form working
- [ ] Email validation working
- [ ] Password strength indicator (optional)
- [ ] Error messages showing
- [ ] Redirect after auth working
- [ ] Responsive design

**Estimated Effort**: 3 hours

---

### Task 3.9: Implement User Dashboard
**Status**: Pending
**Depends on**: Task 3.8
**Owner**: TBD

**Description**:
Create user profile and dashboard page.

**Dashboard Page** (app/dashboard/page.tsx):
- User profile info (name, email, phone, address)
- Edit profile button (modal or form)
- Order history (recent orders)
- Link to full order history
- Logout button
- Protected route (requires auth)

**File to Create**:
- app/dashboard/page.tsx
- app/orders/page.tsx (order history)
- app/orders/[id]/page.tsx (order detail)
- components/ProfileCard.tsx
- components/OrderHistoryTable.tsx

**Acceptance Criteria**:
- [ ] Dashboard loads with user info
- [ ] Edit profile working
- [ ] Order history displaying
- [ ] Order detail page working
- [ ] Logout working
- [ ] Protected route working (redirect if not auth)
- [ ] Responsive design

**Estimated Effort**: 4 hours

---

## Phase 4: AI Chat Integration (Week 6)

### Task 4.1: Implement Chat Widget Component
**Status**: Pending
**Depends on**: Task 3.1
**Owner**: TBD
**Skill**: `building-chat-widgets`

**Description**:
Create floating chat widget component with message display and input.

**Chat Widget** (components/ChatWidget.tsx):
- Floating button (bottom-right, pink color)
- Click opens chat window (400x600px)
- Close button collapses window
- Messages display area (scrollable)
- Input field with send button
- Streaming message display (text appears gradually)
- Session management (localStorage session_id)

**Acceptance Criteria**:
- [ ] Widget appears on all pages (except login/register)
- [ ] Widget opens/closes
- [ ] Messages display correctly
- [ ] Input field working
- [ ] Streaming responses working
- [ ] Mobile responsive
- [ ] Session ID persisting

**Estimated Effort**: 4 hours

---

### Task 4.2: Implement Chat Backend (OpenAI Integration)
**Status**: Pending
**Depends on**: Task 2.7
**Owner**: TBD
**Skill**: `scaffolding-openai-agents`

**Description**:
Create chat service Netlify Function with OpenAI integration.

**File to Create**:
- netlify/functions/chat-service.py

**Features**:
```python
# OpenAI chat function with:
# - System prompt: "You are a helpful assistant for Fatima Zehra Boutique"
# - Streaming responses (SSE format)
# - Product search integration (search_products function)
# - Chat history storage in Neon database
# - Session-based conversations

class ChatHandler:
    def handle_message(session_id, user_message):
        # 1. Retrieve chat history
        # 2. Call OpenAI API with messages
        # 3. Stream response back
        # 4. Save to database
        # 5. Return assistant message

    def search_products(query, category, max_price):
        # Call product-service to search products
        # Return formatted results for AI to include in response
```

**Function Tools**:
- `search_products(query, category, max_price)`: Search products
- `get_product_details(product_id)`: Get specific product info
- `get_categories()`: List all categories

**Acceptance Criteria**:
- [ ] OpenAI integration working
- [ ] Streaming responses working (SSE)
- [ ] Product search integration working
- [ ] Chat history storage working
- [ ] Error handling (API failures, timeouts)
- [ ] No API key exposed in code

**Estimated Effort**: 5 hours

---

### Task 4.3: Implement Chat API Endpoints
**Status**: Pending
**Depends on**: Task 4.2
**Owner**: TBD

**Description**:
Create backend endpoints for chat messaging and history.

**Endpoints**:
1. **POST /api/chat/messages** (chat-service)
   - Input: {text, session_id}
   - Output: Stream (SSE)
   - Response format: `data: {text}\n\n`

2. **GET /api/chat/history** (chat-service)
   - Query params: session_id
   - Output: {messages: [{role, content, timestamp}]}

3. **DELETE /api/chat/history** (chat-service)
   - Clears chat history for session

**Acceptance Criteria**:
- [ ] All endpoints implemented
- [ ] Streaming responses working
- [ ] Chat history retrievable
- [ ] History clearable
- [ ] Error responses appropriate

**Estimated Effort**: 2 hours

---

### Task 4.4: Connect Chat Widget to Backend
**Status**: Pending
**Depends on**: Task 4.3
**Owner**: TBD
**Skill**: `streaming-llm-responses`

**Description**:
Connect frontend chat widget to backend API with streaming.

**Frontend Integration** (lib/chat.ts):
```typescript
// Client-side chat handler:
async function sendMessage(text, sessionId) {
  // 1. POST to /api/chat/messages
  // 2. Get ReadableStream response
  // 3. Read stream line by line
  // 4. Parse SSE format
  // 5. Display message as it arrives
  // 6. Save message to state
}

async function getChatHistory(sessionId) {
  // 1. GET /api/chat/history?session_id=xxx
  // 2. Return messages array
}
```

**Acceptance Criteria**:
- [ ] Chat messages sending successfully
- [ ] Streaming responses displaying
- [ ] Chat history loading
- [ ] Error messages showing
- [ ] Product recommendations clickable
- [ ] Add to cart from recommendation
- [ ] No console errors

**Estimated Effort**: 3 hours

---

## Phase 5: Images & Branding (Week 7)

### Task 5.1: Generate Product Images
**Status**: Pending
**Depends on**: None
**Owner**: TBD
**Skill**: `browser-use`, `browsing-with-playwright`

**Description**:
Use browser automation to source and download fashion product images.

**Image Categories** (20-30 total):
1. Dresses (5-6): Evening, casual, party, traditional
2. Tops (3-4): Blouses, shirts, t-shirts
3. Skirts (3-4): Long, short, traditional
4. Accessories (3-4): Scarves, bags, jewelry
5. Hero/Banner images (2-3)

**Process**:
1. [ ] Search Unsplash/Pexels/Pixabay for fashion images
2. [ ] Download high-resolution images (min 800px width)
3. [ ] Optimize for web (resize to 800x800, convert to WebP)
4. [ ] Save to `frontend/public/images/products/`
5. [ ] Create seed data with image URLs
6. [ ] Update database with image URLs

**Acceptance Criteria**:
- [ ] All 20-30 images downloaded
- [ ] Images optimized for web
- [ ] No copyright issues (free stock images)
- [ ] Images cover all categories
- [ ] Seed data updated
- [ ] Database updated

**Estimated Effort**: 4 hours

---

### Task 5.2: Create Logo & Branding Assets
**Status**: Pending
**Depends on**: None
**Owner**: TBD

**Description**:
Create or find logo for "Fatima Zehra Boutique" and branding assets.

**Assets to Create**:
1. [ ] Logo (500x200px, PNG + SVG)
2. [ ] Favicon (32x32, ICO)
3. [ ] Hero background (1920x1080, JPG/WebP)
4. [ ] Category banners (4x 800x400)
5. [ ] Social media preview (1200x630)

**Branding Guidelines**:
- Color palette: Pink (#EC4899), Purple (#9333EA), Gold (#F59E0B)
- Fonts: Playfair Display (headings), Inter (body)
- Style: Elegant, minimalist, professional

**Acceptance Criteria**:
- [ ] Logo created
- [ ] Favicon created
- [ ] All assets saved in public/images/
- [ ] Assets optimized for web
- [ ] Logo used in navbar
- [ ] Favicon appears in browser tab

**Estimated Effort**: 3 hours

---

### Task 5.3: Seed Database with Sample Products
**Status**: Pending
**Depends on**: Task 5.1
**Owner**: TBD

**Description**:
Create SQL seeds or script to populate database with sample products.

**File to Create**:
- database/seeds/seed_products.sql

**Sample Data**:
- 5-6 categories (Dresses, Tops, Skirts, Accessories, Traditional, Shoes)
- 20-30 products across categories
- Realistic prices (Rs. 2,000 - Rs. 10,000)
- Product descriptions
- Image URLs (from Task 5.1)
- Stock quantities (50-100 per item)

**Seed Script**:
```sql
INSERT INTO categories (name, description, image_url) VALUES
('Dresses', 'Beautiful dresses for every occasion', 'url');

INSERT INTO products (name, description, price, category_id, image_url, stock_quantity, featured)
VALUES
('Midnight Blue Gown', 'Elegant evening dress...', 4500, 1, 'url', 50, true);
```

**Acceptance Criteria**:
- [ ] Seed script created
- [ ] 20-30 products seeded
- [ ] All categories covered
- [ ] Prices realistic
- [ ] Images loaded
- [ ] Stock quantities set
- [ ] Featured items marked

**Estimated Effort**: 2 hours

---

## Phase 6: Deployment & Testing (Week 8)

### Task 6.1: Setup GitHub Actions CI/CD
**Status**: Pending
**Depends on**: Task 3.1
**Owner**: TBD

**Description**:
Create GitHub Actions workflow to build and deploy frontend.

**File to Create**:
- .github/workflows/deploy-frontend.yml

**Workflow**:
1. Trigger: On push to main branch
2. Setup Node.js
3. Install dependencies
4. Run tests (npm run test)
5. Build Next.js static site (npm run build)
6. Deploy to gh-pages branch
7. GitHub Pages serves automatically

**Acceptance Criteria**:
- [ ] Workflow file created
- [ ] Workflow passes
- [ ] Frontend builds successfully
- [ ] Deployment to gh-pages working
- [ ] GitHub Pages URL working

**Estimated Effort**: 2 hours

---

### Task 6.2: Configure Netlify Deployment
**Status**: Pending
**Depends on**: Task 2.7, Task 5.3
**Owner**: TBD

**Description**:
Setup Netlify for backend deployment with environment variables.

**Steps**:
1. [ ] Connect Netlify to GitHub repo
2. [ ] Create netlify.toml
3. [ ] Set environment variables:
   - NEON_DATABASE_URL
   - OPENAI_API_KEY
   - JWT_SECRET
   - CORS_ORIGINS
4. [ ] Test deployment
5. [ ] Verify functions work

**netlify.toml Configuration**:
```toml
[build]
  command = "echo 'Functions ready'"
  publish = "."

[functions]
  directory = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

**Acceptance Criteria**:
- [ ] Netlify project created
- [ ] Functions deployed
- [ ] Environment variables set
- [ ] API endpoints accessible
- [ ] Logs visible in Netlify UI

**Estimated Effort**: 2 hours

---

### Task 6.3: End-to-End Testing
**Status**: Pending
**Depends on**: Task 6.1, 6.2
**Owner**: TBD

**Description**:
Test complete user flow from registration to order.

**Test Scenarios**:
1. [ ] Register new account
2. [ ] Login with credentials
3. [ ] Browse products
4. [ ] Filter by category
5. [ ] View product details
6. [ ] Add to cart (multiple items)
7. [ ] Remove item from cart
8. [ ] Proceed to checkout
9. [ ] Fill shipping address
10. [ ] Place order
11. [ ] View order confirmation
12. [ ] Check order history
13. [ ] Chat with AI ("Show me dresses under Rs. 3000")
14. [ ] Click product from chat
15. [ ] Add to cart from chat

**Acceptance Criteria**:
- [ ] All flows working on desktop
- [ ] All flows working on mobile
- [ ] No console errors
- [ ] No unhandled exceptions
- [ ] Performance acceptable (< 3s page loads)
- [ ] Chat responses working
- [ ] Order created successfully

**Estimated Effort**: 4 hours

---

### Task 6.4: Performance & Security Testing
**Status**: Pending
**Depends on**: Task 6.3
**Owner**: TBD

**Description**:
Test performance metrics and security compliance.

**Performance Testing**:
- [ ] Lighthouse score > 90
- [ ] First Contentful Paint (FCP) < 1.5s
- [ ] Largest Contentful Paint (LCP) < 2.5s
- [ ] Cumulative Layout Shift (CLS) < 0.1
- [ ] API response time < 500ms

**Security Testing**:
- [ ] HTTPS enforced
- [ ] CORS headers correct
- [ ] No hardcoded secrets
- [ ] JWT tokens secure
- [ ] Password hashing working
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] No console warnings

**Acceptance Criteria**:
- [ ] Lighthouse score > 90
- [ ] Core Web Vitals passing
- [ ] No security issues found
- [ ] No hardcoded secrets in code

**Estimated Effort**: 3 hours

---

### Task 6.5: Production Deployment & Monitoring
**Status**: Pending
**Depends on**: Task 6.4
**Owner**: TBD

**Description**:
Deploy to production and setup monitoring.

**Frontend**:
- [ ] Deploy to GitHub Pages (main branch push)
- [ ] Verify https://[username].github.io/fatima-zehra-boutique/
- [ ] Check all pages load
- [ ] Test mobile responsiveness

**Backend**:
- [ ] Deploy to Netlify Functions
- [ ] Verify https://[site].netlify.app/.netlify/functions/
- [ ] Test all API endpoints
- [ ] Check Netlify logs

**Database**:
- [ ] Verify Neon connection
- [ ] Test database queries
- [ ] Setup automated backups
- [ ] Monitor connection pool

**Monitoring**:
- [ ] Setup error tracking (Sentry optional)
- [ ] Monitor Netlify Function logs
- [ ] Monitor GitHub Pages status
- [ ] Setup status page (optional)

**Acceptance Criteria**:
- [ ] Frontend URL working
- [ ] Backend URL working
- [ ] Database connected
- [ ] All user flows working
- [ ] Monitoring setup
- [ ] Documentation updated

**Estimated Effort**: 3 hours

---

## Summary of Task Dependencies

```
Phase 1 (Foundation):
  1.1 Docs → 1.2 Database → 1.3 Docker → 1.4-1.6 Directories

Phase 2 (Backend):
  2.1 User Models → 2.2 Auth → 2.3 Endpoints → 2.4 Netlify → 2.5 Tests
  2.6 Product Service (parallel)
  2.7 Order Service (parallel)

Phase 3 (Frontend):
  3.1 Setup → 3.2 API Client → 3.3 Auth Context
  3.4 Homepage
  3.5 Navbar/Footer
  3.6 Products
  3.7 Cart/Checkout
  3.8 Auth Pages
  3.9 Dashboard

Phase 4 (Chat):
  4.1 Widget → 4.2 OpenAI Backend → 4.3 Endpoints → 4.4 Integration

Phase 5 (Images):
  5.1 Product Images, 5.2 Branding, 5.3 Seed Data (parallel)

Phase 6 (Deployment):
  6.1 GitHub Actions, 6.2 Netlify, 6.3 E2E Tests, 6.4 Performance, 6.5 Production
```

---

**This task list provides a complete breakdown of all implementation work needed for the Fatima Zehra Boutique e-commerce platform.**
