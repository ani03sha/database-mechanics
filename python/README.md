# Database Mechanics - Python Implementation

This directory contains Python implementations of core database concepts and internals.

## Features

- **Storage Engine**: Page-based storage with buffer management
- **Indexing**: B+ tree implementation with range queries
- **Query Processing**: Simple query parser and executor
- **Transaction Management**: ACID properties implementation
- **Concurrency Control**: Lock-based and optimistic protocols

## Quick Start

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Run all quality checks
pre-commit run --all-files
```

## Project Structure

```
src/
├── database_mechanics/
│   ├── storage/          # Storage engine components
│   ├── indexing/         # B+ trees and other indexes
│   ├── query/            # Query processing
│   ├── transaction/      # Transaction management
│   └── concurrency/      # Concurrency control
tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
└── performance/          # Performance benchmarks
docs/                     # Documentation
```

## Development

This project follows modern Python development practices:

- **Type hints**: Full type annotation coverage
- **Code formatting**: Black + isort
- **Linting**: Flake8 with strict settings
- **Testing**: pytest with coverage reporting
- **Documentation**: Sphinx with autodoc