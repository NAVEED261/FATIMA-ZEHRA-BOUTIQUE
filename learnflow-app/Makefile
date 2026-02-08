.PHONY: help setup run stop clean test build deploy-docker deploy-k8s deploy-helm logs setup-minikube

SHELL := /bin/bash
APP_NAME := learnflow-app
DOCKER_COMPOSE_FILE := docker-compose.yml
DOCKER_COMPOSE := docker-compose -f $(DOCKER_COMPOSE_FILE)

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "$(GREEN)╔══════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║         LearnFlow App - Available Commands           ║$(NC)"
	@echo "$(GREEN)╚══════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup & Run:$(NC)"
	@echo "  make setup              - First-time setup (install dependencies)"
	@echo "  make run                - Start all services (Docker Compose)"
	@echo "  make stop               - Stop all services"
	@echo "  make restart            - Restart all services"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  make test               - Run all tests"
	@echo "  make test-backend       - Run backend tests only"
	@echo "  make test-frontend      - Run frontend tests only"
	@echo "  make build              - Build all services"
	@echo "  make lint               - Lint code (ESLint + Black)"
	@echo "  make format             - Format code (Prettier + Black)"
	@echo ""
	@echo "$(YELLOW)Deployment:$(NC)"
	@echo "  make deploy-docker      - Deploy with Docker"
	@echo "  make deploy-k8s         - Deploy to Kubernetes"
	@echo "  make deploy-helm        - Deploy with Helm"
	@echo "  make setup-minikube     - Setup local Minikube K8s"
	@echo "  make deploy-prod        - Deploy to production"
	@echo ""
	@echo "$(YELLOW)Utilities:$(NC)"
	@echo "  make logs               - View logs (all services)"
	@echo "  make clean              - Clean up resources"
	@echo "  make db-migrate         - Run database migrations"
	@echo "  make db-seed            - Seed database with sample data"
	@echo "  make status             - Check service status"
	@echo "  make help               - Show this help message"
	@echo ""

# ============================================================================
# SETUP & INITIALIZATION
# ============================================================================

