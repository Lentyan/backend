SHELL := /bin/bash
LOCAL_COMPOSE_FILE := infra/docker-compose.local.yaml

COLOR_RESET = \033[0m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m
COLOR_WHITE = \033[00m

.DEFAULT_GOAL := help
.PHONY: help
help:  # Show help
	@echo -e "$(COLOR_GREEN)Makefile help:"
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "$(COLOR_GREEN)-$$(echo $$l | cut -f 1 -d':'):$(COLOR_WHITE)$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: run-unittests
run-unittests: # Run Django unit tests:
	@echo -e "$(COLOR_YELLOW)Start Django unit tests...$(COLOR_RESET)"
	@until poetry run python src/manage.py test; do \
	  echo "Waiting for Django dev server..."; \
	  sleep 5; \
	done
	@sleep 3;
	@echo -e "$(COLOR_GREEN)Dev server is running$(COLOR_RESET)"

.PHONY: run-local
run-local: #Run Django DRF app with infrastructure
	@if command -v docker &> /dev/null; then \
        docker-compose -f $(LOCAL_COMPOSE_FILE) up -d; \
    else \
        echo "Docker is not installed"; \
    fi
