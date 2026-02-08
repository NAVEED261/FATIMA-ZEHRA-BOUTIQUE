# 🧪 Fatima Zehra Boutique - Complete Testing Guide

**Date**: 2026-01-26
**Status**: All Features Ready for Testing
**Test Environment**: Local (localhost:3000)

---

## 🎯 Testing Objectives

✅ All pages load correctly
✅ Authentication works (register/login/logout)
✅ Product browsing & filtering works
✅ Shopping cart functionality works
✅ Checkout process works
✅ Chat widget streams responses
✅ User profile management works
✅ Order history displays correctly
✅ Navigation works smoothly
✅ Responsive design works

---

## 🚀 Setup for Testing

### 1. Start All Services

```bash
cd /mnt/d/HACKATON-III/FATIMA-ZEHRA-BOUTIQUE-APP/learnflow-app

# Copy environment
cp .env.example .env

# Edit .env (add your settings if needed)

# Start services
docker-compose up -d

# Wait for services
sleep 30

# Verify all running
docker-compose ps
```

### 2. Seed Database

```bash
# Make seed script executable
chmod +x scripts/seed-database.sh

# Run seed script
./scripts/seed-database.sh

# Output should show:
# ✅ Database seeding complete!
# Categories: 6
# Products: 17
# Test Users: 1
```

### 3. Verify Services

```bash
# Check APIs are running
curl http://localhost:8001/docs      # User Service
curl http://localhost:8002/docs      # Product Service
curl http://localhost:8003/docs      # Order Service
curl http://localhost:8004/docs      # Chat Service
curl http://localhost:3000           # Frontend
```

---

## 📝 Test Cases

### TEST 1: User Registration & Login

**Objective**: Verify user can create account and login

**Test Steps**:
```
1. Navigate to http://localhost:3000
2. Click "Register" button (top right)
3. Fill in:
   - Full Name: John Doe
   - Email: john@example.com
   - Password: testpass123
4. Click "Register"
5. Verify redirected to homepage
6. Check user menu shows "John"
7. Logout
8. Login with new credentials
9. Verify successful login
```

**Expected Results**:
✅ Registration form validates input
✅ New account created
✅ JWT token issued
✅ Logged in automatically
✅ User menu shows name
✅ Login works with new credentials
✅ Logout clears session

---

### TEST 2: Browse Products

**Objective**: Verify product listing and filtering works

**Test Steps**:
```
1. Click "Products" in navbar
2. Verify product grid displays
3. Check filters work:
   - Select category "Dresses"
   - Verify only dresses shown
   - Search for "Evening"
   - Verify results filtered
4. Test pagination
5. Click product card
6. Verify product detail page
```

**Expected Results**:
✅ Products load from API
✅ Grid displays 12+ products
✅ Category filter works
✅ Search works
✅ Pagination works
✅ Product detail page loads
✅ Product info displays correctly

---

### TEST 3: Shopping Cart & Checkout

**Objective**: Verify shopping flow works end-to-end

**Test Steps**:
```
1. Browse to products
2. Click "Add to Cart" on any product
3. See success message
4. Check cart badge updates
5. Click cart icon (top right)
6. Verify items in cart
7. Update quantity
8. Remove item
9. Click "Proceed to Checkout"
10. Verify order created
11. Confirm order shows in Orders page
```

**Expected Results**:
✅ Add to cart works
✅ Cart badge updates
✅ Cart page shows items
✅ Quantity update works
✅ Remove item works
✅ Checkout creates order
✅ Order appears in history

---

### TEST 4: Chat Widget

**Objective**: Verify AI chat integration works

**Test Steps**:
```
1. Click chat button (💬 bottom right)
2. Chat window opens
3. Type: "Show me evening dresses"
4. Click Send
5. Verify streaming response
6. See assistant message
7. Continue conversation
8. Click "Clear chat"
9. Verify chat cleared
10. Refresh page
11. Verify history persists
```

**Expected Results**:
✅ Chat widget appears
✅ Message sends
✅ Response streams in real-time
✅ Chat displays properly
✅ Clear works
✅ History persists across sessions

---

### TEST 5: User Profile

**Objective**: Verify profile management works

