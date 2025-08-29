# AI Report Writer - Development Makefile
#
# Common development tasks for code quality, testing, and deployment
#
# Usage:
#   make help          - Show this help
#   make install       - Install all dependencies
#   make format        - Format code with black and isort
#   make lint          - Run all linting checks
#   make test          - Run test suite
#   make security      - Run security scans
#   make quality       - Run all quality checks
#   make clean         - Clean temporary files
#   make pre-commit    - Setup pre-commit hooks

.PHONY: help install format lint test security quality clean pre-commit

# Default target
help:
	@echo "🛠️  AI Report Writer - Development Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install all dependencies including dev tools"
	@echo "  make pre-commit    Setup pre-commit hooks"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format        Format code with black and isort"
	@echo "  make lint          Run linting checks (flake8, mypy)"
	@echo "  make security      Run security scans (bandit)"
	@echo "  make quality       Run all quality checks"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run full test suite"
	@echo "  make test-fast     Run fast tests only"
	@echo "  make coverage      Run tests with coverage report"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         Clean temporary files and caches"
	@echo "  make deps-check    Check for dependency updates"
	@echo ""

# Installation and setup
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

pre-commit:
	@echo "🔗 Setting up pre-commit hooks..."
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ Pre-commit hooks installed"

# Code formatting
format:
	@echo "🎨 Formatting code..."
	python -m isort .
	python -m black .
	@echo "✅ Code formatted"

# Linting and type checking
lint:
	@echo "🔍 Running linting checks..."
	python -m flake8
	python -m mypy breakdown ai_report_writer --ignore-missing-imports
	@echo "✅ Linting complete"

# Security scanning
security:
	@echo "🔒 Running security scans..."
	python -m bandit -r breakdown ai_report_writer -f json -o security_report.json || true
	python -m bandit -r breakdown ai_report_writer
	@echo "✅ Security scan complete"

# Combined quality checks
quality: format lint security
	@echo "🎯 All quality checks complete"

# Testing
test:
	@echo "🧪 Running full test suite..."
	python run_tests.py
	@echo "✅ Tests complete"

test-fast:
	@echo "⚡ Running fast tests..."
	python run_tests.py --fast
	@echo "✅ Fast tests complete"

coverage:
	@echo "📊 Running tests with coverage..."
	python run_tests.py --coverage
	@echo "✅ Coverage report generated"

# Maintenance
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f security_report.json 2>/dev/null || true
	@echo "✅ Cleanup complete"

deps-check:
	@echo "🔍 Checking for dependency updates..."
	pip list --outdated
	@echo "💡 Consider updating outdated packages"

# Django specific commands
migrate:
	@echo "🔄 Running Django migrations..."
	python manage.py makemigrations
	python manage.py migrate
	@echo "✅ Migrations complete"

collectstatic:
	@echo "📁 Collecting static files..."
	python manage.py collectstatic --noinput
	@echo "✅ Static files collected"

# Development server
runserver:
	@echo "🚀 Starting development server..."
	python manage.py runserver

# Production readiness
prod-check: quality test security
	@echo "🏭 Production readiness check complete"
	@echo "✅ System ready for deployment"
