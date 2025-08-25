# AlphaLoop Database Service

PostgreSQL database service for AlphaLoop Core with separate databases for system monitoring and market data.

## Features

- **PostgreSQL 16.4**: Latest stable PostgreSQL version
- **Separate Databases**:
  - `alphaloop_sys`: System monitoring and metrics
  - `alphaloop_market`: Market data and trading information
- **Health Checks**: Built-in health monitoring
- **Persistent Storage**: Data persistence across container restarts
- **User Management**: Separate users for system, market, and testing

## Quick Start

1. **Copy environment template**:
   ```bash
   cp env.example .env
   ```

2. **Customize environment variables** in `.env`

3. **Start the service**:
   ```bash
   docker-compose up -d
   ```

4. **Check status**:
   ```bash
   docker-compose ps
   ```

## Environment Variables

| Variable             | Description                         | Default             |
|----------------------|-------------------------------------|---------------------|
| `POSTGRES_USER`      | PostgreSQL superuser                | `postgres`          |
| `POSTGRES_PASSWORD`  | PostgreSQL superuser password       | -                   |
| `DB_SYS_USER`        | System database user                | `alphaloop_sys`     |
| `DB_SYS_PASSWORD`    | System database password            | -                   |
| `DB_MARKET_USER`     | Market database user                | `alphaloop_market`  |
| `DB_MARKET_PASSWORD` | Market database password            | -                   |
| `DB_MARKET_NAME`     | Market database name                | `alphaloop_market`  |
| `DB_SYS_NAME`        | System database name                | `alphaloop_sys`     |
| `DB_TEST_USER`       | Test user                           | `alphaloop_test`    |
| `DB_TEST_PASSWORD`   | Test user password                  | -                   |
| `ALPHALOOP_HOME`     | Base directory for data             | `/opt/alphaloop`    |

## Database Structure

### System Database (`alphaloop_sys`)
- System metrics and monitoring data
- Hardware information
- Performance metrics
- Health status

### Market Database (`alphaloop_market`)
- Market data and prices
- Trading information
- Historical data
- Aggregated metrics

## Connection Examples

```bash
# Connect as superuser
psql -h localhost -p 5432 -U postgres -d postgres

# Connect to system database
psql -h localhost -p 5432 -U alphaloop_sys -d alphaloop_sys

# Connect to market database
psql -h localhost -p 5432 -U alphaloop_market -d alphaloop_market

```

## Health Check

The service includes health checks:
```bash
docker-compose exec alphaloop-database pg_isready -U postgres
```

## Data Persistence

Data is stored in `${ALPHALOOP_HOME}/postgres_db/` on the host system.
