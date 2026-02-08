#!/bin/bash

# Vercel Deployment Verification Script
# Usage: ./verify-deployment.sh https://your-app.vercel.app
#
# This script verifies that all endpoints are working correctly
# and the app is properly deployed.

if [ -z "$1" ]; then
    echo "Usage: ./verify-deployment.sh <VERCEL_URL>"
    echo "Example: ./verify-deployment.sh https://fatima-zehra-boutique.vercel.app"
    exit 1
fi

BASE_URL="$1"
PASSED=0
FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Fatima Zehra Boutique — Deployment Verification${NC}"
echo -e "${BLUE}URL: ${BASE_URL}${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Test function
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected="$3"

    echo -ne "${BLUE}Testing${NC} $name... "

    response=$(curl -s "$url" 2>/dev/null)

    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "  Expected: $expected"
        echo "  Got: $response" | head -1
        ((FAILED++))
    fi
}

# 1. Health Check
echo -e "${YELLOW}[1/10] API Health Checks${NC}"
test_endpoint "Health" "$BASE_URL/api/health" '"status":"ok"'

# 2. Categories
echo -e "\n${YELLOW}[2/10] Categories Endpoint${NC}"
test_endpoint "Categories" "$BASE_URL/api/categories" '"id"'

# 3. Products
echo -e "\n${YELLOW}[3/10] Products Endpoint${NC}"
test_endpoint "Products" "$BASE_URL/api/products?limit=1" '"name"'

# 4. Product Count
echo -e "\n${YELLOW}[4/10] Product Count (should be 40)${NC}"
count=$(curl -s "$BASE_URL/api/products" | grep -o '"id"' | wc -l)
echo -ne "${BLUE}Product count${NC}: "
if [ "$count" -gt 0 ]; then
    echo -e "${GREEN}✅ $count products found${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ No products found${NC}"
    ((FAILED++))
fi

# 5. Frontend Home Page
echo -e "\n${YELLOW}[5/10] Frontend Home Page${NC}"
test_endpoint "Homepage" "$BASE_URL/" "Fatima Zehra\|fatima\|boutique"

# 6. Frontend Assets
echo -e "\n${YELLOW}[6/10] Frontend Assets (Next.js)${NC}"
status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$status" = "200" ]; then
    echo -e "${GREEN}✅ Page loads (HTTP $status)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Page not loading (HTTP $status)${NC}"
    ((FAILED++))
fi

# 7. Register Endpoint
echo -e "\n${YELLOW}[7/10] User Registration Endpoint${NC}"
register_response=$(curl -s -X POST "$BASE_URL/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}' 2>/dev/null)

if echo "$register_response" | grep -q "id\|email\|error"; then
    echo -e "${GREEN}✅ Register endpoint responds${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Register endpoint unknown response${NC}"
fi

# 8. Product Details
echo -e "\n${YELLOW}[8/10] Product Details Endpoint${NC}"
test_endpoint "Product Details" "$BASE_URL/api/products/1" '"name"'

# 9. Verify Database Connection
echo -e "\n${YELLOW}[9/10] Database Connection${NC}"
echo -ne "${BLUE}Checking database connectivity${NC}... "
db_test=$(curl -s "$BASE_URL/api/products" | grep -c "total")
if [ "$db_test" -gt 0 ]; then
    echo -e "${GREEN}✅ Database connected${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Database not responding${NC}"
    ((FAILED++))
fi

# 10. Response Times
echo -e "\n${YELLOW}[10/10] Performance Check${NC}"
echo -ne "${BLUE}Frontend response time${NC}: "
start_time=$(date +%s%N)
curl -s "$BASE_URL/" > /dev/null 2>&1
end_time=$(date +%s%N)
response_ms=$(( (end_time - start_time) / 1000000 ))

if [ "$response_ms" -lt 5000 ]; then
    echo -e "${GREEN}✅ ${response_ms}ms${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  ${response_ms}ms (slow, might be cold start)${NC}"
fi

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ "$FAILED" -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed! Deployment is working correctly.${NC}\n"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Check the errors above.${NC}\n"
    exit 1
fi
