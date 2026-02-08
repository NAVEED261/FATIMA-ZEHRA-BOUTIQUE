# Browser Automation Test Suite

**Date**: 2026-01-26
**Application**: Fatima Zehra Boutique E-Commerce Platform
**Test Environment**: http://localhost:3000 (local) or deployed URL

---

## Prerequisites

- Frontend running at http://localhost:3000 (or deployed URL)
- All 4 backend services running (8001-8004)
- Database seeded with test data
- Browser automation tools ready

---

## Test Scenarios (Automated)

### TEST 1: Homepage Loads Correctly

**Objective**: Verify homepage loads with correct branding and layout

**Steps**:
1. Navigate to http://localhost:3000
2. Wait for page to fully load
3. Verify page title: "Fatima Zehra Boutique"
4. Check for:
   - Navbar with logo
   - Hero section with banner
   - Featured products section
   - Categories section
   - Footer
5. Take screenshot

**Expected Results**:
- Page loads within 3 seconds
- All sections visible
- No console errors
- Responsive layout

**Pass Criteria**: ✅ Homepage displays correctly with all sections

---

### TEST 2: User Registration Flow

**Objective**: Verify new user can register account

**Steps**:
1. Click "Register" button in navbar
2. Navigate to /auth/register page
3. Fill registration form:
   - Email: test.user.automation@example.com
   - Password: TestPassword123!
   - Full Name: Test Automation User
4. Click "Register" button
5. Verify redirect to homepage
6. Check user menu shows user name

**Expected Results**:
- Form validates input (password min 8 chars)
- Account created successfully
- JWT token issued
- User logged in automatically
- User name appears in navbar

**Pass Criteria**: ✅ Registration successful, user logged in

---

### TEST 3: User Login Flow

**Objective**: Verify existing user can login

**Prerequisites**: Test user exists (test@example.com / test123456)

**Steps**:
1. If logged in, logout first
2. Click "Login" in navbar
3. Navigate to /auth/login page
4. Fill login form:
   - Email: test@example.com
   - Password: test123456
5. Click "Login" button
6. Verify redirect to homepage
7. Check user menu shows user name

**Expected Results**:
- Login form displays
- Credentials accepted
- JWT token issued
- User logged in
- User name visible in navbar

**Pass Criteria**: ✅ Login successful

---

### TEST 4: Browse Products

**Objective**: Verify product listing with filters

**Steps**:
1. Click "Products" in navbar
2. Wait for product grid to load
3. Verify at least 12 products displayed
4. Check each product card shows:
   - Product image
   - Product name
   - Price in Rs.
   - "Add to Cart" button
5. Test filters:
   - Select category "Dresses"
   - Verify only dresses shown
   - Clear filter
6. Test search:
   - Search for "evening"
   - Verify results filtered
7. Test pagination:
   - Navigate through pages
   - Verify correct products per page

**Expected Results**:
- Products load from API
- Filters work correctly
- Search works
- Pagination functional
- Prices formatted as Rs.

**Pass Criteria**: ✅ Product listing works with all filters

---

### TEST 5: Product Detail Page

**Objective**: Verify product detail page loads and functions

**Steps**:
1. From products page, click on any product card
2. Navigate to /products/[id] page
3. Verify page displays:
   - Large product image
   - Product name
   - Full description
   - Price (Rs.)
   - Stock status
   - Quantity selector
   - "Add to Cart" button
4. Test quantity selector:
   - Change quantity using +/- buttons
   - Change quantity via input field
   - Verify max stock limit enforced
5. Click "Add to Cart"
6. Verify success message

**Expected Results**:
- Product detail page loads
- All information displays
- Quantity selector works
- Add to cart functional
- Success message shown

**Pass Criteria**: ✅ Product details and add to cart working

---

### TEST 6: Shopping Cart

**Objective**: Verify shopping cart functionality

**Prerequisites**: At least one item added to cart

**Steps**:
1. Click cart icon in navbar
2. Verify cart page loads (/cart)
3. Check cart displays:
   - Items in cart
   - Quantity for each
   - Price per item
   - Subtotal
