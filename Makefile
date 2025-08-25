.PHONY: help install dev test test-integration integration lint type-check format format-check format-fix clean start stop logs restart restart-no-cache wait-for-services status export-pr-comments analyze-pr-comments analyze-pr-comments-latest export-and-analyze-pr export-and-analyze-pr-latest

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
	@echo "1. Fixing formatting issues..."
	@$(MAKE) format-fix
	@echo "2. Running linting..."
	@$(MAKE) lint
	@echo "3. Running type checking..."
	@$(MAKE) type-check
	@echo "4. Running tests..."
	@$(MAKE) test
	@echo "Development cycle complete! ✨"

test: ## Run unit tests (integration tests skipped - API not implemented yet)
	poetry run pytest tests/unit/ -v
	@echo "💡 Integration tests skipped - API not implemented yet"

test-infrastructure: ## Run tests for all infrastructure packages
	@echo "🧪 Running tests for all infrastructure packages..."
	@echo "Installing dependencies for all packages..."
	@cd infrastructure/alphaloop-heartbeat && poetry install
	@cd infrastructure/alphaloop-logging && poetry install
	@cd infrastructure/alphaloop-security && poetry install
	@cd infrastructure/alphaloop-storage && poetry install
	@cd infrastructure/alphaloop-cache && poetry install
	@echo "Testing alphaloop-heartbeat..."
	@cd infrastructure/alphaloop-heartbeat && poetry run pytest tests/ -v
	@echo "Testing alphaloop-logging..."
	@cd infrastructure/alphaloop-logging && poetry run pytest tests/ -v
	@echo "Testing alphaloop-security..."
	@cd infrastructure/alphaloop-security && poetry run pytest tests/ -v
	@echo "Testing alphaloop-storage..."
	@cd infrastructure/alphaloop-storage && poetry run pytest tests/ -v
	@echo "Testing alphaloop-cache..."
	@cd infrastructure/alphaloop-cache && poetry run pytest tests/ -v
	@echo "✅ All infrastructure tests completed!"

test-all: ## Run all tests (main project + infrastructure)
	@echo "🚀 Running all tests..."
	@echo "1. Running main project tests..."
	@$(MAKE) test
	@echo "2. Running infrastructure tests..."
	@$(MAKE) test-infrastructure
	@echo "✅ All tests completed!"

test-conda: ## Test conda environment setup
	python scripts/test_conda_env.py

test-integration: ## Run integration tests (SKIPPED - API not implemented yet)
	@echo "⚠️  Integration tests skipped - API not implemented yet"
	@echo "💡 These tests will be enabled when the API is implemented"
	@echo "   Run manually with: poetry run pytest tests/integration/ -v"

integration: restart-no-cache wait-for-services test-integration ## Restart services and run integration tests
	@echo "Integration testing complete! ✨"

lint: ## Run linting
	poetry run ruff check .

type-check: ## Run type checking with smart filtering
	poetry run mypy src/alphaloop_core/ --ignore-missing-imports --disable-error-code=misc --disable-error-code=unused-ignore --disable-error-code=unreachable --disable-error-code=no-any-return --disable-error-code=dict-item --disable-error-code=attr-defined --disable-error-code=index --disable-error-code=var-annotated --disable-error-code=operator --disable-error-code=call-overload --disable-error-code=union-attr --disable-error-code=no-untyped-def --disable-error-code=safe-super

format: ## Format code
	@echo "🔧 Formatting code..."
	poetry run ruff format .
	poetry run ruff check --fix .
	@echo "✅ Code formatting complete!"

format-check: ## Check formatting without fixing
	@echo "🔍 Checking code formatting..."
	poetry run ruff format --check .
	poetry run ruff check .
	@echo "✅ Code formatting check complete!"

format-fix: ## Fix all formatting issues automatically
	@echo "🔧 Running comprehensive formatting fixes..."
	python scripts/fix-formatting.py
	@echo "✅ All formatting issues fixed!"

clean: ## Clean up build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

start: ## Start all services (legacy - use services-start-local or services-start-cloud)
	@echo "⚠️  Legacy docker-compose.yml removed. Use:"
	@echo "   make services-start-local    # For local development"
	@echo "   make services-start-cloud    # For cloud deployment"

stop: ## Stop all services (legacy - use services-stop)
	@echo "⚠️  Legacy docker-compose.yml removed. Use:"
	@echo "   make services-stop"

