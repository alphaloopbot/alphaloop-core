# AlphaLoop Services

This directory contains all the Docker services for the AlphaLoop Core system, organized by functionality and deployment type.

## 🏗️ Service Architecture

```
services/
├── alphaloop-database/          # PostgreSQL database service
├── alphaloop-system-metrics/    # System monitoring service
├── alphaloop-market-data/       # Market data service (local/cloud variants)
└── docker-compose.yml          # Main orchestration file
```

## 🚀 Quick Start

### 1. Local Development Setup

```bash
# Start all services (local deployment)
docker-compose up -d

# Start specific services
docker-compose up -d alphaloop-database
docker-compose up -d alphaloop-system-metrics
docker-compose up -d alphaloop-market-data-local
```

### 2. Cloud Deployment

```bash
# Start cloud deployment (without local sync)
docker-compose up -d alphaloop-database
docker-compose up -d alphaloop-market-data-cloud
```

## 📋 Services Overview

### 🗄️ AlphaLoop Database (`alphaloop-database`)
- **Purpose**: PostgreSQL database with separate databases for system and market data
- **Databases**:
  - `alphaloop_sys`: System monitoring and metrics
  - `alphaloop_market`: Market data and trading information
- **Port**: 5432
- **Health Check**: Built-in PostgreSQL health monitoring

### 📊 System Metrics (`alphaloop-system-metrics`)
- **Purpose**: Collects and stores system performance metrics
- **Features**:
  - CPU, memory, disk usage monitoring
  - Hardware information collection
  - Performance metrics aggregation
- **Dependencies**: Requires `alphaloop-database`
- **Health Check**: Python process monitoring

### 📈 Market Data (`alphaloop-market-data`)
- **Purpose**: Collects and processes market data from exchanges
- **Deployment Types**:
  - **Local**: Includes cloud data synchronization for missing data
  - **Cloud**: Primary data collection without sync capabilities
- **Features**:
  - Real-time market data collection
  - Data aggregation and storage
  - Cloud synchronization (local only)
- **Ports**: 8000 (cloud), 8001 (local)
- **Dependencies**: Requires `alphaloop-database`

## 🔧 Configuration

### Environment Setup

Each service has its own environment configuration:

```bash
# Database service
cp alphaloop-database/env.example alphaloop-database/.env

# System metrics service
cp alphaloop-system-metrics/env.example alphaloop-system-metrics/.env

# Market data service (local)
cp alphaloop-market-data/env.example.local alphaloop-market-data/.env.local

# Market data service (cloud)
cp alphaloop-market-data/env.example.cloud alphaloop-market-data/.env.cloud
```

### Key Configuration Variables

| Service | Key Variables | Description |
|---------|---------------|-------------|
| Database | `POSTGRES_PASSWORD`, `DB_SYS_PASSWORD` | Database passwords |
| System Metrics | `DATABASE_URL`, `METRICS_INTERVAL` | Database connection and collection interval |
| Market Data (Local) | `CLOUD_API_URL`, `CLOUD_SYNC_ENABLED` | Cloud API for data retrieval |
| Market Data (Cloud) | `DATABASE_URL`, `MARKET_DATA_INTERVAL` | Database connection and collection interval |

## 🏃‍♂️ Deployment Scenarios

### Local Development
```bash
# Full local stack with cloud sync
docker-compose up -d alphaloop-database
docker-compose up -d alphaloop-system-metrics
docker-compose up -d alphaloop-market-data-local
```

### Cloud Production
```bash
# Cloud deployment without local sync
docker-compose up -d alphaloop-database
docker-compose up -d alphaloop-market-data-cloud
```

### System Monitoring Only
```bash
# Just system metrics collection
docker-compose up -d alphaloop-database
docker-compose up -d alphaloop-system-metrics
```

## 🔍 Monitoring & Health Checks

### Service Health
```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs alphaloop-database
docker-compose logs alphaloop-system-metrics
docker-compose logs alphaloop-market-data-local
```

### Database Health
```bash
# Test database connection
docker-compose exec alphaloop-database pg_isready -U postgres

# Connect to database
docker-compose exec alphaloop-database psql -U postgres -d postgres
```

### API Health
```bash
# Market data API health
curl http://localhost:8000/health  # Cloud
curl http://localhost:8001/health  # Local
```

## 📁 Data Persistence

All data is persisted in `${ALPHALOOP_HOME}/`:
- **Database**: `${ALPHALOOP_HOME}/postgres_db/`
- **Logs**: `${ALPHALOOP_HOME}/logs/`
- **Cache**: `${ALPHALOOP_HOME}/cache/` (local market data only)

## 🔒 Security

- All services run as non-root users
- Database passwords are configurable via environment variables
- Health checks ensure service availability
- Read-only mounts for system monitoring

## 🛠️ Development

### Building Services
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build alphaloop-market-data-local
```

### Service Development
```bash
# Run with live code changes
docker-compose up --build

# Debug mode
docker-compose run --rm alphaloop-market-data-local bash
```

## 📚 Documentation

- [Database Service](alphaloop-database/README.md)
- [System Metrics Service](alphaloop-system-metrics/README.md)
- [Market Data Service](alphaloop-market-data/README.md)
