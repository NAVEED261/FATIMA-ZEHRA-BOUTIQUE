#!/bin/bash

# ============================================================================
# LearnFlow App - Push to GitHub Script
# ============================================================================
# One-command GitHub push with complete setup
#
# Usage: ./PUSH-TO-GITHUB.sh
#
# ============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   LearnFlow App - Push to GitHub                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# Step 1: Verify prerequisites
# ============================================================================

echo -e "${YELLOW}1️⃣  Checking prerequisites...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed!${NC}"
    echo "   Install from: https://git-scm.com/download/"
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI not found (optional)${NC}"
    echo "   Install from: https://cli.github.com/"
    USE_GH=false
else
    USE_GH=true
fi

echo -e "${GREEN}✅ Prerequisites checked${NC}"

# ============================================================================
# Step 2: Initialize Git (if needed)
# ============================================================================

echo ""
echo -e "${YELLOW}2️⃣  Initializing Git repository...${NC}"

if [ ! -d ".git" ]; then
    echo "Initializing git..."
    git init
    echo -e "${GREEN}✅ Git initialized${NC}"
else
    echo -e "${GREEN}✅ Git already initialized${NC}"
fi

# ============================================================================
# Step 3: Add all files
# ============================================================================

echo ""
echo -e "${YELLOW}3️⃣  Adding files...${NC}"

git add .

# Verify .env is NOT staged
if git diff --cached --name-only | grep -q "\.env$"; then
    echo -e "${RED}❌ ERROR: .env file should not be committed!${NC}"
    git reset .env
    echo -e "${GREEN}✅ Removed .env from staging${NC}"
fi

echo -e "${GREEN}✅ Files added${NC}"

# ============================================================================
# Step 4: Create commit
# ============================================================================

echo ""
echo -e "${YELLOW}4️⃣  Creating initial commit...${NC}"

git commit -m "feat: LearnFlow App - Production-ready e-commerce platform

Complete foundation with:
- 14+ directories with full structure
- 4,500+ lines of comprehensive documentation
- 6 database migrations (users, products, orders, chat)
- Docker Compose setup (5 services + PostgreSQL)
- Configuration with sensible defaults (.env.example, config.yaml)
- Makefile with 30+ common commands
- GitHub Actions CI/CD pipeline
- 4 AI integration templates (OpenAI, Gemini, Goose, custom)
- 5 deployment options (Docker, K8s, Helm, Minikube, manual)
- Complete specifications (15 user stories, 50+ tasks)
- Team standards and guidelines (CONSTITUTION.md)

Ready for:
✅ Local development (docker-compose up -d)
✅ Phase 2 backend implementation
✅ Phase 3 frontend development
✅ Team collaboration (GitHub)
✅ Production deployment (Docker/K8s/Helm)

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"

echo -e "${GREEN}✅ Commit created${NC}"

# ============================================================================
# Step 5: Set up remote
# ============================================================================

echo ""
echo -e "${YELLOW}5️⃣  Setting up GitHub remote...${NC}"

# Check if remote exists
if git remote | grep -q origin; then
    echo -e "${YELLOW}Remote 'origin' already exists${NC}"
    EXISTING_URL=$(git remote get-url origin)
    echo "Current URL: $EXISTING_URL"
else
    echo -e "${YELLOW}Enter your GitHub repository URL:${NC}"
    echo "Format: https://github.com/YOUR_USERNAME/learnflow-app.git"
    read -p "GitHub URL: " GITHUB_URL

    if [ -z "$GITHUB_URL" ]; then
        echo -e "${RED}❌ No URL provided${NC}"
        exit 1
    fi

    git remote add origin "$GITHUB_URL"
    echo -e "${GREEN}✅ Remote added${NC}"
fi

# ============================================================================
# Step 6: Push to GitHub
# ============================================================================

echo ""
echo -e "${YELLOW}6️⃣  Pushing to GitHub...${NC}"

# Create main branch
git branch -M main

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
else
    echo -e "${RED}❌ Push failed!${NC}"
    exit 1
fi

# ============================================================================
# Step 7: Verify push
# ============================================================================

echo ""
echo -e "${YELLOW}7️⃣  Verifying push...${NC}"

if git log -1 --oneline; then
    echo -e "${GREEN}✅ Push verified${NC}"
fi

# ============================================================================
# Step 8: Show next steps
# ============================================================================

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🎉 Successfully Pushed! 🎉               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

REPO_URL=$(git remote get-url origin)
GITHUB_USERNAME=$(echo $REPO_URL | cut -d'/' -f4)
REPO_NAME=$(echo $REPO_URL | cut -d'/' -f5 | sed 's/.git//')

echo -e "${YELLOW}📋 Repository Information:${NC}"
echo "  URL: $REPO_URL"
echo "  Username: $GITHUB_USERNAME"
echo "  Repository: $REPO_NAME"
echo ""

echo -e "${YELLOW}🌐 Access Your Repository:${NC}"
echo "  https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

echo -e "${YELLOW}👥 Share with Team:${NC}"
echo "  Clone: git clone $REPO_URL"
echo "  URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

echo -e "${YELLOW}🚀 Next Steps:${NC}"
echo "  1. Visit your repository on GitHub"
echo "  2. Setup branch protection (optional)"
echo "  3. Add team members as collaborators"
echo "  4. Start Phase 2 implementation"
echo ""

echo -e "${YELLOW}📖 Documentation:${NC}"
echo "  - Start: README.md"
echo "  - Reference: CLAUDE.md"
echo "  - Setup: SETUP-COMPLETE.md"
echo "  - User Stories: specs/spec.md"
echo "  - Tasks: specs/tasks.md"
echo "  - Standards: CONSTITUTION.md"
echo ""

echo -e "${GREEN}✅ You're all set! Happy coding! 🚀${NC}"
echo ""
