#!/bin/bash

##############################################################################
# LearnFlow App - Zero-Config Quickstart
# Instantly run the full e-commerce platform with one command
#
# Usage: ./quickstart.sh
# Cleanup: ./quickstart-cleanup.sh
##############################################################################

set -e

echo "🚀 LearnFlow App - Zero-Config Quickstart"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check 1: Prerequisites
echo "📋 Step 1: Checking prerequisites..."
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "   Install from: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC} ($(docker --version | awk '{print $3}' | sed 's/,//'))"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "   Install from: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Check Docker daemon
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    echo "   Start Docker Desktop or the Docker daemon"
    exit 1
fi
echo -e "${GREEN}✅ Docker daemon is running${NC}"

echo ""
echo "📋 Step 2: Setting up environment..."
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file with demo credentials..."
    cat > .env << 'EOF'
# LearnFlow Demo Environment
DATABASE_URL=postgresql://postgres:demo123@postgres:5432/learnflow
JWT_SECRET=demo-secret-key-change-in-production-12345
AI_API_KEY=sk-demo-key
ENVIRONMENT=development
DEBUG=true
FRONTEND_URL=http://localhost:3000
API_PORT=8001
DEMO_MODE=true
EOF
    echo -e "${GREEN}✅ .env created with demo credentials${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists, using existing configuration${NC}"
fi

echo ""
echo "📋 Step 3: Starting services with Docker Compose..."
echo ""

# Stop any existing containers
echo "Checking for existing containers..."
docker-compose down -v 2>/dev/null || true

# Start services
echo "Starting Docker Compose services..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be healthy (this may take 30-60 seconds)..."
echo ""

# Function to check if service is healthy
check_service() {
    local port=$1
    local name=$2
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if nc -z localhost $port 2>/dev/null; then
            echo -e "${GREEN}✅ $name is ready${NC} (port $port)"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e "${RED}❌ $name did not start in time${NC}"
    return 1
}

# Check all services
services_ok=true

check_service 5432 "PostgreSQL" || services_ok=false
check_service 3000 "Frontend" || services_ok=false
check_service 8001 "User Service" || services_ok=false
check_service 8002 "Product Service" || services_ok=false
check_service 8003 "Order Service" || services_ok=false

if [ "$services_ok" = false ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Some services may still be starting. Checking logs...${NC}"
    docker-compose logs --tail=20
fi

echo ""
echo "📋 Step 4: Seeding demo data..."
echo ""

# Seed database with demo data
if [ -f "scripts/seed-database.sh" ]; then
    bash scripts/seed-database.sh 2>/dev/null || echo -e "${YELLOW}⚠️  Database seeding skipped${NC}"
else
    echo -e "${YELLOW}⚠️  Seed script not found, skipping demo data${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ LearnFlow App is running!${NC}"
echo ""
echo "🌐 Frontend:  ${YELLOW}http://localhost:3000${NC}"
echo "📚 API Docs:  ${YELLOW}http://localhost:8001/docs${NC}"
echo ""
echo "📧 Demo Credentials:"
echo "   Email:    ${YELLOW}demo@example.com${NC}"
echo "   Password: ${YELLOW}demo123${NC}"
echo ""
echo "🧪 Test the app:"
echo "   1. Open ${YELLOW}http://localhost:3000${NC} in your browser"
echo "   2. Browse products (40 items with images)"
echo "   3. Click on a product to see details"
echo "   4. Try the payment form (demo mode)"
echo "   5. Chat with AI on any page (bottom right)"
echo ""
echo "🛑 To stop all services:"
echo "   ${YELLOW}docker-compose down${NC}"
echo ""
echo "🗑️  To cleanup completely:"
echo "   ${YELLOW}./quickstart-cleanup.sh${NC}"
echo ""
echo "📖 For more information:"
echo "   - Read: ${YELLOW}README.md${NC} (quick overview)"
echo "   - Read: ${YELLOW}CLAUDE.md${NC} (complete reference)"
echo "   - Read: ${YELLOW}docs/SETUP.md${NC} (detailed setup)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if nc command exists for port checking
if ! command -v nc &> /dev/null; then
    echo -e "${YELLOW}⚠️  Note: Install 'netcat' for better service health checks${NC}"
    echo "   Ubuntu/Debian: ${YELLOW}sudo apt-get install netcat${NC}"
    echo "   macOS:         ${YELLOW}brew install netcat${NC}"
    echo ""
fi

exit 0
