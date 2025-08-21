# ADR-0001: Core Architectural Principles and Axioms

## Status
Accepted

## Context
We need to establish clear, immutable principles that guide all architectural decisions and code implementation. These principles serve as axioms - if code violates them, it's wrong by definition.

## Decision
We will follow these core architectural axioms:

### 🏗️ **Clean Architecture Axioms**

#### A1: **Dependency Rule**
- **Axiom**: Dependencies must point inward. Domain → Application → Infrastructure
- **Violation**: If any outer layer imports from an inner layer, the code is wrong
- **Example**: Infrastructure importing domain entities directly = ❌

#### A2: **Domain Independence**
- **Axiom**: Domain layer must be completely independent of external concerns
- **Violation**: If domain code imports frameworks, databases, or external APIs, it's wrong
- **Example**: Domain entity importing SQLAlchemy = ❌

#### A3: **Use Case Orchestration**
- **Axiom**: Application layer orchestrates domain objects, never contains business logic
- **Violation**: If use cases contain business rules instead of coordinating them, they're wrong
- **Example**: Use case calculating risk instead of calling domain service = ❌

### 🔒 **Immutability Axioms**

#### A4: **Value Object Immutability**
- **Axiom**: All value objects must be immutable and side-effect free
- **Violation**: If a value object can be modified after creation, it's wrong
- **Example**: Money object with setters = ❌

#### A5: **Entity Identity**
- **Axiom**: Entities are identified by their ID, not their attributes
- **Violation**: If entity equality depends on mutable attributes, it's wrong
- **Example**: Two entities with same ID but different equality = ❌

### 🎯 **Single Responsibility Axioms**

#### A6: **Class Purpose**
- **Axiom**: Each class must have exactly one reason to change
- **Violation**: If a class handles multiple concerns, it's wrong
- **Example**: Repository that also handles business logic = ❌

#### A7: **Method Purpose**
- **Axiom**: Each method must do exactly one thing
- **Violation**: If a method has multiple responsibilities, it's wrong
- **Example**: Method that validates AND saves AND logs = ❌

### 🔄 **Dependency Injection Axioms**

#### A8: **Interface Dependencies**
- **Axiom**: High-level modules must depend on abstractions, not concretions
- **Violation**: If a class directly instantiates its dependencies, it's wrong
- **Example**: Use case creating repository instance = ❌

#### A9: **Inversion of Control**
- **Axiom**: Dependencies must be injected, not created internally
- **Violation**: If a class creates its own dependencies, it's wrong
- **Example**: Service instantiating database connection = ❌

### 🛡️ **Error Handling Axioms**

#### A10: **Domain Exception Hierarchy**
- **Axiom**: All exceptions must inherit from appropriate base classes
- **Violation**: If exceptions don't follow the hierarchy, they're wrong
- **Example**: Domain exception inheriting from generic Exception = ❌

#### A11: **Exception Context**
- **Axiom**: Exceptions must provide meaningful context and be actionable
- **Violation**: If exceptions don't help with debugging or recovery, they're wrong
- **Example**: Generic "Something went wrong" exception = ❌

### 📊 **Data Flow Axioms**

#### A12: **Repository Pattern**
- **Axiom**: Data access must go through repository interfaces
- **Violation**: If code bypasses repositories for data access, it's wrong
- **Example**: Use case directly querying database = ❌

#### A13: **Event-Driven Communication**
- **Axiom**: Cross-boundary communication must use domain events
- **Violation**: If modules directly call each other across boundaries, it's wrong
- **Example**: Infrastructure directly calling application methods = ❌

### 🧪 **Testing Axioms**

#### A14: **Test Independence**
- **Axiom**: Tests must be independent and not affect each other
- **Violation**: If tests depend on shared state or order, they're wrong
- **Example**: Tests that modify global state = ❌

#### A15: **Test Coverage**
- **Axiom**: Domain logic must have 100% test coverage
- **Violation**: If domain code lacks tests, it's wrong
- **Example**: Untested value object validation = ❌

## Consequences

### Positive
- **Consistency**: All code follows the same principles
- **Maintainability**: Clear guidelines prevent architectural drift
- **Onboarding**: New developers understand the rules immediately
- **Code Reviews**: Clear criteria for accepting/rejecting changes

### Negative
- **Learning Curve**: Developers must understand all axioms
- **Rigidity**: May slow down rapid prototyping
- **Overhead**: Need to check axioms during development

## Implementation

### Code Review Checklist
Every PR must be checked against these axioms:

- [ ] No dependency violations (A1, A2)
- [ ] Proper use case orchestration (A3)
- [ ] Value objects are immutable (A4)
- [ ] Entities have proper identity (A5)
- [ ] Single responsibility maintained (A6, A7)
- [ ] Dependencies properly injected (A8, A9)
- [ ] Exception hierarchy followed (A10, A11)
- [ ] Repository pattern used (A12)
- [ ] Events used for cross-boundary communication (A13)
- [ ] Tests are independent (A14)
- [ ] Domain logic is tested (A15)

### Automated Checks
We will implement automated checks for:
- Import analysis (A1, A2)
- Immutability verification (A4)
- Dependency injection validation (A8, A9)
- Test coverage enforcement (A15)

### Documentation
- Each axiom must be documented with examples
- Violation examples must be provided
- Corrective actions must be clear
