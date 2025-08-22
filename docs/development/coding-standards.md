# Coding Standards & Axioms

## 🎯 **Core Axioms - If Violated, Code is Wrong**

### **Architecture Axioms**

#### A1: **Dependency Direction**
```
✅ CORRECT: Domain ← Application ← Infrastructure
❌ WRONG: Infrastructure → Domain
```

#### A2: **Domain Purity**
```
✅ CORRECT: Domain has no external dependencies
❌ WRONG: Domain imports SQLAlchemy, FastAPI, etc.
```

#### A3: **Repository Pattern**
```
✅ CORRECT: All data access through repository interfaces
❌ WRONG: Direct database queries in use cases
```

### **Code Quality Axioms**

#### A4: **Single Responsibility**
```
✅ CORRECT: One class = one reason to change
❌ WRONG: Class that validates, saves, and logs
```

#### A5: **Immutability**
```
✅ CORRECT: Value objects are immutable
❌ WRONG: Money object with setters
```

#### A6: **Dependency Injection**
```
✅ CORRECT: Dependencies injected via constructor
❌ WRONG: Class creates its own dependencies
```

### **Error Handling Axioms**

#### A7: **Exception Hierarchy**
```
✅ CORRECT: DomainException → ValidationError
❌ WRONG: Generic Exception or bare raise
```

#### A8: **Meaningful Errors**
```
✅ CORRECT: "Invalid price: -10.50 (must be positive)"
❌ WRONG: "Something went wrong"
```

### **Testing Axioms**

#### A9: **Test Independence**
```
✅ CORRECT: Each test is isolated
❌ WRONG: Tests depend on shared state
```

#### A10: **Domain Coverage**
```
✅ CORRECT: 100% test coverage for domain logic
❌ WRONG: Untested value object validation
```

## 🔍 **Quick Reference**

### **Import Rules**
```python
# ✅ Domain layer - no external imports
from ..shared.types.enums import Currency
from ..value_objects.money import Money

# ❌ Domain layer - external imports
from sqlalchemy import Column  # WRONG
from fastapi import APIRouter  # WRONG
```

### **Class Structure**
```python
# ✅ Proper entity
class Ticker(Entity):
    def __init__(self, symbol: str, ...):
        self._symbol = symbol  # Private, immutable

    @property
    def symbol(self) -> str:
        return self._symbol  # Read-only access

# ❌ Wrong entity
class Ticker:
    def __init__(self, symbol: str):
        self.symbol = symbol  # Public, mutable

    def set_symbol(self, symbol: str):  # WRONG - entities shouldn't have setters
        self.symbol = symbol
```

### **Use Case Pattern**
```python
# ✅ Proper use case
class ScrapeMarketDataUseCase:
    def __init__(
        self,
        ticker_repository: TickerRepository,  # Interface dependency
        market_data_service: MarketDataService,
    ):
        self._ticker_repository = ticker_repository
        self._market_data_service = market_data_service

    async def execute(self, symbol: str) -> dict:
        # Orchestrates domain objects
        ticker = await self._ticker_repository.find_by_symbol(symbol)
        if not ticker:
            raise TickerNotFoundError(f"Ticker {symbol} not found")

        return await self._market_data_service.scrape_data(ticker)

# ❌ Wrong use case
class ScrapeMarketDataUseCase:
    def __init__(self):
        self._db = Database()  # WRONG - creates dependency

    async def execute(self, symbol: str) -> dict:
        # WRONG - contains business logic
        if symbol.lower() == 'btc':
            return {"price": 50000}
        return {"price": 0}
```

### **Repository Pattern**
```python
# ✅ Proper repository interface
class TickerRepository(Repository[Ticker]):
    @abstractmethod
    async def find_by_symbol(self, symbol: str) -> Ticker | None:
        pass

# ✅ Proper repository implementation
class SQLTickerRepository(TickerRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_symbol(self, symbol: str) -> Ticker | None:
        # Implementation details here
        pass

# ❌ Wrong - bypassing repository
class UseCase:
    async def execute(self, symbol: str):
        # WRONG - direct database access
        result = await db.execute("SELECT * FROM tickers WHERE symbol = ?", [symbol])
```

### **Value Objects**
```python
# ✅ Proper value object
class Money:
    def __init__(self, amount: Decimal, currency: Currency):
        if amount < 0:
            raise InvalidMoneyValueError("Amount cannot be negative")
        self._amount = amount
        self._currency = currency

    @property
    def amount(self) -> Decimal:
        return self._amount

    def __add__(self, other: "Money") -> "Money":
        if self._currency != other._currency:
            raise CurrencyMismatchError("Cannot add different currencies")
        return Money(self._amount + other._amount, self._currency)

# ❌ Wrong value object
class Money:
    def __init__(self, amount: float, currency: str):
        self.amount = amount  # WRONG - public mutable
        self.currency = currency

    def set_amount(self, amount: float):  # WRONG - setters
        self.amount = amount
```

## 🚨 **Violation Examples**

### **Common Mistakes to Avoid**

1. **Domain importing infrastructure**
   ```python
   # WRONG - in domain/entities/ticker.py
   from sqlalchemy import Column
   ```

2. **Use case with business logic**
   ```python
   # WRONG - business logic in use case
   def calculate_risk(self, portfolio):
       return portfolio.value * 0.1  # Should be in domain service
   ```

3. **Entity with setters**
   ```python
   # WRONG - mutable entity
   class Ticker:
       def set_symbol(self, symbol: str):
           self.symbol = symbol
   ```

4. **Direct dependency creation**
   ```python
   # WRONG - creating dependencies
   class UseCase:
       def __init__(self):
           self.repository = SQLRepository()  # Should be injected
   ```

5. **Generic exceptions**
   ```python
   # WRONG - generic exception
   raise Exception("Error occurred")

   # ✅ CORRECT - specific exception
   raise InvalidSymbolError("Symbol cannot be empty")
   ```

## 📋 **Code Review Checklist**

Before merging any PR, verify:

- [ ] No dependency violations (A1, A2)
- [ ] Repository pattern used (A3)
- [ ] Single responsibility maintained (A4)
- [ ] Value objects are immutable (A5)
- [ ] Dependencies properly injected (A6)
- [ ] Exception hierarchy followed (A7, A8)
- [ ] Tests are independent (A9)
- [ ] Domain logic is tested (A10)

## 🛠️ **Automated Enforcement**

We use these tools to enforce axioms:

- **Ruff**: Import analysis, code quality
- **MyPy**: Type checking, dependency analysis
- **Pre-commit**: Automated checks before commits
- **Pytest**: Test coverage enforcement

## 📚 **Further Reading**

- [ADR-0001: Core Architectural Principles](./../architecture/decisions/0001-architecture-principles.md)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design by Eric Evans](https://domainlanguage.com/ddd/)
