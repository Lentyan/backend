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

.PHONY: run-local
run-local: # Run Application locally
	@if command -v docker &> /dev/null; then \
        docker-compose -f $(LOCAL_COMPOSE_FILE) up -d; \
    else \
        echo "Docker is not installed"; \
    fi