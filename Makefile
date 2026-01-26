.PHONY: help install run backend frontend init-db test clean docker-build docker-run format lint

# Variables
PYTHON := python3
PIP := pip3
VENV := venv
BACKEND_DIR := backend
FRONTEND_DIR := frontend/streamlit

help:
	@echo "Expense AI Assistant - Available Commands"
	@echo "=========================================="
	@echo ""
	@echo "Installation & Setup:"
	@echo "  make install          - Install all dependencies"
	@echo "  make venv             - Create the virtual environment"
	@echo "  make init-db          - Initialize database with sample data"
	@echo "  make init-db-empty    - Initialize an empty database"
	@echo ""
	@echo "Execution:"
	@echo "  make run              - Start both backend and frontend"
	@echo "  make backend          - Start only the backend"
	@echo "  make frontend         - Start only the frontend"
	@echo ""
	@echo "Development:"
	@echo "  make test             - Run tests"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make format           - Format code using Black"
	@echo "  make lint             - Lint code using Flake8"
	@echo "  make clean            - Clean temporary files"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-run       - Run using Docker Compose"
	@echo "  make docker-stop      - Stop containers"
	@echo "  make docker-clean     - Clean containers and images"
	@echo ""
	@echo "Utilities:"
	@echo "  make logs             - Show application logs"
	@echo "  make shell            - Open a Python shell with context loaded"
	@echo "  make backup-db        - Create a database backup"
	@echo ""

# Installation
venv:
	@echo "📦 Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "✅ Virtual environment created"

install: venv
	@echo "📦 Installing dependencies..."
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

# Initialization
init-db:
	@echo "🗄️  Initializing database with sample data..."
	. $(VENV)/bin/activate && $(PYTHON) scripts/init_db.py
	@echo "✅ Database initialized"

init-db-empty:
	@echo "🗄️  Initializing empty database..."
	. $(VENV)/bin/activate && $(PYTHON) -c "from backend.models.database import init_db; init_db()"
	@echo "✅ Database initialized"

# Execution
backend:
	@echo "🚀 Starting Backend (FastAPI)..."
	. $(VENV)/bin/activate && $(PYTHON) $(BACKEND_DIR)/api/main.py

frontend:
	@echo "🎨 Starting Frontend (Streamlit)..."
	. $(VENV)/bin/activate && streamlit run $(FRONTEND_DIR)/app.py

run:
	@echo "🚀 Starting full application..."
	@echo "Use Ctrl+C to stop"
	@make -j2 backend frontend

# Testing
test:
	@echo "🧪 Running tests..."
	. $(VENV)/bin/activate && pytest tests/ -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	. $(VENV)/bin/activate && pytest tests/ --cov=$(BACKEND_DIR) --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated in htmlcov/"

# Code Quality
format:
	@echo "🎨 Formatting code with Black..."
	. $(VENV)/bin/activate && black $(BACKEND_DIR)/ $(FRONTEND_DIR)/ tests/
	@echo "✅ Code formatted"

lint:
	@echo "🔍 Linting code with Flake8..."
	. $(VENV)/bin/activate && flake8 $(BACKEND_DIR)/ --max-line-length=100 --exclude=venv
	@echo "✅ Linting completed"

# Cleanup
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed"

clean-all: clean
	@echo "🧹 Deep cleaning..."
	rm -rf $(VENV)
	rm -rf data/database/*.db
	rm -rf data/raw/*
	rm -rf backend/ml/saved_models/*.pkl
	rm -rf logs/*.log
	@echo "✅ Deep cleaning completed"

# Docker
docker-build:
	@echo "🐳 Building Docker images..."
	cd docker && docker-compose build
	@echo "✅ Images built"

docker-run:
	@echo "🐳 Starting with Docker Compose..."
	cd docker && docker-compose up

docker-stop:
	@echo "🐳 Stopping containers..."
	cd docker && docker-compose down
	@echo "✅ Containers stopped"

docker-clean:
	@echo "🐳 Cleaning Docker environment..."
	cd docker && docker-compose down -v --rmi all
	@echo "✅ Docker environment cleaned"

# Utilities
logs:
	@echo "📋 Showing logs..."
	tail -f logs/app.log

shell:
	@echo "🐍 Opening Python shell..."
	. $(VENV)/bin/activate && PYTHONPATH=. $(PYTHON)

backup-db:
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	@cp data/database/expenses.db backups/expenses_backup_$$(date +%Y%m%d_%H%M%S).db
	@echo "✅ Backup created in backups/"

# Development
dev-setup: install init-db
	@echo "✅ Development environment configured"
	@echo ""
	@echo "Next steps:"
	@echo "1. Activate virtual environment: source venv/bin/activate"
	@echo "2. Run application: make run"
	@echo "3. Access via http://localhost:8501"

# Database
migrate:
	@echo "🗄️  Running migrations..."
	. $(VENV)/bin/activate && alembic upgrade head
	@echo "✅ Migrations applied"

migrate-create:
	@echo "🗄️  Creating new migration..."
	@read -p "Migration name: " name; \
	. $(VENV)/bin/activate && alembic revision --autogenerate -m "$$name"
	@echo "✅ Migration created"

# Deployment
deploy-prod:
	@echo "🚀 Deploying to production..."
	@echo "⚠️  Ensure you have configured production environment variables"
	@read -p "Continue? (y/n): " confirm; \
	if [ "$$confirm" = "y" ]; then \
		make docker-build && make docker-run; \
	fi

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@echo "API Docs available at: http://localhost:8000/docs"
	@echo "Open your browser at that URL after starting the backend"

# Monitoring
status:
	@echo "📊 Application Status:"
	@echo ""
	@if pgrep -f "uvicorn" > /dev/null; then \
		echo "✅ Backend: Running"; \
	else \
		echo "❌ Backend: Stopped"; \
	fi
	@if pgrep -f "streamlit" > /dev/null; then \
		echo "✅ Frontend: Running"; \
	else \
		echo "❌ Frontend: Stopped"; \
	fi
	@if [ -f "data/database/expenses.db" ]; then \
		echo "✅ Database: Exists"; \
	else \
		echo "❌ Database: Not found"; \
	fi
