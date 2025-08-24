-- AlphaLoop Database Schemas - Generated from YAML
-- This file is auto-generated from config/database_schema.yaml
-- DO NOT EDIT MANUALLY - Run scripts/generate-database-schema.py to regenerate

-- Drop existing databases and recreate from scratch
\c postgres;

-- Drop existing databases if they exist
DROP DATABASE IF EXISTS alphaloop_sys CASCADE;
DROP DATABASE IF EXISTS alphaloop_market CASCADE;

-- Create fresh databases
CREATE DATABASE alphaloop_sys;
CREATE DATABASE alphaloop_market;

-- ============================================================================
-- ALPHALOOP_SYS DATABASE
-- ============================================================================
\c alphaloop_sys;

-- System hardware and configuration information
CREATE TABLE system_attributes (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    kernel_version VARCHAR(255),
    system_name VARCHAR(255),
    node_name VARCHAR(255),
    host_name VARCHAR(255),
    machine VARCHAR(255),
    boot_time TIMESTAMP,
    app_start_time TIMESTAMP,
    cpu_cores INTEGER,
    cpu_cores_logical INTEGER,
    ram_total DECIMAL(20,8),
    swap_total DECIMAL(20,8),
    ssd_total DECIMAL(20,8)
);


-- Real-time system metrics (30-second granularity)
CREATE TABLE system_metrics (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    metadata_id INTEGER REFERENCES system_attributes.id,
    timestamp_id INTEGER,
    cpu_temperature DECIMAL(20,8),
    cpu_speed INTEGER,
    cpu_usage DECIMAL(20,8),
    cores_usage JSONB,
    core_usage_max DECIMAL(20,8),
    core_usage_min DECIMAL(20,8),
    ram_usage DECIMAL(20,8),
    swap_usage DECIMAL(20,8),
    ssd_usage DECIMAL(20,8),
    ip_address VARCHAR(255),
    ip_renewed BOOLEAN
);

CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp_id);
CREATE INDEX idx_system_metrics_metadata_id ON system_metrics(metadata_id);
CREATE INDEX idx_system_metrics_metadata_timestamp ON system_metrics(metadata_id, timestamp_id);

-- Aggregated system metrics at multiple timeframes
CREATE TABLE system_metrics_summary (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    metadata_id INTEGER REFERENCES system_attributes.id,
    timestamp_id INTEGER,
    cpu_temperature DECIMAL(20,8),
    cpu_speed DECIMAL(20,8),
    cpu_usage DECIMAL(20,8),
    core_usage_max DECIMAL(20,8),
    core_usage_min DECIMAL(20,8),
    ram_usage DECIMAL(20,8),
    swap_usage DECIMAL(20,8),
    ssd_usage DECIMAL(20,8),
    ip_address VARCHAR(255)
);



-- ============================================================================
-- SAMPLE DATA FOR ALPHALOOP_SYS
-- ============================================================================

-- Insert sample system metadata
INSERT INTO system_attributes (
    host_name, system_name, node_name, machine, kernel_version,
    cpu_cores, cpu_cores_logical, ram_total, disk_total, boot_time
) VALUES (
    'alphaloop-node-001',
    'Linux',
    'alphaloop-node-001',
    'x86_64',
    '5.15.0-generic',
    8,
    16,
    34359738368.0,  -- 32GB
    1099511627776.0, -- 1TB
    CURRENT_TIMESTAMP - INTERVAL '1 hour'
);

-- ============================================================================
-- ALPHALOOP_MARKET DATABASE
-- ============================================================================
\c alphaloop_market;

-- Ticker definitions and exchange information
CREATE TABLE tickers_metadata (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    ticker VARCHAR(255),
    base VARCHAR(255),
    quote VARCHAR(255),
    exchange VARCHAR(255),
    active BOOLEAN
);


-- Real-time price data (10-second granularity)
CREATE TABLE tickers_prices (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    metadata_id INTEGER REFERENCES tickers_metadata.id,
    timestamp_id INTEGER,
    price DECIMAL(20,8),
    quote_volume24h DECIMAL(20,8)
);

CREATE INDEX idx_tickers_prices_timestamp ON tickers_prices(timestamp_id);
CREATE INDEX idx_tickers_prices_metadata_id ON tickers_prices(metadata_id);
CREATE INDEX idx_tickers_prices_metadata_timestamp ON tickers_prices(metadata_id, timestamp_id);

-- OHLC aggregated price data at multiple timeframes
CREATE TABLE tickers_prices_ohlca (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    metadata_id INTEGER REFERENCES tickers_metadata.id,
    timestamp_id INTEGER,
    open DECIMAL(20,8),
    high DECIMAL(20,8),
    low DECIMAL(20,8),
    close DECIMAL(20,8),
    average DECIMAL(20,8),
    quote_volume24h DECIMAL(20,8)
);



-- ============================================================================
-- SAMPLE DATA FOR ALPHALOOP_MARKET
-- ============================================================================

-- Insert sample market metadata
INSERT INTO tickers_metadata (ticker, base, quote, exchange, active) VALUES
('BTC/USDT', 'BTC', 'USDT', 'binance', true),
('ETH/USDT', 'ETH', 'USDT', 'binance', true),
('ADA/USDT', 'ADA', 'USDT', 'binance', true),
('DOT/USDT', 'DOT', 'USDT', 'binance', true);

-- Show created tables
\c alphaloop_sys;
\dt

\c alphaloop_market;
\dt