4. Test quantity update:
   - Increase quantity
   - Decrease quantity
   - Verify subtotal updates
5. Test remove item:
   - Click remove on one item
   - Verify item removed
   - Subtotal updated
6. Add different product:
   - Verify multiple items in cart
   - Check cart badge updates in navbar
7. Click "Proceed to Checkout"

**Expected Results**:
- Cart displays all items
- Quantity updates work
- Subtotal calculates correctly
- Remove item works
- Cart badge shows count
- Checkout button functional

**Pass Criteria**: ✅ Shopping cart works correctly

---

### TEST 7: Checkout & Order Creation

**Objective**: Verify checkout process creates order

**Steps**:
1. From cart, click "Proceed to Checkout"
2. Verify checkout page displays
3. Fill shipping form:
   - Shipping Address: "123 Main Street, Karachi"
4. Review order summary:
   - Check items
   - Check total
5. Click "Place Order"
6. Verify order confirmation page
7. Check order appears in database

**Expected Results**:
- Checkout form displays
- Order created with correct items
- Order visible in orders page
- Cart cleared after checkout
- Success message shown

**Pass Criteria**: ✅ Checkout creates order successfully

---

### TEST 8: Orders History

**Objective**: Verify user can view order history

**Steps**:
1. Click user menu → "My Orders"
2. Navigate to /orders page
3. Verify page displays:
   - List of all user orders
   - Order number
   - Order status
   - Order date
   - Order total
4. Click order to expand:
   - View order items
   - View quantities and prices
   - View shipping address
   - View order summary
5. Click "Continue Shopping"
6. Verify redirected to products

**Expected Results**:
- Orders page displays
- All orders listed
- Expandable order details work
- All information visible
- Navigation works

**Pass Criteria**: ✅ Order history displays correctly

---

### TEST 9: User Profile Management

**Objective**: Verify profile viewing and editing

**Steps**:
1. Click user menu → "My Profile"
2. Navigate to /profile page
3. Verify profile displays:
   - Email (read-only)
   - Full name
   - Phone number
   - Address
   - Member since date
4. Click "Edit Profile"
5. Update information:
   - Change full name to "Automation Test User Updated"
   - Add phone: "+92 300 1234567"
   - Add address: "123 Main St, Karachi"
6. Click "Save Changes"
7. Verify success message
8. Refresh page
9. Verify changes persisted

**Expected Results**:
- Profile page loads
- Edit mode works
- Changes save to API
- Success message shown
- Changes persist after refresh

**Pass Criteria**: ✅ Profile management working

---

### TEST 10: Chat Widget Functionality

**Objective**: Verify AI chat widget works with streaming

**Steps**:
1. Look for floating chat button (bottom-right corner)
2. Click chat button to open chat window
3. Verify chat window displays:
   - Welcome message
   - Input field
   - Send button
4. Type message: "Show me evening dresses"
5. Click Send
6. Verify:
   - Message appears with user styling
   - Loading indicator shows
   - Assistant message streams in
   - Streaming chunks appear progressively
7. Wait for full response
8. Verify response content makes sense
9. Type follow-up: "Which one is most popular?"
10. Verify conversation continues
11. Click "Clear Chat"
12. Verify chat cleared
13. Refresh page
14. Verify chat history persists

**Expected Results**:
- Chat widget appears on page
- Messages send successfully
- OpenAI responses stream in real-time
- Chat history loads on refresh
- Clear function works
- Smooth animations

**Pass Criteria**: ✅ Chat widget with streaming working

---

### TEST 11: Navigation & Links

**Objective**: Verify all navigation links work

**Steps**:
1. From any page, test navbar links:
   - Click "Home" → verify homepage
   - Click "Products" → verify products page
   - Click "About" → verify about page
   - Click logo → verify homepage
2. Test footer links (if present)
3. Test invalid route:
   - Navigate to /invalid-page
   - Verify 404 page displays
   - Click "Back to Home"
   - Verify redirected to homepage

**Expected Results**:
- All navbar links functional
- Correct pages load
- 404 page works
- Navigation smooth

**Pass Criteria**: ✅ Navigation works correctly

