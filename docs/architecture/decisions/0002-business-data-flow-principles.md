# ADR 0002: Business Data Flow Principles

## Status

Accepted

## Context

The AlphaLoop system handles multiple types of data flows across different environments (local, cloud, exchanges) and needs clear principles to ensure data integrity, consistency, and proper lifecycle management. This ADR establishes the foundational axioms for how data moves through the system.

## Decision

We establish the following business data flow principles as core axioms that all data operations must follow:

### B1: Data Source Hierarchy
**Data flows from authoritative sources to consumers, never the reverse.**

- **Exchange → Central Infrastructure**: Exchanges are the authoritative source for real-time market data
- **Exchange → Local Instances**: Exchanges are the authoritative source for real-time market data
- **Central Infrastructure → Local Instances**: Central infrastructure provides missing time series data when local instances have gaps
- **Market Data Only**: Local Instances and Central Infrastructure only read market data from exchanges (no write operations for market data)
- **Future Trading Operations**: Order placement and trading operations will be implemented separately with their own data flow patterns



### B2: Data Synchronization Patterns
**Data synchronization follows specific patterns based on deployment type.**

- **Local Instances**: Collect data directly from exchanges, request missing data from central infrastructure
- **Central Infrastructure**: Collects data directly from exchanges, provides missing time series data to local instances on request
- **Independent Collection**: Both local instances and central infrastructure collect data independently for redundancy

### B3: Data Lifecycle Management
**Data has defined retention and archival policies.**

- **Market data**: Point-in-time data and aggregated data (1min, 10min, 2h, 1day granularities) + metadata
- **System metrics**: Point-in-time data and aggregated data (1min, 10min, 2h, 1day granularities) + metadata
- **Data retention**: Specific retention policies to be defined based on business requirements

### B4: Data Validation Gates
**Data must pass validation at each stage of the flow.**

- **Ingestion**: Validate format, timestamps, and basic integrity
- **Processing**: Validate business rules and relationships
- **Storage**: Validate consistency with existing data
- **Retrieval**: Validate access permissions and data freshness

### B5: Error Handling and Recovery
**Data flow errors must be handled gracefully with recovery mechanisms.**

- **Temporary failures**: Retry with exponential backoff
- **Permanent failures**: Log error and continue with available data
- **Data corruption**: Reject and request fresh data from source
- **Network issues**: Use cached data within freshness window

### B6: Data Consistency Boundaries
**Data consistency is maintained within defined boundaries.**

- **Market data consistency**: Point-in-time data may vary between instances due to rapid price changes (10s collection intervals), but should be within reasonable bounds
- **System metrics isolation**: Each local instance maintains its own system metrics data, independent of other instances
- **Strong consistency**: Within single database (local or central)
- **Eventual consistency**: Between local instances and central infrastructure for market data recovery

### B7: Data Access Patterns
**Data access follows specific patterns based on use case.**

- **Market data access**: Point-in-time data and aggregated data with configurable granularities (1min, 10min, 2h, 1day)
- **System metrics access**: Point-in-time data and aggregated data with configurable granularities (1min, 10min, 2h, 1day)
- **Metadata access**: Consistent metadata across all data types
- **Analysis**: Aggregated data with configurable time windows
- **Reporting**: Pre-computed aggregates and summaries

### B8: Data Transformation Rules
**Data transformations must be reversible and auditable.**

- **Aggregation**: Must preserve original data for drill-down
- **Normalization**: Must maintain referential integrity
- **Enrichment**: Must not overwrite original data
- **Filtering**: Must be configurable and documented

### B9: Data Security and Privacy
**Data access and transmission must follow security principles.**

- **Encryption**: All data in transit and at rest
- **Authentication**: Required for all data access
- **Authorization**: Role-based access to data
- **Audit trails**: All data access and modifications logged

## Consequences

### Positive
- **Clear data flow patterns** make the system easier to understand and maintain
- **Consistent error handling** improves system reliability
- **Defined data lifecycles** optimize storage and performance
- **Security principles** protect sensitive data

### Negative
- **Increased complexity** in data flow implementation
- **Potential performance overhead** from validation and logging
- **Stricter requirements** may limit flexibility in edge cases

### Risks
- **Over-engineering** if principles are too rigid
- **Performance impact** if validation is too strict
- **Maintenance burden** if principles are not consistently applied

## Implementation

### Phase 1: Foundation
1. Implement data validation gates in all ingestion points
2. Set up data lifecycle management policies
3. Establish error handling patterns

### Phase 2: Integration
1. Implement data synchronization between local instances and central infrastructure
2. Set up audit trails and logging
3. Configure security and access controls

### Phase 3: Optimization
1. Optimize data flow performance
2. Implement caching strategies
3. Fine-tune retention policies

## Code Review Checklist

When reviewing data flow implementations, ensure:

- [ ] Data flows follow the established hierarchy (B1)
- [ ] Synchronization patterns are correctly implemented (B2)
- [ ] Lifecycle management is in place (B3)
- [ ] Validation gates are present (B4)
- [ ] Error handling follows patterns (B5)
- [ ] Consistency boundaries are respected (B6)
- [ ] Access patterns are appropriate (B7)
- [ ] Transformations are reversible (B8)
- [ ] Security principles are followed (B9)

## Related Documents

- [ADR 0001: Architecture Principles](0001-architecture-principles.md)
- [System Architecture Diagrams](../diagrams/system-overview.md)
- [Service Architecture](../overview.md)
