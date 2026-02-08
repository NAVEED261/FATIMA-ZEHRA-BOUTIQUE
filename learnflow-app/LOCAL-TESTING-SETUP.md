# Local Testing Setup Guide

**Date**: 2026-01-26
**Environment**: Linux WSL 2
**Status**: Ready for Testing

---

## Prerequisites Installed

- ✅ Python 3.12.3
- ✅ Neon PostgreSQL connection configured
- ✅ All backend services ready
- ✅ All frontend files ready
- ⚠️ Docker NOT available (use native Python/Node.js instead)
- ⚠️ Node.js NOT available (for frontend, will use remote testing)

---

## Setup Steps (For Running Locally)

### Option 1: Manual Backend Service Startup

```bash
# Navigate to each service and install dependencies
cd app/backend/user-service
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# In another terminal:
cd app/backend/product-service
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# In another terminal:
cd app/backend/order-service
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# In another terminal:
cd app/backend/chat-service
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload

# Frontend requires Node.js (use remote testing instead)
```

### Option 2: Remote Testing (Recommended)

Since Node.js is not available locally, use browser automation to:
1. Test against deployed/running instance
2. Execute full user flows
3. Verify all API endpoints
4. Check chat widget functionality

---

## Backend Service Verification

### Check User Service

```bash
curl http://localhost:8001/docs    # Swagger UI
curl http://localhost:8001/health  # Health check
```

### Check Product Service

```bash
curl http://localhost:8002/docs    # Swagger UI
curl http://localhost:8002/api/products  # Get products
```

### Check Order Service

```bash
curl http://localhost:8003/docs    # Swagger UI
curl http://localhost:8003/health  # Health check
```

### Check Chat Service

```bash
curl http://localhost:8004/docs    # Swagger UI
```

---

## Database Seeding

Once backend services are running:

```bash
# Run seed script (after database migrations)
chmod +x scripts/seed-database.sh
./scripts/seed-database.sh
```

Expected output:
```
✅ Database seeding complete!

📊 Summary:
   - Categories: 6
   - Products: 17
   - Test Users: 1

🔑 Test User Credentials:
   Email: test@example.com
   Password: test123456
```

---

## Manual Test Checklist

### TEST 1: User Registration & Login
```bash
# Register new user
curl -X POST http://localhost:8001/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Login with credentials
curl -X POST http://localhost:8001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123"
  }'

# Expected: JWT token in response
```

### TEST 2: Get Products
```bash
curl http://localhost:8002/api/products

# With filters
curl "http://localhost:8002/api/products?category_id=1&featured=true"
```

### TEST 3: Add to Cart
```bash
# Need JWT token from login
TOKEN="your_token_here"

curl -X POST http://localhost:8003/api/cart/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2,
    "price": 5000
  }'
```

### TEST 4: Checkout
```bash
TOKEN="your_token_here"

curl -X POST http://localhost:8003/api/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": "123 Main St, City"
  }'
```

### TEST 5: Chat Message
```bash
curl -X POST http://localhost:8004/api/chat/messages \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Show me evening dresses",
    "session_id": "session-123"
  }'

# Expected: Streaming response
```

---

## Remote Browser Testing (Recommended)

Use browser automation to test the full application:

```bash
# This is handled by browser-use skill in testing phase
# See BROWSER-TESTING.md for detailed automation scripts
```

---

## API Health Status

| Service | Port | Endpoint | Expected |
|---------|------|----------|----------|
| User | 8001 | /docs | Swagger UI |
| Product | 8002 | /docs | Swagger UI |
| Order | 8003 | /docs | Swagger UI |
| Chat | 8004 | /docs | Swagger UI |
| Frontend | 3000 | / | HTML page |

---

## Troubleshooting

### Port Already in Use

```bash
# Kill process using port
lsof -ti:8001 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Database Connection Error

```bash
# Verify connection string in .env
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Missing Dependencies

```bash
# Install all backend dependencies
for service in user-service product-service order-service chat-service; do
  cd "app/backend/$service"
  pip install -r requirements.txt
  cd ../../../
done
```

---

## Next Steps

1. ✅ Verify all services can start
2. ✅ Seed database with test data
3. ✅ Run manual API tests
4. ✅ Use browser automation for full integration testing
5. ✅ Document test results