---

### TEST 12: Responsive Design

**Objective**: Verify app works on different screen sizes

**Steps**:
1. Test on desktop (1920x1080):
   - Verify full layout visible
   - Products show in grid
   - Navbar fully visible
2. Test on tablet (768x1024):
   - Verify layout adjusts
   - Products in smaller grid
   - Navigation still accessible
3. Test on mobile (375x667):
   - Verify mobile layout
   - Menu collapses to hamburger
   - Products single column
   - Touch targets adequate size
4. Test chat widget on mobile:
   - Widget still accessible
   - Expandable on small screen

**Expected Results**:
- Responsive on all sizes
- Content readable
- Navigation accessible
- Touch targets large enough

**Pass Criteria**: ✅ Responsive design working

---

### TEST 13: Error Handling

**Objective**: Verify error messages display correctly

**Steps**:
1. Try registering with existing email
   - Verify error message
2. Try login with wrong password
   - Verify error message
3. Add invalid quantity to cart
   - Verify validation
4. Access protected page without login
   - Verify redirect to login
5. Try empty search
   - Verify handling

**Expected Results**:
- Clear error messages
- Form validation works
- Protected routes enforced
- User not confused

**Pass Criteria**: ✅ Error handling working

---

### TEST 14: Performance Metrics

**Objective**: Verify page loading performance

**Steps**:
1. Open DevTools Performance tab
2. Hard refresh homepage
3. Measure:
   - Page load time (target: < 3 seconds)
   - First Contentful Paint (FCP)
   - Largest Contentful Paint (LCP)
   - Total requests
   - Total size transferred
4. Check for:
   - No console errors
   - No console warnings
   - Smooth interactions

**Expected Results**:
- Page load < 3 seconds
- LCP < 2.5 seconds
- Minimal requests
- Optimized asset sizes
- No errors

**Pass Criteria**: ✅ Performance acceptable

---

### TEST 15: Security

**Objective**: Verify security measures in place

**Steps**:
1. Check JWT token:
   - Verify token in request headers
   - Verify token expires properly
2. Check password:
   - Verify not displayed in HTML
   - Verify hashed in database
3. Check CORS:
   - Verify API calls work from frontend
   - Verify XSS prevention
4. Check no sensitive data:
   - Verify no API keys in code
   - Verify no passwords in logs

**Expected Results**:
- JWT tokens used correctly
- Passwords hashed
- CORS configured
- No sensitive data exposed
- HTTPS ready

**Pass Criteria**: ✅ Security measures in place

---

## Test Execution Report

### Automated Test Results

| Test # | Name | Status | Time | Notes |
|--------|------|--------|------|-------|
| 1 | Homepage | [  ] | - | - |
| 2 | Registration | [  ] | - | - |
| 3 | Login | [  ] | - | - |
| 4 | Browse Products | [  ] | - | - |
| 5 | Product Detail | [  ] | - | - |
| 6 | Shopping Cart | [  ] | - | - |
| 7 | Checkout | [  ] | - | - |
| 8 | Orders History | [  ] | - | - |
| 9 | Profile Management | [  ] | - | - |
| 10 | Chat Widget | [  ] | - | - |
| 11 | Navigation | [  ] | - | - |
| 12 | Responsive Design | [  ] | - | - |
| 13 | Error Handling | [  ] | - | - |
| 14 | Performance | [  ] | - | - |
| 15 | Security | [  ] | - | - |

### Summary

- **Total Tests**: 15
- **Passed**: [ ]
- **Failed**: [ ]
- **Blocked**: [ ]

### Critical Issues Found

(None at this time - testing not yet executed)

### Recommendations

1. Run tests in sequence
2. Document any failures
3. Fix issues immediately
4. Re-test before deployment
5. Monitor production performance

---

## Next Phase: Deployment

Once all tests pass:
1. Deploy frontend to GitHub Pages
2. Deploy backend to Netlify (if needed)
3. Configure custom domain
4. Run production smoke tests
5. Monitor for errors

---

**Status**: Ready to execute automated tests
**Last Updated**: 2026-01-26

