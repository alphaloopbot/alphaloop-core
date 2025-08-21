# 🎯 Axioms Reference Card

## **If Violated, Code is Wrong**

### **🏗️ Architecture**
- **A1**: Dependencies point inward only (Domain ← Application ← Infrastructure)
- **A2**: Domain has zero external dependencies
- **A3**: All data access through repository interfaces

### **🔒 Immutability**
- **A4**: Value objects are immutable (no setters)
- **A5**: Entities identified by ID, not attributes

### **🎯 Responsibility**
- **A6**: One class = one reason to change
- **A7**: One method = one thing to do

### **🔄 Dependencies**
- **A8**: Depend on abstractions, not concretions
- **A9**: Inject dependencies, don't create them

### **🛡️ Errors**
- **A10**: Use proper exception hierarchy
- **A11**: Exceptions must be meaningful and actionable

### **🧪 Testing**
- **A12**: Tests are independent
- **A13**: Domain logic has 100% test coverage

---

## **Quick Examples**

### ✅ **Correct**
```python
# Domain entity
class Ticker(Entity):
    def __init__(self, symbol: str):
        self._symbol = symbol  # Private, immutable

    @property
    def symbol(self) -> str:
        return self._symbol

# Use case with dependency injection
class UseCase:
    def __init__(self, repository: Repository):
        self._repository = repository  # Injected

# Value object
class Money:
    def __init__(self, amount: Decimal, currency: Currency):
        self._amount = amount  # Immutable
```

### ❌ **Wrong**
```python
# Domain importing infrastructure
from sqlalchemy import Column  # WRONG

# Creating dependencies
class UseCase:
    def __init__(self):
        self.repository = SQLRepository()  # WRONG

# Mutable value object
class Money:
    def set_amount(self, amount: float):  # WRONG
        self.amount = amount
```

---

## **Code Review Checklist**
- [ ] No dependency violations (A1, A2)
- [ ] Repository pattern used (A3)
- [ ] Single responsibility (A6, A7)
- [ ] Immutable value objects (A4)
- [ ] Proper dependency injection (A8, A9)
- [ ] Meaningful exceptions (A10, A11)
- [ ] Independent tests (A12)
- [ ] Domain coverage (A13)
