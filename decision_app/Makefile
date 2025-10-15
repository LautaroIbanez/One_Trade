.PHONY: help install test lint format clean dev down logs

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "One Trade Decision App - Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup Commands
install: ## Install all dependencies (backend + frontend)
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed!"

setup-env: ## Copy .env.example files
	@echo "Setting up environment files..."
	cp -n backend/env.example backend/.env || true
	cp -n env.example .env || true
	@echo "✅ Environment files created! Remember to update them with your values."

# Development Commands
dev: ## Start all services in development mode
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✅ All services started!"
	@echo "Backend API: http://localhost:8000"
	@echo "Frontend: Run 'make frontend' in another terminal"
	@echo "PgAdmin: http://localhost:5050"
	@echo "RabbitMQ Management: http://localhost:15672"
	@echo "Flower (Celery): http://localhost:5555"

down: ## Stop all services
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

down-v: ## Stop all services and remove volumes
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v

restart: down dev ## Restart all services

# Individual Services
backend: ## Run backend development server (requires services running)
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Run frontend development server
	cd frontend && npm run dev

# Database Commands
db-migrate: ## Run database migrations
	cd backend && alembic upgrade head

db-revision: ## Create a new migration (use MSG="message")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

db-downgrade: ## Downgrade database by one revision
	cd backend && alembic downgrade -1

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "⚠️  This will destroy all data! Press Ctrl+C to cancel..."
	@sleep 5
	docker-compose down -v
	docker-compose up -d postgres
	sleep 5
	cd backend && alembic upgrade head

# Testing Commands
test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

test-backend: ## Run backend tests only
	cd backend && pytest -v

test-frontend: ## Run frontend tests only
	cd frontend && npm test

test-cov: ## Run tests with coverage
	cd backend && pytest --cov=app --cov-report=html
	cd frontend && npm run test:coverage

# Linting and Formatting
lint: ## Run linters (backend + frontend)
	@echo "Linting backend..."
	cd backend && flake8 .
	cd backend && mypy .
	@echo "Linting frontend..."
	cd frontend && npm run lint

lint-fix: ## Auto-fix linting issues
	cd backend && black .
	cd backend && isort .
	cd frontend && npm run lint:fix

format: lint-fix ## Format code (alias for lint-fix)

type-check: ## Run type checking
	cd backend && mypy .
	cd frontend && npm run type-check

# Build Commands
build: ## Build Docker images
	docker-compose build

build-backend: ## Build backend Docker image
	cd backend && docker build -t onetrade-backend:latest .

build-frontend: ## Build frontend Docker image
	cd frontend && docker build -t onetrade-frontend:latest .

build-prod: ## Build production images
	cd frontend && npm run build
	docker-compose -f docker-compose.yml build

# Logs
logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-postgres: ## Show PostgreSQL logs
	docker-compose logs -f postgres

logs-redis: ## Show Redis logs
	docker-compose logs -f redis

logs-rabbitmq: ## Show RabbitMQ logs
	docker-compose logs -f rabbitmq

# Cleaning
clean: ## Clean temporary files and caches
	@echo "Cleaning Python cache..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaning Node modules cache..."
	cd frontend && rm -rf node_modules/.cache 2>/dev/null || true
	@echo "✅ Cleanup complete!"

clean-all: clean ## Deep clean (including node_modules and venv)
	@echo "⚠️  This will remove node_modules and venv! Press Ctrl+C to cancel..."
	@sleep 5
	rm -rf backend/venv
	rm -rf frontend/node_modules
	@echo "✅ Deep cleanup complete!"

# Production Commands
deploy: ## Deploy to production (requires configuration)
	@echo "🚀 Deploying to production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✅ Deployment complete!"

# Health Check
health: ## Check health of all services
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Backend is down"
	@curl -f http://localhost:5173/health || echo "❌ Frontend is down"
	@docker-compose ps

