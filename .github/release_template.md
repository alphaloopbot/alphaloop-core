# AlphaLoop Core {{TAG_NAME}}

## 🎉 Release Overview

This release includes improvements, bug fixes, and new features for the AlphaLoop Core trading system.

## 🚀 What's New

### Features
- [Add new features here]

### Improvements
- [Add improvements here]

### Bug Fixes
- [Add bug fixes here]

## 📦 Installation

### Using Poetry (Recommended)
```bash
poetry add alphaloop-core
```

### Using Conda
```bash
conda env create -f environment.yml
conda activate alphaloop-core
```

## 🔧 Configuration

Copy the environment template and customize:
```bash
cp env.example .env
```

Key configuration options:
- `SERVICE_HOST` / `SERVICE_PORT`: API service location
- `DB_HOST` / `DB_PORT`: Database connection
- `API_KEY`: Authentication key
- `LOG_LEVEL`: Logging verbosity
- `ENVIRONMENT`: Deployment environment
- `DEFAULT_CURRENCY`: Default currency for market data and trading operations (default: USDT)

## 🧪 Testing

Run the test suite to ensure everything works:
```bash
make test
make lint
make type-check
```

## 📚 Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Coding Standards](docs/development/coding-standards.md)
- [Axioms Reference](docs/development/axioms-reference.md)

## 🔗 Links

- [GitHub Repository](https://github.com/alphaloop-core/alphaloop-core)
- [Documentation](https://github.com/alphaloop-core/alphaloop-core/tree/main/docs)
- [Issues](https://github.com/alphaloop-core/alphaloop-core/issues)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

---

**Version**: {{VERSION}}
**Release Date**: $(date +%Y-%m-%d)
**Python Version**: 3.12+