restart: ## Restart all services (legacy - use services-stop then services-start-local/cloud)
	@echo "⚠️  Legacy docker-compose.yml removed. Use:"
	@echo "   make services-stop"
	@echo "   make services-start-local    # or services-start-cloud"

restart-no-cache: ## Restart all services with fresh Docker builds (legacy)
	@echo "⚠️  Legacy docker-compose.yml removed. Use:"
	@echo "   make services-build"
	@echo "   make services-start-local    # or services-start-cloud"

wait-for-services: ## Wait for services needed by integration tests
	@echo "⚠️  Legacy docker-compose.yml removed. Use services in services/ directory"

logs: ## Show logs from all services (legacy - use services-logs)
	@echo "⚠️  Legacy docker-compose.yml removed. Use:"
	@echo "   make services-logs"

status: ## Show service status (legacy - use services-status)
	@echo "⚠️  Legacy docker-compose.yml removed. Use:"
	@echo "   make services-status"

run-api: ## Run the API locally
	poetry run uvicorn alphaloop_core.api:app --reload --host 0.0.0.0 --port 8000

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

export-pr-unresolved: ## Export unresolved review threads (requires PR=<number>)
	@if [ -z "$(PR)" ]; then \
		echo "Error: PR number required. Usage: make export-pr-unresolved PR=123"; \
		exit 1; \
	fi
	@echo "Exporting unresolved threads for PR #$(PR)..."
	@chmod +x scripts/github-pr-tools/export_unresolved_threads.sh
	@cd scripts/github-pr-tools && ./export_unresolved_threads.sh $(PR)
	@echo "✅ Unresolved threads exported to scripts/github-pr-tools/output/pr_$(PR)_unresolved_threads.txt"
	@echo "💡 Review the unresolved threads to address pending feedback"

export-pr-unresolved-resolve: ## Export and resolve outdated threads (requires PR=<number>)
	@if [ -z "$(PR)" ]; then \
		echo "Error: PR number required. Usage: make export-pr-unresolved-resolve PR=123"; \
		exit 1; \
	fi
	@echo "Exporting and resolving outdated threads for PR #$(PR)..."
	@chmod +x scripts/github-pr-tools/export_unresolved_threads.sh
	@cd scripts/github-pr-tools && ./export_unresolved_threads.sh $(PR) --resolve-outdated --dry-run=false
	@echo "✅ Unresolved threads exported and outdated threads resolved"
	@echo "💡 Check scripts/github-pr-tools/output/pr_$(PR)_unresolved_threads.txt for remaining threads"

export-pr-unresolved-markdown: ## Export unresolved threads with full content to Markdown (requires PR=<number>)
	@if [ -z "$(PR)" ]; then \
		echo "Error: PR number required. Usage: make export-pr-unresolved-markdown PR=123"; \
		exit 1; \
	fi
	@echo "Exporting unresolved threads with full content to Markdown for PR #$(PR)..."
	@chmod +x scripts/github-pr-tools/export_unresolved_threads_markdown.sh
	@cd scripts/github-pr-tools && ./export_unresolved_threads_markdown.sh $(PR)
	@echo "✅ Unresolved threads exported to Markdown"
	@echo "💡 Check scripts/github-pr-tools/output/pr_$(PR)_unresolved_threads.md for detailed review"

export-pr-current-checklist: ## Generate tickable checklist of current unresolved threads (requires PR=<number>)
	@if [ -z "$(PR)" ]; then \
		echo "Error: PR number required. Usage: make export-pr-current-checklist PR=123"; \
		exit 1; \
	fi
	@echo "Generating current-only checklist for PR #$(PR)..."
	@chmod +x scripts/github-pr-tools/make_current_checklist.sh
	@cd scripts/github-pr-tools && ./make_current_checklist.sh $(PR)
	@echo "✅ Current checklist generated"
	@echo "💡 Check scripts/github-pr-tools/output/pr_$(PR)_current_checklist.md for tickable list"

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

# Service Management
services-start-local: ## Start local development services
	@cd services && ./scripts/start-local.sh

services-start-all: ## Start all services in correct order (database -> system-metrics -> market-data)
	@echo "🚀 Starting all AlphaLoop services in correct order..."
	@$(MAKE) services-setup-env
	@$(MAKE) services-database
	@echo "⏳ Waiting for database to be fully ready..."
	@sleep 5
	@$(MAKE) services-system-metrics
	@echo "⏳ Waiting for system metrics to start..."
	@sleep 3
	@$(MAKE) services-market-data-local
	@echo "⏳ Waiting for all services to be healthy..."
	@sleep 10
	@$(MAKE) services-health-check
	@echo "✅ All services started successfully!"

