# Middleware, CORS & Lifespan Events

## CORS Configuration

### Basic CORS Setup

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Basic CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://example.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    max_age=600  # Cache preflight for 10 minutes
)
```

### Dynamic CORS Configuration

```python
from app.core.config import settings

# Dynamic based on environment
if settings.ENVIRONMENT == "development":
    origins = ["*"]  # Allow all in dev
else:
    origins = settings.ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Custom CORS Middleware

```python
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Handle preflight
        if request.method == "OPTIONS":
            return Response(
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type",
                }
            )

        # Add CORS headers to response
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"

        return response

app.add_middleware(CustomCORSMiddleware)
```

## Middleware Stack

### Request/Response Logging

```python
from fastapi.middleware.base import BaseHTTPMiddleware
import logging
import time

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Log request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )

        # Process request
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"[{request_id}] Status: {response.status_code} "
            f"Duration: {process_time:.2f}s",
            extra={"request_id": request_id}
        )

        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id

        return response

app.add_middleware(LoggingMiddleware)
```

### Authentication Middleware

```python
class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip for public routes
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Verify token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            if not request.url.path.startswith("/api/auth"):
                # Add to request state
                request.state.user = None

        return await call_next(request)

app.add_middleware(AuthenticationMiddleware)
```

### Rate Limiting Middleware

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply rate limiting
@app.get("/items")
@limiter.limit("5/minute")
async def get_items(request: Request):
    return {"items": []}
```

### Trust Proxy Middleware

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)
```

### HTTPS Redirect

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

## Lifespan Events

### Lifespan Context Manager (FastAPI 0.93+)

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application starting...")
    await init_database()
    await init_cache()
    load_models()

    yield  # Application runs here

    # Shutdown
    print("Application shutting down...")
    await close_database()
    await close_cache()
    cleanup_resources()

app = FastAPI(lifespan=lifespan)
```

### Alternative: Event Decorators

```python
# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    print("Starting up...")

    # Initialize database
    global db_engine
    db_engine = create_engine(DATABASE_URL)
    create_tables()

    # Initialize cache
    global cache
    cache = redis.Redis(host="localhost", port=6379)

    # Load models
    load_ml_models()

    print("Startup complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    print("Shutting down...")

    # Close database
    db_engine.dispose()

    # Close cache
    cache.close()

    # Cleanup
    cleanup_resources()

    print("Shutdown complete")
```

### Database Initialization

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None

@app.on_event("startup")
async def startup():
    global engine, SessionLocal

    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_size=20,
        max_overflow=10
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized")

@app.on_event("shutdown")
async def shutdown():
    if engine:
        engine.dispose()
        print("Database closed")
```

### Cache Initialization

```python
import aioredis

redis = None

@app.on_event("startup")
async def init_cache():
    global redis
    redis = await aioredis.create_redis_pool("redis://localhost")
    print("Cache initialized")

@app.on_event("shutdown")
async def close_cache():
    if redis:
        redis.close()
        await redis.wait_closed()
        print("Cache closed")
```

### Background Tasks at Startup

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@app.on_event("startup")
async def start_scheduler():
    """Start background job scheduler"""
    scheduler.start()

    # Add scheduled jobs
    scheduler.add_job(
        cleanup_old_data,
        "interval",
        hours=24,
        id="cleanup_old_data"
    )

    scheduler.add_job(
        send_daily_reports,
        "cron",
        hour=8,
        minute=0,
        id="daily_reports"
    )

    print("Background scheduler started")

@app.on_event("shutdown")
async def stop_scheduler():
    """Stop background scheduler"""
    scheduler.shutdown()
    print("Background scheduler stopped")

async def cleanup_old_data():
    """Background task: cleanup old data"""
    print("Running cleanup task...")

async def send_daily_reports():
    """Background task: send daily reports"""
    print("Sending daily reports...")
```

### Health Check with Initialization

```python
health_status = {
    "database": False,
    "cache": False,
    "ready": False
}

@app.on_event("startup")
async def check_health():
    """Check all dependencies on startup"""
    global health_status

    # Check database
    try:
        async with get_db() as db:
            await db.execute("SELECT 1")
        health_status["database"] = True
    except Exception as e:
        print(f"Database check failed: {e}")

    # Check cache
    try:
        redis = await aioredis.create_redis_pool("redis://localhost")
        await redis.ping()
        redis.close()
        health_status["cache"] = True
    except Exception as e:
        print(f"Cache check failed: {e}")

    health_status["ready"] = all(health_status.values())
    print(f"Health status: {health_status}")

@app.get("/health")
async def health():
    """Health check endpoint"""
    if not health_status["ready"]:
        raise HTTPException(
            status_code=503,
            detail="Service not ready"
        )
    return {"status": "healthy", "details": health_status}
```

## Complete Middleware Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

# Middleware order matters (execute from last to first)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("📦 Initializing application...")
    await init_resources()

    yield

    # Shutdown
    print("🛑 Cleaning up resources...")
    await cleanup_resources()

# Create app with lifespan
app = FastAPI(
    title="My API",
    description="API with full middleware stack",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trust proxy (for behind reverse proxy)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com"]
)

# GZIP compression
app.add_middleware(
    GZIPMiddleware,
    minimum_size=1000
)

# Custom middleware (last)
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthenticationMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```
