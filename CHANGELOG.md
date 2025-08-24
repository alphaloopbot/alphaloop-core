# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.0.2-foundation] - 2025-08-24 - Foundation

### Added
- **Infrastructure Packages**: Complete set of reusable infrastructure packages
  - `alphaloop-logging`: Structured logging with multiple handlers and async support
  - `alphaloop-storage`: YAML-driven database schema management with lazy table creation
  - `alphaloop-cache`: Redis-based caching with TTL support
  - `alphaloop-security`: HMAC-SHA256, Fernet encryption, and secure URL handling
  - `alphaloop-heartbeat`: File-based heartbeat monitoring system

- **Service Architecture**: Clean architecture with centralized logic
  - `alphaloop-core`: Central business logic and service orchestration
  - Docker services as thin wrappers around core functionality
  - Service factory pattern for infrastructure component management

- **Database Schema**: Normalized, YAML-driven schema design
  - Single source of truth in `config/database_schema.yaml`
  - Dynamic table creation from YAML specifications
  - Lazy table creation/update on first access
  - Support for metadata and time-series data separation

- **System Metrics Service**: Real-time system monitoring
  - CPU, memory, disk usage collection
  - Public IP address detection with fallback to NULL
  - 30-second collection intervals
  - Continuous data storage in PostgreSQL

- **Market Data Service**: Cryptocurrency price collection
  - Mock market data generation for BTC/USDT, ETH/USDT, ADA/USDT, DOT/USDT
  - 10-second collection intervals
  - Automatic metadata creation and linking
  - Price and volume data storage

- **Docker Infrastructure**: Production-ready containerization
  - Multi-stage Docker builds with Poetry dependency management
  - Health checks for all services
  - Non-root user security
  - Host networking for database connectivity

- **Development Tools**: Comprehensive development environment
  - Makefile with build, test, and deployment commands
  - End-to-end testing scripts
  - Database setup and testing automation
  - Linting and type checking support

### Changed
- **Project Structure**: Reorganized from monolithic to modular architecture
  - Moved from `packages/` to `infrastructure/` directory
  - Flattened infrastructure package structure
  - Centralized configuration management

- **Database Management**: Transitioned to YAML-driven schema
  - Eliminated hardcoded table definitions
  - Single source of truth for schema configuration
  - Dynamic SQL generation from YAML specifications

- **Logging System**: Implemented structured logging across all components
  - Replaced print statements with `alphaloop-logging`
  - Async logging with synchronous wrappers
  - Fallback logging for development environments

### Technical Improvements
- **Async/Sync Integration**: Proper handling of asynchronous operations
  - Event loop management for async operations in sync contexts
  - Synchronous wrappers for async infrastructure components
  - Proper coroutine handling and cleanup

- **Error Handling**: Robust error handling and recovery
  - Graceful fallbacks for network connectivity issues
  - Database connection error recovery
  - Service health monitoring and restart capabilities

- **Configuration Management**: Environment-based configuration
  - Centralized environment variable management
  - Database connection parameterization
  - Service interval configuration

## [v0.0.1-scaffolding] - 2025-08-22 - Scaffolding

### Added
- **Initial Project Structure**: Basic project scaffolding
  - Python project setup with Poetry
  - Basic directory structure
  - Initial documentation

- **Core Dependencies**: Essential Python packages
  - SQLAlchemy for database operations
  - Pydantic for data validation
  - Basic testing framework

- **Documentation**: Initial project documentation
  - README with project overview
  - Basic architecture documentation
  - Development setup instructions

### Changed
- **Project Naming**: Renamed from cryptobot to alphaloop
- **Repository Structure**: Initial organization of source code

---

## Version Naming Convention

### v0.0.1 - Scaffolding
- Basic project structure and dependencies
- Initial documentation and setup

### v0.0.2 - Infrastructure Foundation
- Complete infrastructure package ecosystem
- YAML-driven database schema management
- Service architecture implementation

### Future Versions
- **v0.0.3 - Data Collection**: Real exchange API integration
- **v0.0.4 - Analytics**: Data analysis and visualization
- **v0.0.5 - Cloud Integration**: Central infrastructure deployment
- **v0.1.0 - Production Ready**: Full production deployment capabilities
