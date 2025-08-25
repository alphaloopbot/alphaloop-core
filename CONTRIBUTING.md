# Contributing to AlphaLoop Core

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/alphaloopbot/alphaloop-core.git
   cd alphaloop-core
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Run tests**
   ```bash
   # Unit tests only (default)
   make test

   # All tests (including integration)
   poetry run pytest tests/ -v
   ```

## Code Quality

- **Linting**: `poetry run ruff check .`
- **Type checking**: `poetry run mypy .`
- **Formatting**: `poetry run ruff format .`

## Testing Strategy

- **Unit tests**: Run by default in CI
- **Integration tests**: Skipped in CI (API not implemented yet)
- **Infrastructure tests**: Run locally with `make test-infrastructure`

## Pull Request Process

1. Create a feature branch from `develop`
2. Make your changes
3. Ensure all tests pass: `make test`
4. Ensure code quality checks pass: `make lint`
5. Submit a pull request

## CI/CD

- **Unit tests only** are required for merge
- Integration tests are skipped until API is implemented
- All code quality checks must pass

## Architecture

- **alphaloop-core**: Main business logic
- **infrastructure modules**: Internal modules in `src/infrastructure/`
- **Docker services**: Thin wrappers around core logic
