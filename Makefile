.PHONY: help install dev test test-integration integration lint type-check format clean start stop logs restart restart-no-cache wait-for-services status export-pr-comments analyze-pr-comments analyze-pr-comments-latest export-and-analyze-pr export-and-analyze-pr-latest

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
export-pr-comments: ## Export GitHub PR comments to JSON (requires PR=<number>)
	@if [ -z "$(PR)" ]; then \
		echo "Error: PR number required. Usage: make export-pr-comments PR=123"; \
		exit 1; \
	fi
	@echo "Exporting PR #$(PR) comments..."
	@chmod +x scripts/github-pr-tools/export_github_pr_comments.sh
	@./scripts/github-pr-tools/export_github_pr_comments.sh $(PR)
	@echo "✅ Comments exported to scripts/github-pr-tools/output/pr_$(PR)_comments.json"
	@echo "💡 You can now feed this JSON to an LLM for analysis"

analyze-pr-comments: ## Analyze PR comments and generate LLM prompt (requires PR=<number>)
	@if [ -z "$(PR)" ]; then \
		echo "Error: PR number required. Usage: make analyze-pr-comments PR=123"; \
		exit 1; \
	fi
	@echo "Analyzing PR #$(PR) comments..."
	@python scripts/github-pr-tools/analyze_pr_comments.py scripts/github-pr-tools/output/pr_$(PR)_comments.json

analyze-pr-comments-latest: ## Analyze only the latest PR review (requires PR=<number>)
	@if [ -z "$(PR)" ]; then \
		echo "Error: PR number required. Usage: make analyze-pr-comments-latest PR=123"; \
		exit 1; \
	fi
	@echo "Analyzing latest review for PR #$(PR)..."
	@python scripts/github-pr-tools/analyze_pr_comments.py scripts/github-pr-tools/output/pr_$(PR)_comments.json --latest-only

export-and-analyze-pr: ## Export and analyze PR comments in one command (requires PR=<number>)
	@if [ -z "$(PR)" ]; then \
		echo "Error: PR number required. Usage: make export-and-analyze-pr PR=123"; \
		exit 1; \
	fi
	@echo "🚀 Exporting and analyzing PR #$(PR) comments..."
	@$(MAKE) export-pr-comments PR=$(PR)
	@$(MAKE) analyze-pr-comments PR=$(PR)
	@echo "✅ Complete! Files ready in scripts/github-pr-tools/output/"
	@echo "💡 Open scripts/github-pr-tools/output/pr_$(PR)_comments_llm_prompt.txt in Cursor"

export-and-analyze-pr-latest: ## Export and analyze latest PR review in one command (requires PR=<number>)
	@if [ -z "$(PR)" ]; then \
		echo "Error: PR number required. Usage: make export-and-analyze-pr-latest PR=123"; \
		exit 1; \
	fi
	@echo "🚀 Exporting and analyzing latest review for PR #$(PR)..."
	@$(MAKE) export-pr-comments PR=$(PR)
	@$(MAKE) analyze-pr-comments-latest PR=$(PR)
	@echo "✅ Complete! Files ready in scripts/github-pr-tools/output/"
	@echo "💡 Open scripts/github-pr-tools/output/pr_$(PR)_comments_latest_review_llm_prompt.txt in Cursor"
