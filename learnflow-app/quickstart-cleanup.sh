#!/bin/bash

##############################################################################
# LearnFlow App - Quickstart Cleanup
# Stops all services and optionally removes demo data
#
# Usage: ./quickstart-cleanup.sh [--full]
# --full: Also removes volumes (database data)
##############################################################################

set -e

echo "🗑️  LearnFlow App - Cleanup"
echo "==========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
FULL_CLEANUP=false
if [ "$1" = "--full" ]; then
    FULL_CLEANUP=true
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker daemon is not running${NC}"
    echo "   Services may not be running. Continuing..."
fi

echo "Stopping Docker Compose services..."
docker-compose down || true

if [ "$FULL_CLEANUP" = true ]; then
    echo ""
    echo -e "${YELLOW}🗑️  Removing volumes (database data)...${NC}"
    docker-compose down -v || true

    echo -e "${GREEN}✅ Full cleanup complete${NC}"
    echo ""
    echo "All services, containers, and data have been removed."
    echo "To restart: ${YELLOW}./quickstart.sh${NC}"
else
    echo -e "${GREEN}✅ Services stopped${NC}"
    echo ""
    echo "Containers are stopped but data is preserved."
    echo "To restart: ${YELLOW}docker-compose up -d${NC}"
    echo "To full cleanup: ${YELLOW}./quickstart-cleanup.sh --full${NC}"
fi

echo ""
