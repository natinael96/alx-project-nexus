.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs from all services
	docker-compose logs -f

logs-web: ## View logs from web service
	docker-compose logs -f web

logs-db: ## View logs from database service
	docker-compose logs -f db

shell: ## Open Django shell
	docker-compose exec web python manage.py shell

bash: ## Open bash shell in web container
	docker-compose exec web bash

migrate: ## Run database migrations
	docker-compose exec web python manage.py migrate

makemigrations: ## Create new migrations
	docker-compose exec web python manage.py makemigrations

createsuperuser: ## Create Django superuser
	docker-compose exec web python manage.py createsuperuser

test: ## Run all tests with pytest
	docker-compose exec web pytest

test-cov: ## Run tests with coverage report
	docker-compose exec web pytest --cov=apps --cov-report=html --cov-report=term-missing

test-verbose: ## Run tests with verbose output
	docker-compose exec web pytest -v

test-accounts: ## Run account tests only
	docker-compose exec web pytest tests/test_accounts.py -v

test-jobs: ## Run job tests only
	docker-compose exec web pytest tests/test_jobs.py -v

test-models: ## Run model tests only
	docker-compose exec web pytest tests/test_models.py -v

test-integration: ## Run integration tests only
	docker-compose exec web pytest tests/test_integration.py -v

collectstatic: ## Collect static files
	docker-compose exec web python manage.py collectstatic --noinput

clean: ## Remove containers, volumes, and images
	docker-compose down -v
	docker system prune -f

reset-db: ## Reset database (WARNING: Deletes all data)
	docker-compose down -v
	docker volume rm jobboard_postgres_data || true
	docker-compose up -d db
	sleep 5
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py createsuperuser

setup: ## Initial setup - build, up, migrate, collectstatic
	make build
	make up
	sleep 5
	make migrate
	make collectstatic
	@echo "Setup complete! Run 'make createsuperuser' to create an admin user."

