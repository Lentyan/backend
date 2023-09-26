SHELL := /bin/bash
LOCAL_COMPOSE_FILE := infra/dev/docker-compose.local.yaml

COLOR_RESET = \033[0m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m
COLOR_WHITE = \033[00m

.DEFAULT_GOAL := help
.PHONY: help
help:  # Show help
	@echo -e "$(COLOR_GREEN)Makefile help:"
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "$(COLOR_GREEN)-$$(echo $$l | cut -f 1 -d':'):$(COLOR_WHITE)$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: run-database
run-database: # Run PostgreSQL container
	@if command -v docker &> /dev/null; then \
        docker-compose -f $(LOCAL_COMPOSE_FILE) up -d; \
    else \
        echo "Docker is not installed"; \
    fi

.PHONY: migrate
migrate: # Commit migrations to Database
	@echo -e "$(COLOR_YELLOW)Migrating...$(COLOR_RESET)"
	@until poetry run python manage.py migrate; do \
	  echo "Waiting for migrations..."; \
	  sleep 5; \
	done
	@sleep 3;
	@echo -e "$(COLOR_GREEN)Migrated$(COLOR_RESET)"

.PHONY: run-django-app-devserver
run-django-app-devserver: # Run Django dev server
	@echo -e "$(COLOR_YELLOW)Start Django dev server...$(COLOR_RESET)"
	@until poetry run python manage.py runserver; do \
	  echo "Waiting for Django dev server..."; \
	  sleep 5; \
	done
	@sleep 3;
	@echo -e "$(COLOR_GREEN)Dev server is running$(COLOR_RESET)"

.PHONY: run-dev
run-dev: run-database migrate run-django-app-devserver # Run application for dev:
	@echo -e "$(COLOR_YELLOW)Starting dev environment...$(COLOR_RESET)"
	@source $$(poetry env info -p)/bin/activate