**Test Steps**:
```
1. Click user menu (top right)
2. Select "My Profile"
3. Verify profile info displays
4. Click "Edit Profile"
5. Update:
   - Full Name: Jane Doe
   - Phone: +92 300 1234567
   - Address: 123 Main St
6. Click "Save Changes"
7. Verify success message
8. Refresh page
9. Verify changes persisted
```

**Expected Results**:
✅ Profile page loads
✅ Current info displays
✅ Edit mode works
✅ Update saves to API
✅ Success message shows
✅ Changes persist after refresh

---

### TEST 6: Order History

**Objective**: Verify order viewing works

**Test Steps**:
```
1. Click user menu
2. Select "My Orders"
3. Verify list of orders (if any)
4. Click order to expand
5. Verify order details show:
   - Order items
   - Shipping address
   - Order total
   - Order status
6. Click "Continue Shopping"
```

**Expected Results**:
✅ Orders page loads
✅ List displays correctly
✅ Can expand/collapse orders
✅ All details visible
✅ Status badges show
✅ Navigation works

---

### TEST 7: Navigation & Pages

**Objective**: Verify all pages are accessible

**Test Steps**:
```
1. Test navbar links:
   - Home ✓
   - Products ✓
   - About ✓
2. Test footer links
3. Test 404 page:
   - Navigate to /invalid
   - Verify 404 page
   - Click "Back to Home"
4. Test breadcrumbs on detail pages
```

**Expected Results**:
✅ All navbar links work
✅ All footer links work
✅ 404 page displays
✅ Back navigation works
✅ Breadcrumbs navigate correctly

---

### TEST 8: Responsive Design

**Objective**: Verify design works on all screen sizes

**Test Steps**:
```
1. Open DevTools (F12)
2. Test different breakpoints:
   - Mobile (320px)
   - Tablet (768px)
   - Desktop (1920px)
3. Verify layout adapts:
   - Menu collapses on mobile
   - Grid adjusts
   - Touch targets are large
4. Test chat widget on mobile
5. Test forms on mobile
```

**Expected Results**:
✅ Layout responsive
✅ Mobile optimized
✅ Tablet view works
✅ Desktop full featured
✅ Touch targets adequate
✅ Images scale properly

---

### TEST 9: Error Handling

**Objective**: Verify error messages and handling

**Test Steps**:
```
1. Try registering with existing email
2. Verify error message
3. Try invalid password (< 8 chars)
4. Verify validation error
5. Try adding invalid quantity
6. Try accessing protected page without login
7. Verify redirected to login
8. Simulate network error (disconnect)
9. Verify error message
```

**Expected Results**:
✅ Email validation works
✅ Password validation works
✅ Quantity validation works
✅ Auth protection works
✅ Error messages clear
✅ Network errors handled

---

### TEST 10: Performance

**Objective**: Verify app loads quickly

**Test Steps**:
```
1. Open DevTools → Network tab
2. Hard refresh homepage
3. Check load time (target: < 3s)
4. Check:
   - Total KB transferred
   - Number of requests
   - Largest assets
5. Check for:
   - Unused CSS
   - Unoptimized images
   - Slow API calls
```

**Expected Results**:
✅ Page loads < 3 seconds
✅ API calls responsive
✅ Images optimized
✅ No console errors
✅ Smooth interactions

---

## 🔐 Security Testing

### Authentication Security

```
✅ JWT tokens in cookies
✅ Password stored hashed (not visible)
✅ Protected endpoints require auth
✅ Token expires on logout
✅ CORS properly configured
✅ XSS prevention (no dangerous HTML)
✅ CSRF token sent (if applicable)
```

### Input Validation

```
✅ Email format validated
✅ Password minimum length
✅ No SQL injection possible (ORM used)
✅ File upload (if any) validated
✅ All API inputs validated
✅ Output properly escaped
```

---

## 📊 API Testing

### User Service Endpoints

```bash
# Register
curl -X POST http://localhost:8001/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Get Profile (requires token)
curl -X GET http://localhost:8001/api/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Product Service Endpoints

```bash
# List products
curl http://localhost:8002/api/products

# List with filters
curl "http://localhost:8002/api/products?category_id=1&featured=true"

