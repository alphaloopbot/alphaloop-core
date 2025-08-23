# System Architecture Diagrams

## Overview

This document contains Mermaid diagrams that visualize the AlphaLoop system architecture, data flows, and component relationships.

## System Overview

```mermaid
graph TB
    subgraph "Data Sources"
        EX[Exchanges<br/>Binance, Coinbase, Kraken]
    end

    subgraph "Central Infrastructure"
        subgraph "Central Services"
            CDB[(Central Database<br/>Market Prices)]
        end

        subgraph "Central Applications"
            CMD[Central Market Data<br/>Service]
            CAPI[Central API<br/>Missing Data Service]
        end
    end

    subgraph "Local Nodes"
        subgraph "Local Instance 1"
            L1_MD[Local 1 Market Data<br/>Service]
            L1_DB[(Local 1 Database<br/>Market Prices, Aggregates)]
        end

        subgraph "Local Instance 2"
            L2_MD[Local 2 Market Data<br/>Service]
            L2_DB[(Local 2 Database<br/>Market Prices, Aggregates)]
        end
    end

    subgraph "Core Library"
        AL[AlphaLoop Core<br/>Library]
        AH[AlphaLoop<br/>Heartbeat]
        AD[AlphaLoop<br/>Database]
        ALG[AlphaLoop<br/>Logging]
    end

    %% Data flows from exchanges
    EX --> CMD
    EX --> L1_MD
    EX --> L2_MD

    %% Central internal connections
    CMD --> CDB
    CAPI --> CDB

    %% Local internal connections
    L1_MD --> L1_DB
    L2_MD --> L2_DB

    %% Central API provides missing data to local instances
    CAPI -.->|Missing Time Series| L1_MD
    CAPI -.->|Missing Time Series| L2_MD

    %% Library usage
    AL --> CMD
    AL --> L1_MD
    AL --> L2_MD
    AD --> CDB
    AD --> L1_DB
    AD --> L2_DB
    ALG --> CMD
    ALG --> L1_MD
    ALG --> L2_MD

    %% Styling
    classDef external fill:#ff9999
    classDef central fill:#99ccff
    classDef local fill:#ffcc99
    classDef library fill:#cc99ff

    class EX external
    class CDB,CMD,CAPI central
    class L1_MD,L1_DB,L2_MD,L2_DB local
    class AL,AH,AD,ALG library
```

## Data Flow Architecture

```mermaid
flowchart TD
    subgraph "Data Sources"
        EXCH[Exchanges]
        NEWS[News APIs]
        SENT[Sentiment APIs]
    end

    subgraph "Data Ingestion"
        INGEST[Data Ingestion<br/>Service]
        VALIDATE[Data Validation<br/>Gates]
        TRANSFORM[Data Transformation<br/>Service]
    end

    subgraph "Storage Layer"
        HOT[(Hot Storage<br/>Redis)]
        WARM[(Warm Storage<br/>PostgreSQL)]
        COLD[(Cold Storage<br/>Archive)]
    end

    subgraph "Processing Layer"
        RT[Real-time<br/>Processing]
        BATCH[Batch<br/>Processing]
        ANALYTICS[Analytics<br/>Engine]
    end

    subgraph "Consumption Layer"
        TRADING[Trading<br/>Engine]
        REPORTING[Reporting<br/>Service]
        API[API<br/>Service]
    end

    %% Data flow
    EXCH --> INGEST
    NEWS --> INGEST
    SENT --> INGEST

    INGEST --> VALIDATE
    VALIDATE --> TRANSFORM
    TRANSFORM --> HOT

    HOT --> RT
    HOT --> WARM
    WARM --> BATCH
    WARM --> COLD

    RT --> TRADING
    BATCH --> ANALYTICS
    ANALYTICS --> REPORTING
    HOT --> API
    WARM --> API

    %% Styling
    classDef source fill:#ff9999
    classDef ingestion fill:#ffcc99
    classDef storage fill:#99ccff
    classDef processing fill:#99ff99
    classDef consumption fill:#cc99ff

    class EXCH,NEWS,SENT source
    class INGEST,VALIDATE,TRANSFORM ingestion
    class HOT,WARM,COLD storage
    class RT,BATCH,ANALYTICS processing
    class TRADING,REPORTING,API consumption
```

## Service Communication

```mermaid
sequenceDiagram
    participant EX as Exchanges
    participant LX as Local Instance X
    participant CI as Central Infrastructure

    Note over EX,CI: Normal Operation - All Instances Collect Data
    EX->>LX: Market data
    EX->>CI: Market data

    Note over LX,CI: Local Instance X Fails - Central Infrastructure Provides Backup
    LX->>CI: Request missing time series data
    CI->>LX: Provide missing data
```