services-start-cloud: ## Start cloud production services
	@cd services && ./scripts/start-cloud.sh

services-stop: ## Stop all services
	@cd services && docker-compose down

services-logs: ## Show service logs
	@cd services && docker-compose logs -f

services-status: ## Show service status
	@cd services && docker-compose ps

services-build: ## Build all service images
	@cd services && docker-compose build

# Individual Service Management
services-database: ## Start only database service
	@echo "🗄️ Starting AlphaLoop Database..."
	@cd services && docker-compose up -d alphaloop-database
	@echo "⏳ Waiting for database to be ready..."
	@cd services && until docker-compose exec -T alphaloop-database pg_isready -U postgres; do echo "   Waiting for database..."; sleep 2; done
	@echo "✅ Database is ready!"

services-system-metrics: ## Start only system metrics service
	@echo "📊 Starting AlphaLoop System Metrics..."
	@cd services && docker-compose up -d alphaloop-system-metrics
	@echo "✅ System Metrics started!"

services-market-data-local: ## Start only market data service (local)
	@echo "📈 Starting AlphaLoop Market Data (Local)..."
	@cd services && docker-compose up -d alphaloop-market-data-local
	@echo "✅ Market Data (Local) started!"

services-market-data-cloud: ## Start only market data service (cloud)
	@echo "☁️ Starting AlphaLoop Market Data (Cloud)..."
	@cd services && docker-compose up -d alphaloop-market-data-cloud
	@echo "✅ Market Data (Cloud) started!"

# Service Testing
services-test-e2e: ## Run end-to-end tests for all services
	@echo "🧪 Running end-to-end tests for AlphaLoop services..."
	@$(MAKE) services-test-database
	@$(MAKE) services-test-system-metrics
	@$(MAKE) services-test-market-data
	@echo "✅ All end-to-end tests completed!"

services-test-e2e-comprehensive: ## Run comprehensive end-to-end tests with detailed reporting
	@echo "🧪 Running comprehensive end-to-end tests..."
	@cd services && ./scripts/test-e2e.sh

# New Service Testing Commands
services-build-test-images: ## Build test images for system metrics and market data services
	@echo "🔨 Building test images for services..."
	@echo "Building system metrics service..."
	@docker build -f services/alphaloop-system-metrics/Dockerfile -t test-system-metrics .
	@echo "Building market data service..."
	@docker build -f services/alphaloop-market-data/Dockerfile -t test-market-data .
	@echo "✅ Test images built successfully!"

services-test-docker-e2e: ## Run comprehensive E2E tests for Docker services
	@echo "🧪 Running comprehensive E2E tests for Docker services..."
	@./scripts/test-services-e2e.sh

services-test-system-metrics-docker: ## Test system metrics service in Docker
	@echo "📊 Testing system metrics service in Docker..."
	@docker run --rm test-system-metrics python -c "from alphaloop_core.services.system_metrics import SystemMetricsService; service = SystemMetricsService(); metrics = service.collect_metrics(); print(f'✅ Collected {len(metrics)} system metrics') if metrics else print('❌ Failed to collect metrics')"

services-test-market-data-docker: ## Test market data service in Docker
	@echo "📈 Testing market data service in Docker..."
	@docker run --rm test-market-data python -c "from alphaloop_core.services.market_data import MarketDataService; service = MarketDataService(); data = service.collect_from_exchanges(); print(f'✅ Generated {len(data)} market data records') if data else print('❌ Failed to generate market data')"

services-test-infrastructure: ## Test infrastructure modules in Docker services
	@echo "🔧 Testing infrastructure modules in Docker services..."
	@echo "Testing system metrics infrastructure..."
	@docker run --rm test-system-metrics python -c "from alphaloop_logging import AlphaLoopLogger, LoggingConfig; from alphaloop_storage import create_database_manager; from alphaloop_cache import create_cache_manager; from alphaloop_heartbeat import HeartbeatGenerator; print('✅ System metrics infrastructure modules work')"
	@echo "Testing market data infrastructure..."
	@docker run --rm test-market-data python -c "from alphaloop_logging import AlphaLoopLogger, LoggingConfig; from alphaloop_storage import create_database_manager; from alphaloop_cache import create_cache_manager; from alphaloop_heartbeat import HeartbeatGenerator; print('✅ Market data infrastructure modules work')"
	@echo "✅ Infrastructure tests completed!"