setup:
	@echo "$(GREEN)🔧 Setting up LearnFlow App...$(NC)"
	@chmod +x scripts/*.sh
	@./scripts/setup.sh
	@echo "$(GREEN)✅ Setup complete!$(NC)"

# ============================================================================
# RUN & CONTROL
# ============================================================================

run:
	@echo "$(GREEN)🚀 Starting LearnFlow App...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ App started!$(NC)"
	@echo ""
	@echo "$(YELLOW)Access:$(NC)"
	@echo "  Frontend:  http://localhost:3000"
	@echo "  User API:  http://localhost:8001/docs"
	@echo "  Product API: http://localhost:8002/docs"
	@echo "  Order API: http://localhost:8003/docs"
	@echo "  Chat API:  http://localhost:8004/docs"

stop:
	@echo "$(YELLOW)⛔ Stopping LearnFlow App...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ App stopped!$(NC)"

restart: stop run
	@echo "$(GREEN)✅ App restarted!$(NC)"

# ============================================================================
# TESTING
# ============================================================================

test:
	@echo "$(GREEN)🧪 Running all tests...$(NC)"
	@./scripts/test.sh
	@echo "$(GREEN)✅ Tests complete!$(NC)"

test-backend:
	@echo "$(GREEN)🧪 Running backend tests...$(NC)"
	@$(DOCKER_COMPOSE) exec user-service pytest
	@$(DOCKER_COMPOSE) exec product-service pytest
	@$(DOCKER_COMPOSE) exec order-service pytest
	@echo "$(GREEN)✅ Backend tests complete!$(NC)"

test-frontend:
	@echo "$(GREEN)🧪 Running frontend tests...$(NC)"
	@cd app/frontend && npm test
	@echo "$(GREEN)✅ Frontend tests complete!$(NC)"

# ============================================================================
# BUILD
# ============================================================================

build:
	@echo "$(GREEN)🔨 Building services...$(NC)"
	@./scripts/build.sh
	@echo "$(GREEN)✅ Build complete!$(NC)"

# ============================================================================
# CODE QUALITY
# ============================================================================

lint:
	@echo "$(GREEN)🔍 Linting code...$(NC)"
	@echo "Python (Black):"
	@find app/backend -name "*.py" -exec black --check {} \;
	@echo "JavaScript (ESLint):"
	@cd app/frontend && npm run lint
	@echo "$(GREEN)✅ Linting complete!$(NC)"

format:
	@echo "$(GREEN)✨ Formatting code...$(NC)"
	@echo "Python (Black):"
	@find app/backend -name "*.py" -exec black {} \;
	@echo "JavaScript (Prettier):"
	@cd app/frontend && npm run format
	@echo "$(GREEN)✅ Formatting complete!$(NC)"

# ============================================================================
# DATABASE
# ============================================================================

db-migrate:
	@echo "$(GREEN)📊 Running database migrations...$(NC)"
	@./scripts/migrate-db.sh
	@echo "$(GREEN)✅ Migrations complete!$(NC)"

db-seed:
	@echo "$(GREEN)🌱 Seeding database...$(NC)"
	@$(DOCKER_COMPOSE) exec user-service python -m scripts.seed_db
	@echo "$(GREEN)✅ Database seeded!$(NC)"

db-reset:
	@echo "$(RED)🗑️  Resetting database (DESTRUCTIVE)...$(NC)"
	@read -p "Are you sure? Type 'yes': " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		$(DOCKER_COMPOSE) exec -T user-service python -m scripts.reset_db; \
		$(MAKE) db-migrate; \
		$(MAKE) db-seed; \
		echo "$(GREEN)✅ Database reset!$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled.$(NC)"; \
	fi

# ============================================================================
# DEPLOYMENT
# ============================================================================

deploy-docker:
	@echo "$(GREEN)🐳 Deploying with Docker...$(NC)"
	@./deploy/scripts/deploy-docker.sh
	@echo "$(GREEN)✅ Docker deployment complete!$(NC)"

deploy-k8s:
	@echo "$(GREEN)☸️  Deploying to Kubernetes...$(NC)"
	@kubectl apply -f deploy/kubernetes/
	@echo "$(GREEN)✅ K8s deployment complete!$(NC)"
	@echo "Check status: kubectl get pods"

deploy-helm:
	@echo "$(GREEN)📊 Deploying with Helm...$(NC)"
	@helm install learnflow deploy/helm/learnflow-chart || helm upgrade learnflow deploy/helm/learnflow-chart
	@echo "$(GREEN)✅ Helm deployment complete!$(NC)"

setup-minikube:
	@echo "$(GREEN)🛠️  Setting up Minikube...$(NC)"
	@./deploy/minikube/setup.sh
	@echo "$(GREEN)✅ Minikube setup complete!$(NC)"
	@echo "Access dashboard: minikube dashboard"

deploy-prod:
	@echo "$(RED)🚀 Deploying to production...$(NC)"
	@echo "Choose deployment method:"
	@echo "1) Docker (./deploy/scripts/deploy-docker.sh prod)"
	@echo "2) Kubernetes (kubectl apply -f deploy/kubernetes/prod/)"
	@echo "3) Helm (helm install learnflow deploy/helm/learnflow-chart --values deploy/helm/values-prod.yaml)"
	@read -p "Enter choice (1-3): " choice; \
	case $$choice in \
		1) $(MAKE) deploy-docker ;; \
		2) $(MAKE) deploy-k8s ;; \
		3) $(MAKE) deploy-helm ;; \
		*) echo "Invalid choice" ;; \
	esac

# ============================================================================
# UTILITIES
# ============================================================================

logs:
	@echo "$(GREEN)📋 Viewing logs...$(NC)"
	@$(DOCKER_COMPOSE) logs -f

logs-user:
	@$(DOCKER_COMPOSE) logs -f user-service

logs-product:
	@$(DOCKER_COMPOSE) logs -f product-service

logs-order:
	@$(DOCKER_COMPOSE) logs -f order-service

logs-frontend:
	@$(DOCKER_COMPOSE) logs -f frontend

status:
	@echo "$(GREEN)📊 Service Status:$(NC)"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(GREEN)🌐 URLs:$(NC)"
	@echo "  Frontend:      http://localhost:3000"
	@echo "  User Service:  http://localhost:8001/docs"
	@echo "  Product API:   http://localhost:8002/docs"
	@echo "  Order API:     http://localhost:8003/docs"
	@echo "  Chat API:      http://localhost:8004/docs"

clean:
	@echo "$(RED)🗑️  Cleaning up...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete!$(NC)"

# ============================================================================
# AI MODEL SWITCHING
# ============================================================================

ai-switch-gemini:
	@echo "$(GREEN)🤖 Switching to Google Gemini...$(NC)"
	@sed -i 's/ai_model: .*/ai_model: gemini/' config/config.yaml
	@$(DOCKER_COMPOSE) restart chat-service
	@echo "$(GREEN)✅ Switched to Gemini!$(NC)"

ai-switch-goose:
	@echo "$(GREEN)🤖 Switching to Goose...$(NC)"
	@sed -i 's/ai_model: .*/ai_model: goose/' config/config.yaml
	@$(DOCKER_COMPOSE) restart chat-service
	@echo "$(GREEN)✅ Switched to Goose!$(NC)"

ai-switch-openai:
	@echo "$(GREEN)🤖 Switching to OpenAI...$(NC)"
	@sed -i 's/ai_model: .*/ai_model: openai/' config/config.yaml
	@$(DOCKER_COMPOSE) restart chat-service
	@echo "$(GREEN)✅ Switched to OpenAI!$(NC)"

# ============================================================================
# QUICK COMMANDS
# ============================================================================

dev: setup run
	@echo "$(GREEN)✅ Development environment ready!$(NC)"

all: setup build test run
	@echo "$(GREEN)✅ Complete setup and startup!$(NC)"

ps:
	@$(DOCKER_COMPOSE) ps

shell-user:
	@$(DOCKER_COMPOSE) exec user-service /bin/bash

shell-product:
	@$(DOCKER_COMPOSE) exec product-service /bin/bash

shell-order:
	@$(DOCKER_COMPOSE) exec order-service /bin/bash

shell-frontend:
	@$(DOCKER_COMPOSE) exec frontend /bin/bash

# ============================================================================
# GIT & VERSION CONTROL
# ============================================================================

git-status:
	@git status

git-add:
	@git add .

git-commit:
	@read -p "Enter commit message: " msg; \
	git commit -m "$$msg" -m "Co-Authored-By: LearnFlow App <learnflow@github.com>"

git-push:
	@git push

git-pull:
	@git pull

# ============================================================================

.DEFAULT_GOAL := help
