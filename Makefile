# Database Mechanics - Development Commands

.PHONY: help clean test format lint check-all setup-python setup-java

help:
	@echo "Database Mechanics Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup-python    Set up Python development environment"
	@echo "  setup-java      Set up Java development environment"
	@echo ""
	@echo "Development Commands:"
	@echo "  test           Run tests for both Python and Java"
	@echo "  format         Format code in both languages"
	@echo "  lint           Run linting for both languages"
	@echo "  check-all      Run all quality checks"
	@echo "  clean          Clean build artifacts"

# Setup commands
setup-python:
	cd python && pip install -e ".[dev]" && pre-commit install

setup-java:
	cd java && mvn dependency:resolve

# Test commands
test:
	@echo "Running Python tests..."
	cd python && python -m pytest
	@echo "Running Java tests..."
	cd java && mvn test

# Format commands
format:
	@echo "Formatting Python code..."
	cd python && black src/ tests/ && isort src/ tests/
	@echo "Formatting Java code..."
	cd java && mvn spotless:apply

# Lint commands
lint:
	@echo "Linting Python code..."
	cd python && flake8 src/ tests/ && mypy src/
	@echo "Checking Java code..."
	cd java && mvn spotless:check

# Quality checks
check-all:
	@echo "Running all quality checks..."
	cd python && pre-commit run --all-files
	cd java && mvn clean verify

# Clean
clean:
	@echo "Cleaning Python artifacts..."
	cd python && rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	@echo "Cleaning Java artifacts..."
	cd java && mvn clean