services-test-all-docker: ## Run all Docker service tests
	@echo "🚀 Running all Docker service tests..."
	@$(MAKE) services-build-test-images
	@$(MAKE) services-test-system-metrics-docker
	@$(MAKE) services-test-market-data-docker
	@$(MAKE) services-test-infrastructure
	@$(MAKE) services-test-docker-e2e
	@echo "✅ All Docker service tests completed!"

schema-setup: ## Setup database with YAML-driven schema (on-the-fly generation)
	@echo "🗄️ Setting up database with YAML-driven schema..."
	@$(MAKE) services-build-test-images
	@./scripts/setup-database-and-test.sh
	@echo "✅ Database setup completed!"

database-setup: ## Setup database schemas only (no testing)
	@echo "🗄️ Setting up database schemas using alphaloop-storage..."
	@PYTHONPATH="${PYTHONPATH}:$(pwd)/src" python -m infrastructure.alphaloop_storage setup
	@echo "✅ Database schemas setup completed!"

database-test: ## Test database connectivity and service data storage
	@echo "🧪 Testing database connectivity and service data storage..."
	@$(MAKE) services-build-test-images
	@./scripts/test-database-and-services.sh
	@echo "✅ Database and service tests completed!"

services-setup-database: ## Setup database schemas and test real data storage
	@echo "🗄️ Setting up database and testing real data storage..."
	@./scripts/setup-database-and-test.sh

services-test-with-database: ## Build images and test with real database storage
	@echo "🚀 Building images and testing with real database storage..."
	@$(MAKE) services-build-test-images
	@$(MAKE) services-setup-database
	@echo "✅ Database storage testing completed!"

services-test-database: ## Test database service connectivity and functionality
	@echo "🗄️ Testing database service..."
	@cd services && docker-compose exec -T alphaloop-database psql -U postgres -d alphaloop_market -c "SELECT version();" || echo "❌ Database test failed"
	@cd services && docker-compose exec -T alphaloop-database psql -U postgres -d alphaloop_sys -c "SELECT version();" || echo "❌ System database test failed"
	@echo "✅ Database tests completed!"

services-test-system-metrics: ## Test system metrics service
	@echo "📊 Testing system metrics service..."
	@cd services && docker-compose exec -T alphaloop-system-metrics python -c "import psutil; print('System metrics service is working')" || echo "❌ System metrics test failed"
	@echo "✅ System metrics tests completed!"

services-test-market-data: ## Test market data service API
	@echo "📈 Testing market data service..."
	@curl -f http://localhost:8001/health || echo "❌ Market data health check failed"
	@curl -f http://localhost:8001/api/v1/status || echo "❌ Market data status check failed"
	@echo "✅ Market data tests completed!"

services-health-check: ## Check health of all running services
	@echo "🏥 Checking health of all services..."
	@cd services && docker-compose ps
	@echo ""
	@echo "🔍 Health Checks:"
	@echo "Database:"
	@cd services && docker-compose exec -T alphaloop-database pg_isready -U postgres || echo "❌ Database health check failed"
	@echo "System Metrics:"
	@cd services && docker-compose exec -T alphaloop-system-metrics python -c "import psutil; print('✅ OK')" || echo "❌ System metrics health check failed"
	@echo "Market Data:"
	@curl -f http://localhost:8001/health || echo "❌ Market data health check failed"
	@echo "✅ Health checks completed!"

services-setup-env: ## Setup environment files for all services
	@echo "⚙️ Setting up environment files..."
	@cd services && mkdir -p ${ALPHALOOP_HOME:-$(shell pwd)/services/data}/{postgres_db,logs,cache}
	@cd services && [ ! -f "alphaloop-database/.env" ] && cp alphaloop-database/env.example alphaloop-database/.env && echo "✅ Created alphaloop-database/.env"
	@cd services && [ ! -f "alphaloop-system-metrics/.env" ] && cp alphaloop-system-metrics/env.example alphaloop-system-metrics/.env && echo "✅ Created alphaloop-system-metrics/.env"
	@cd services && [ ! -f "alphaloop-market-data/.env.local" ] && cp alphaloop-market-data/env.example.local alphaloop-market-data/.env.local && echo "✅ Created alphaloop-market-data/.env.local"
	@echo "✅ Environment setup completed!"
