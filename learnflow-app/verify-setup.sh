#!/bin/bash

##############################################################################
# LearnFlow App - Verification Script
# Pre-flight checks to ensure the setup is complete and ready
#
# Usage: ./verify-setup.sh
# Exit code: 0 if all checks pass, 1 if any critical check fails
##############################################################################

set -e

echo "🔍 LearnFlow App - Setup Verification"
echo "====================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Scoring
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Helper functions
check_pass() {
    echo -e "${GREEN}✅${NC} $1"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
}

check_fail() {
    echo -e "${RED}❌${NC} $1"
    echo "   ${RED}Fix:${NC} $2"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
}

check_warn() {
    echo -e "${YELLOW}⚠️${NC} $1"
    echo "   ${YELLOW}Note:${NC} $2"
    CHECKS_WARNING=$((CHECKS_WARNING + 1))
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  PREREQUISITES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    check_pass "Docker installed ($DOCKER_VERSION)"
else
    check_fail "Docker not found" "Install from https://docs.docker.com/get-docker/"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    DC_VERSION=$(docker-compose --version | awk '{print $3}' | sed 's/,//')
    check_pass "Docker Compose installed ($DC_VERSION)"
elif docker compose version &> /dev/null 2>&1; then
    check_pass "Docker Compose (integrated) available"
else
    check_fail "Docker Compose not found" "Install from https://docs.docker.com/compose/install/"
fi

# Check Docker daemon
if docker info > /dev/null 2>&1; then
    check_pass "Docker daemon is running"
else
    check_fail "Docker daemon not running" "Start Docker Desktop or the Docker daemon"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    check_pass "Node.js installed ($NODE_VERSION)"
else
    check_warn "Node.js not found" "Only needed if running without Docker (optional)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  PROJECT FILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check required files
files=(
    "docker-compose.yml"
    "app/frontend/package.json"
    "app/frontend/next.config.js"
    "README.md"
    "CLAUDE.md"
    "scripts/setup.sh"
    "scripts/run.sh"
    "scripts/test.sh"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file exists"
    else
        check_fail "$file missing" "File should exist: $file"
    fi
done

# Check required directories
dirs=(
    "app/frontend"
    "app/backend"
    "database"
    "deploy"
    "docs"
    "scripts"
)

for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Directory exists: $dir"
    else
        check_fail "Directory missing: $dir" "Create: mkdir -p $dir"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  ENVIRONMENT CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check .env file
if [ -f ".env" ]; then
    check_pass ".env file exists"

    # Check for required variables
    if grep -q "DATABASE_URL" .env; then
        check_pass "DATABASE_URL is set"
    else
        check_warn "DATABASE_URL not found in .env" "Set: export DATABASE_URL=postgresql://..."
    fi

    if grep -q "JWT_SECRET" .env; then
        check_pass "JWT_SECRET is set"
    else
        check_warn "JWT_SECRET not found in .env" "Set: export JWT_SECRET=your-secret-key"
    fi
else
    check_fail ".env file not found" "Copy from .env.example: cp .env.example .env && edit it"
fi

# Check .env.example exists
if [ -f ".env.example" ]; then
    check_pass ".env.example exists (reference file)"
else
    check_warn ".env.example not found" "Reference configuration file missing"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  PORT AVAILABILITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if ports are available
ports=(
    "3000:Frontend"
    "5432:PostgreSQL"
    "8001:User Service"
    "8002:Product Service"
    "8003:Order Service"
    "8004:Chat Service"
)

check_ports() {
    for port_info in "${ports[@]}"; do
        port=$(echo $port_info | cut -d: -f1)
        service=$(echo $port_info | cut -d: -f2)

        if command -v nc &> /dev/null; then
            if nc -z localhost $port 2>/dev/null; then
                check_warn "Port $port ($service) is in use" "Service might already be running or port is blocked"
            else
                check_pass "Port $port ($service) is available"
            fi
        else
            check_warn "netcat not available" "Install with: apt-get install netcat (Ubuntu) or brew install netcat (macOS)"
            break
        fi
    done
}

check_ports

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  DOCUMENTATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docs=(
    "docs/SETUP.md"
    "docs/ARCHITECTURE.md"
    "docs/DEPLOYMENT.md"
    "docs/API.md"
    "docs/TROUBLESHOOTING.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        check_pass "$doc exists"
    else
        check_warn "$doc missing" "Documentation file should exist"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL_CHECKS=$((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING))

echo "Results:"
echo -e "  ${GREEN}✅ Passed:${NC}  $CHECKS_PASSED/$TOTAL_CHECKS"
echo -e "  ${YELLOW}⚠️  Warnings:${NC} $CHECKS_WARNING/$TOTAL_CHECKS"
echo -e "  ${RED}❌ Failed:${NC}  $CHECKS_FAILED/$TOTAL_CHECKS"
echo ""

# Calculate readiness score
if [ $CHECKS_FAILED -eq 0 ]; then
    READINESS=10
elif [ $CHECKS_FAILED -le 2 ]; then
    READINESS=8
else
    READINESS=$((10 - CHECKS_FAILED))
fi

echo "Readiness Score: ${BLUE}$READINESS/10${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Setup is ready!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start services:  ${YELLOW}./quickstart.sh${NC}"
    echo "  2. Or use Docker:   ${YELLOW}docker-compose up -d${NC}"
    echo "  3. Open frontend:   ${YELLOW}http://localhost:3000${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Setup has issues that must be fixed${NC}"
    echo ""
    echo "Fix the failed checks above, then run this script again."
    echo ""
    exit 1
fi
