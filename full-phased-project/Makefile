# Full Phased Data Engineering Project Makefile

.PHONY: help install setup clean test lint format run-all run-phase1 run-phase2 run-phase3 deploy-infrastructure deploy-applications docker-up docker-down logs

# Default target
help:
	@echo "Available commands:"
	@echo "  install              - Install Python dependencies"
	@echo "  setup                - Setup project environment and databases"
	@echo "  clean                - Clean up temporary files and cache"
	@echo "  test                 - Run all tests"
	@echo "  test-phase1          - Run Phase 1 tests"
	@echo "  test-phase2          - Run Phase 2 tests"
	@echo "  test-phase3          - Run Phase 3 tests"
	@echo "  lint                 - Run code linting"
	@echo "  format               - Format code with black"
	@echo "  run-all              - Run all phases"
	@echo "  run-phase1           - Run Phase 1 (Batch ETL)"
	@echo "  run-phase2           - Run Phase 2 (Streaming & Orchestration)"
	@echo "  run-phase3           - Run Phase 3 (Cloud Pipeline)"
	@echo "  docker-up            - Start all Docker services"
	@echo "  docker-down          - Stop all Docker services"
	@echo "  logs                 - Show Docker logs"
	@echo "  deploy-infrastructure - Deploy cloud infrastructure"
	@echo "  deploy-applications  - Deploy applications"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Setup project environment
setup: install
	@echo "Setting up project environment..."
	mkdir -p data/{raw,processed,output} logs
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Running database setup..."
	python scripts/setup/setup_databases.py

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/

# Testing
test:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-phase1:
	pytest phase1-batch-etl/tests/ -v

test-phase2:
	pytest phase2-streaming-orchestration/tests/ -v

test-phase3:
	pytest phase3-cloud-pipeline/tests/ -v

# Code quality
lint:
	flake8 --max-line-length=88 --extend-ignore=E203 .
	pylint --rcfile=.pylintrc phase1-batch-etl/ phase2-streaming-orchestration/ phase3-cloud-pipeline/ shared/

format:
	black --line-length=88 .
	isort .

# Run phases
run-all: run-phase1 run-phase2 run-phase3

run-phase1:
	@echo "Running Phase 1: Batch ETL Pipeline"
	cd phase1-batch-etl && python src/etl_pipeline.py

run-phase2:
	@echo "Running Phase 2: Streaming & Orchestration"
	cd phase2-streaming-orchestration && python kafka/producer.py &
	cd phase2-streaming-orchestration && python kafka/consumer.py

run-phase3:
	@echo "Running Phase 3: Cloud Pipeline"
	@echo "Note: Requires AWS credentials and deployed infrastructure"
	cd phase3-cloud-pipeline && python src/trigger_glue_job.py

# Docker operations
docker-up:
	docker-compose up -d
	@echo "Services starting... Wait a few moments then check:"
	@echo "  - Kafka UI: http://localhost:8080"
	@echo "  - Airflow: http://localhost:8081"
	@echo "  - Grafana: http://localhost:3000"
	@echo "  - Prometheus: http://localhost:9090"

docker-down:
	docker-compose down

docker-restart: docker-down docker-up

logs:
	docker-compose logs -f

# Database operations
db-reset:
	docker-compose exec postgres psql -U data_eng -d data_engineering -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	python scripts/setup/setup_databases.py

# Deployment
deploy-infrastructure:
	@echo "Deploying cloud infrastructure..."
	cd phase3-cloud-pipeline/terraform && terraform init && terraform plan && terraform apply

deploy-applications:
	@echo "Deploying applications..."
	python scripts/deployment/deploy.py

# Development helpers
dev-setup: install setup docker-up
	@echo "Development environment ready!"
	@echo "Access points:"
	@echo "  - Kafka UI: http://localhost:8080"
	@echo "  - Airflow: http://localhost:8081 (admin/admin)"
	@echo "  - Grafana: http://localhost:3000 (admin/admin)"

# Monitoring
monitor:
	@echo "Opening monitoring dashboards..."
	open http://localhost:3000  # Grafana
	open http://localhost:9090  # Prometheus

# Data operations
load-sample-data:
	python scripts/setup/load_sample_data.py

# Backup and restore
backup:
	mkdir -p backups
	docker-compose exec postgres pg_dump -U data_eng data_engineering > backups/postgres_backup_$(shell date +%Y%m%d_%H%M%S).sql

restore:
	@echo "Usage: make restore BACKUP_FILE=backups/postgres_backup_YYYYMMDD_HHMMSS.sql"
	docker-compose exec -T postgres psql -U data_eng -d data_engineering < $(BACKUP_FILE)

# Security
security-check:
	safety check
	bandit -r . -x tests/

# Performance testing
performance-test:
	python scripts/testing/performance_test.py

# Documentation
docs:
	@echo "Generating documentation..."
	sphinx-build -b html docs/ docs/_build/html
	@echo "Documentation available at docs/_build/html/index.html"