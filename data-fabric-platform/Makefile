.PHONY: help setup install clean test lint format run-local deploy-azure deploy-aws deploy-multi-cloud

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
VENV := venv
DOCKER_COMPOSE := docker-compose

# Help
help:
	@echo "Data Fabric Platform - Makefile Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup           - Complete environment setup"
	@echo "  make install         - Install Python dependencies"
	@echo "  make venv            - Create virtual environment"
	@echo ""
	@echo "Development:"
	@echo "  make run-local       - Run platform locally"
	@echo "  make run-etl         - Run ETL pipeline"
	@echo "  make run-migration   - Run data migration"
	@echo "  make notebook        - Start Jupyter notebook"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run all tests"
	@echo "  make test-unit       - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-e2e        - Run end-to-end tests"
	@echo "  make test-coverage   - Run tests with coverage"
	@echo ""
	@echo "Quality:"
	@echo "  make lint            - Run linters"
	@echo "  make format          - Format code"
	@echo "  make type-check      - Run type checking"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    - Build Docker images"
	@echo "  make docker-up       - Start Docker services"
	@echo "  make docker-down     - Stop Docker services"
	@echo "  make docker-logs     - View Docker logs"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-azure    - Deploy to Azure"
	@echo "  make deploy-aws      - Deploy to AWS"
	@echo "  make deploy-multi-cloud - Deploy to both clouds"
	@echo "  make terraform-init  - Initialize Terraform"
	@echo "  make terraform-plan  - Plan Terraform changes"
	@echo "  make terraform-apply - Apply Terraform changes"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean           - Clean generated files"
	@echo "  make clean-all       - Clean everything including venv"
	@echo "  make docs            - Generate documentation"

# Setup & Installation
setup: venv install docker-build
	@echo "✅ Setup complete!"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "✅ Virtual environment created"

install:
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

# Development
run-local:
	@echo "Starting Data Fabric Platform locally..."
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Platform started on http://localhost:8080"

run-etl:
	@echo "Running ETL pipeline..."
	$(PYTHON) src/etl/pyspark_jobs/bronze_to_silver.py

run-migration:
	@echo "Running data migration..."
	$(PYTHON) src/migration/hadoop_to_cloud.py

notebook:
	@echo "Starting Jupyter notebook..."
	jupyter notebook notebooks/

# Testing
test:
	@echo "Running all tests..."
	pytest tests/ -v

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/ -v

test-e2e:
	@echo "Running end-to-end tests..."
	pytest tests/e2e/ -v

test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/"

# Quality
lint:
	@echo "Running linters..."
	flake8 src/ tests/
	pylint src/
	@echo "✅ Linting complete"

format:
	@echo "Formatting code..."
	black src/ tests/ examples/
	@echo "✅ Code formatted"

type-check:
	@echo "Running type checking..."
	mypy src/
	@echo "✅ Type checking complete"

# Docker
docker-build:
	@echo "Building Docker images..."
	$(DOCKER_COMPOSE) build
	@echo "✅ Docker images built"

docker-up:
	@echo "Starting Docker services..."
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Docker services started"

docker-down:
	@echo "Stopping Docker services..."
	$(DOCKER_COMPOSE) down
	@echo "✅ Docker services stopped"

docker-logs:
	$(DOCKER_COMPOSE) logs -f

# Deployment
deploy-azure:
	@echo "Deploying to Azure..."
	cd infrastructure/terraform/azure && terraform init && terraform apply -auto-approve
	bash scripts/deployment/deploy_to_azure.sh
	@echo "✅ Deployed to Azure"

deploy-aws:
	@echo "Deploying to AWS..."
	cd infrastructure/terraform/aws && terraform init && terraform apply -auto-approve
	bash scripts/deployment/deploy_to_aws.sh
	@echo "✅ Deployed to AWS"

deploy-multi-cloud:
	@echo "Deploying to multi-cloud..."
	$(MAKE) deploy-azure
	$(MAKE) deploy-aws
	@echo "✅ Multi-cloud deployment complete"

terraform-init:
	@echo "Initializing Terraform..."
	cd infrastructure/terraform/azure && terraform init
	cd infrastructure/terraform/aws && terraform init
	@echo "✅ Terraform initialized"

terraform-plan:
	@echo "Planning Terraform changes..."
	cd infrastructure/terraform/azure && terraform plan
	cd infrastructure/terraform/aws && terraform plan

terraform-apply:
	@echo "Applying Terraform changes..."
	cd infrastructure/terraform/azure && terraform apply
	cd infrastructure/terraform/aws && terraform apply

# Utilities
clean:
	@echo "Cleaning generated files..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type f -name '.coverage' -delete
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@echo "✅ Cleaned"

clean-all: clean
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "✅ All clean"

docs:
	@echo "Generating documentation..."
	cd docs && sphinx-build -b html . _build
	@echo "✅ Documentation generated in docs/_build/"

# Data operations
generate-sample-data:
	@echo "Generating sample data..."
	$(PYTHON) scripts/utils/data_generator.py

benchmark:
	@echo "Running performance benchmarks..."
	$(PYTHON) scripts/utils/performance_benchmark.py

# Monitoring
start-monitoring:
	@echo "Starting monitoring stack..."
	$(DOCKER_COMPOSE) -f docker-compose.monitoring.yml up -d
	@echo "✅ Grafana: http://localhost:3000"
	@echo "✅ Prometheus: http://localhost:9090"

stop-monitoring:
	$(DOCKER_COMPOSE) -f docker-compose.monitoring.yml down
