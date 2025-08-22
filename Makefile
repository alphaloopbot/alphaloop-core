.PHONY: help install dev test test-integration integration lint type-check format clean start stop logs restart restart-no-cache wait-for-services status github-pr-export github-pr-analyze github-pr-latest

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	poetry install

dev: ## Install development dependencies and run full development cycle
	$(MAKE) install
	poetry install --with dev
	pre-commit install
	@echo "Running full development cycle..."
	@echo "1. Formatting code..."
	@$(MAKE) format
	@echo "2. Running linting..."
	@$(MAKE) lint
	@echo "3. Running type checking..."
	@$(MAKE) type-check
	@echo "4. Running tests..."
	@$(MAKE) test
	@echo "Development cycle complete! ✨"

test: ## Run unit tests
	poetry run pytest tests/unit/ -v

test-integration: ## Run integration tests (requires running services)
	poetry run pytest tests/integration/ -v

integration: restart-no-cache wait-for-services test-integration ## Restart services and run integration tests
	@echo "Integration testing complete! ✨"

lint: ## Run linting
	poetry run ruff check .

type-check: ## Run type checking with smart filtering
	poetry run mypy src/alphaloop_core/ --ignore-missing-imports --disable-error-code=misc --disable-error-code=unused-ignore --disable-error-code=unreachable --disable-error-code=no-any-return --disable-error-code=dict-item --disable-error-code=attr-defined --disable-error-code=index --disable-error-code=var-annotated --disable-error-code=operator --disable-error-code=call-overload --disable-error-code=union-attr --disable-error-code=no-untyped-def

format: ## Format code
	poetry run ruff format .
	poetry run ruff check --fix .

clean: ## Clean up build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

start: ## Start all services
	docker compose up -d

stop: ## Stop all services
	docker compose down

restart: stop start ## Restart all services

restart-no-cache: ## Restart all services with fresh Docker builds (no cache)
	docker compose down
	docker compose build --no-cache
	docker compose up -d

wait-for-services: ## Wait for services needed by integration tests
	@echo "Waiting for services needed by integration tests..."
	@echo "Waiting for Database..."
	@until docker compose exec -T database pg_isready -U postgres > /dev/null 2>&1; do sleep 1; done
	@echo "Waiting for API..."
	@until curl -s http://localhost:8000/health > /dev/null 2>&1; do sleep 1; done
	@echo "Integration tests ready! ✨"

logs: ## Show logs from all services
	docker compose logs -f

status: ## Show service status
	docker compose ps

run-api: ## Run the API locally
	poetry run uvicorn src.alphaloop_core.api:app --reload --host 0.0.0.0 --port 8000

run-cli: ## Run the CLI
	poetry run alphaloop-cli --help

# GitHub PR Tools
github-pr-export: ## Export GitHub PR comments (usage: make github-pr-export PR_NUMBER=123)
	@if [ -z "$(PR_NUMBER)" ]; then \
		echo "Error: PR_NUMBER is required. Usage: make github-pr-export PR_NUMBER=123"; \
		exit 1; \
	fi
	@echo "Exporting comments for PR #$(PR_NUMBER)..."
	@mkdir -p scripts/github-pr-tools/output
	@./scripts/github-pr-tools/export_github_pr_comments.sh $(PR_NUMBER)
	@echo "Comments exported to scripts/github-pr-tools/output/pr_$(PR_NUMBER)_comments.json"

github-pr-analyze: ## Analyze GitHub PR comments (usage: make github-pr-analyze PR_NUMBER=123)
	@if [ -z "$(PR_NUMBER)" ]; then \
		echo "Error: PR_NUMBER is required. Usage: make github-pr-analyze PR_NUMBER=123"; \
		exit 1; \
	fi
	@echo "Analyzing comments for PR #$(PR_NUMBER)..."
	@python scripts/github-pr-tools/analyze_pr_comments.py scripts/github-pr-tools/output/pr_$(PR_NUMBER)_comments.json
	@echo "Analysis complete! Check the output above for insights."

github-pr-latest: ## Export and analyze the latest PR comments (usage: make github-pr-latest PR_NUMBER=123)
	@if [ -z "$(PR_NUMBER)" ]; then \
		echo "Error: PR_NUMBER is required. Usage: make github-pr-latest PR_NUMBER=123"; \
		exit 1; \
	fi
	@echo "Processing latest comments for PR #$(PR_NUMBER)..."
	@$(MAKE) github-pr-export PR_NUMBER=$(PR_NUMBER)
	@$(MAKE) github-pr-analyze PR_NUMBER=$(PR_NUMBER)
	@echo "Complete analysis finished! ✨"