# Get product
curl http://localhost:8002/api/products/1

# List categories
curl http://localhost:8002/api/categories
```

### Order Service Endpoints

```bash
# Get cart
curl http://localhost:8003/api/cart \
  -H "Authorization: Bearer YOUR_TOKEN"

# Add to cart
curl -X POST http://localhost:8003/api/cart/items \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 1,
    "price": 5000
  }'

# Checkout
curl -X POST http://localhost:8003/api/checkout \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": "123 Main St, City"
  }'
```

### Chat Service Endpoints

```bash
# Send message (streaming)
curl -X POST http://localhost:8004/api/chat/messages \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Show me evening dresses",
    "session_id": "session-123"
  }'
```

---

## 📋 Test Checklist

### Pre-Testing
- [ ] All services running (`docker-compose ps`)
- [ ] Database seeded
- [ ] Environment variables set
- [ ] APIs responding (curl tests pass)

### User Flows
- [ ] Registration flow ✓
- [ ] Login flow ✓
- [ ] Browse products ✓
- [ ] Search & filter ✓
- [ ] View product details ✓
- [ ] Add to cart ✓
- [ ] Checkout ✓
- [ ] View orders ✓
- [ ] Edit profile ✓
- [ ] Chat with AI ✓

### Pages
- [ ] Homepage ✓
- [ ] Products ✓
- [ ] Product Detail ✓
- [ ] Cart ✓
- [ ] Profile ✓
- [ ] Orders ✓
- [ ] Login ✓
- [ ] Register ✓
- [ ] About ✓
- [ ] 404 ✓

### Features
- [ ] Navigation ✓
- [ ] Search ✓
- [ ] Filter ✓
- [ ] Pagination ✓
- [ ] Chat widget ✓
- [ ] User menu ✓
- [ ] Cart badge ✓
- [ ] Forms ✓
- [ ] Validation ✓

### Performance
- [ ] Page load time ✓
- [ ] API response time ✓
- [ ] Smooth interactions ✓
- [ ] No console errors ✓
- [ ] Mobile responsive ✓

### Security
- [ ] Auth working ✓
- [ ] Protected routes ✓
- [ ] Input validation ✓
- [ ] CORS correct ✓
- [ ] No XSS ✓

---

## 🐛 Debugging

### Check Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service
docker-compose logs -f user-service
docker-compose logs -f frontend

# Clear logs
docker-compose logs --tail=0
```

### Database Inspection

```bash
# Connect to database
psql postgresql://postgres:postgres@localhost:5432/learnflow

# List tables
\dt

# View users
SELECT * FROM users;

# View products
SELECT * FROM products;

# View orders
SELECT * FROM orders;
```

### Browser DevTools

```
F12 → Console: Check for errors
F12 → Network: Check API calls
F12 → Application: Check cookies/storage
F12 → Performance: Check load times
```

---

## 📱 Browser Testing

### Required Browsers
- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Mobile Safari (latest)

### Test Coverage

```
✅ Desktop (1920x1080)
✅ Tablet (768x1024)
✅ Mobile (320x568)
✅ Touch interactions
✅ Keyboard navigation
```

---

## 🎯 Test Results Template

```
Test Date: _______
Tester: _______
Environment: localhost:3000

TEST 1: User Registration
Status: [ ] PASS [ ] FAIL
Notes: ___________________

TEST 2: Browse Products
Status: [ ] PASS [ ] FAIL
Notes: ___________________

[Continue for all tests...]

Overall Status: [ ] ALL PASS [ ] SOME FAILED [ ] CRITICAL ISSUES

Issues Found:
1. ______________________
2. ______________________

Performance:
- Page Load: ___ ms
- API Response: ___ ms
- Chat Response: ___ ms
```

---

## 🚀 Next Steps After Testing

✅ All tests pass → Ready for production
⚠️ Minor issues → Fix and retest
❌ Critical issues → Debug and resolve

---

## 📞 Support

If tests fail:
1. Check logs: `docker-compose logs`
2. Verify database: `psql` check
3. Restart services: `docker-compose restart`
4. Verify environment: `cat .env`
5. Check API docs: `http://localhost:8001/docs`

---

**Ready to test! 🚀**