## Other Architecture Diagrams

The following diagrams are conceptual and may not reflect the current implementation:

### Data Flow Architecture
Shows a generic data processing pipeline from ingestion to consumption. This is a conceptual view of how data could flow through the system.

### Library Architecture
Shows how the AlphaLoop Core library and packages could be organized. The AlphaLoop Core library provides the foundation for all services.

**AlphaLoop Core Library**: This is the main library that contains the core business logic, domain entities, use cases, and infrastructure code. It's the foundation that all services (cloud and edge devices) use to implement their functionality.

### Data Lifecycle
Shows how data moves through different storage tiers over time. This is a conceptual view of data retention and archival policies.

### Security Architecture
Shows a generic security model with authentication, authorization, encryption, and audit layers. This is a conceptual security framework.

## Library Architecture

```mermaid
graph TB
    subgraph "AlphaLoop Core"
        DOMAIN[Domain Layer<br/>Entities, Value Objects]
        APP[Application Layer<br/>Use Cases]
        INFRA[Infrastructure Layer<br/>External Concerns]
        SHARED[Shared Layer<br/>Utilities]
    end

    subgraph "Packages"
        AH[alphaloop-heartbeat<br/>Health Monitoring]
        AL[alphaloop-logging<br/>Logging & Reporting]
        AS[alphaloop-storage<br/>Data Storage]
        AC[alphaloop-cache<br/>Caching & Pub/Sub]
    end

    subgraph "Services"
        DB_SVC[Database Service]
        METRICS_SVC[System Metrics Service]
        MARKET_SVC[Market Data Service]
    end

    %% Dependencies
    DOMAIN --> SHARED
    APP --> DOMAIN
    APP --> SHARED
    INFRA --> DOMAIN
    INFRA --> SHARED

    AH --> SHARED
    AL --> SHARED
    AS --> SHARED
    AC --> SHARED

    DB_SVC --> AS
    METRICS_SVC --> AH
    METRICS_SVC --> AL
    MARKET_SVC --> AS
    MARKET_SVC --> AL

    %% Styling
    classDef core fill:#cc99ff
    classDef package fill:#99ccff
    classDef service fill:#99ff99

    class DOMAIN,APP,INFRA,SHARED core
    class AH,AL,AS,AC package
    class DB_SVC,METRICS_SVC,MARKET_SVC service
```

## Data Lifecycle

```mermaid
flowchart LR
    subgraph "Data Lifecycle"
        INGEST[Ingestion]
        PROCESS[Processing]
        STORE[Storage]
        ARCHIVE[Archive]
        DELETE[Delete]
    end

    subgraph "Time Windows"
        T1[0-24h<br/>Hot Storage]
        T2[1d-1y<br/>Warm Storage]
        T3[1y+<br/>Cold Storage]
        T4[7y+<br/>Archive]
        T5[10y+<br/>Delete]
    end

    INGEST --> PROCESS
    PROCESS --> STORE
    STORE --> ARCHIVE
    ARCHIVE --> DELETE

    T1 --> STORE
    T2 --> STORE
    T3 --> ARCHIVE
    T4 --> ARCHIVE
    T5 --> DELETE

    %% Styling
    classDef lifecycle fill:#ffcc99
    classDef time fill:#99ccff

    class INGEST,PROCESS,STORE,ARCHIVE,DELETE lifecycle
    class T1,T2,T3,T4,T5 time
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        AUTH[Authentication<br/>JWT, API Keys]
        AUTHZ[Authorization<br/>RBAC]
        ENCRYPT[Encryption<br/>TLS, AES]
        AUDIT[Audit Trail<br/>Logging]
    end

    subgraph "Components"
        API[API Gateway]
        DB[(Database)]
        CACHE[Cache]
        MQ[Message Queue]
    end

    subgraph "External"
        USER[User]
        SERVICE[External Service]
    end

    USER --> AUTH
    SERVICE --> AUTH
    AUTH --> AUTHZ
    AUTHZ --> API

    API --> ENCRYPT
    API --> AUDIT

    ENCRYPT --> DB
    ENCRYPT --> CACHE
    ENCRYPT --> MQ

    AUDIT --> DB
    AUDIT --> CACHE
    AUDIT --> MQ

    %% Styling
    classDef security fill:#ff9999
    classDef component fill:#99ccff
    classDef external fill:#99ff99

    class AUTH,AUTHZ,ENCRYPT,AUDIT security
    class API,DB,CACHE,MQ component
    class USER,SERVICE external
```
