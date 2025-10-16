# Simplified Makefile for Jira Data Pipeline

.PHONY: help build up down logs clean test pipeline

help: ## Show available commands
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Docker Operations
build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs
	docker-compose logs -f

clean: ## Clean containers and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

# Pipeline Operations
pipeline: ## Run full pipeline
	docker-compose run --rm pipeline

extract: ## Run data extraction only
	docker-compose run --rm pipeline extract

transform: ## Run data transformation only
	docker-compose run --rm pipeline transform

test: ## Run dbt tests
	docker-compose run --rm pipeline test

# Development
dev: ## Run pipeline locally
	python run_pipeline.py

monitor: ## Run monitoring
	python monitor.py

# Database
db: ## Connect to PostgreSQL
	docker-compose exec postgres psql -U dlt_user -d jira_dw

# Quick Start
start: build up pipeline ## Build, start services and run pipeline