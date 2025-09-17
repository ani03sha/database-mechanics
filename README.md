# Database Mechanics

A comprehensive educational project implementing database internals in both Python and Java. This repository contains hands-on implementations of core database concepts including storage engines, indexing, query processing, and transaction management.

## Project Structure

```
database-mechanics/
├── python/                   # Python implementation
│   ├── src/database_mechanics/
│   │   ├── storage/         # Storage engine components
│   │   ├── indexing/        # B+ trees and other indexes
│   │   ├── query/           # Query processing
│   │   ├── transaction/     # Transaction management
│   │   └── concurrency/     # Concurrency control
│   ├── tests/               # Python tests
│   └── docs/                # Python documentation
├── java/                     # Java implementation
│   └── src/main/java/com/databasemechanics/
│       ├── storage/         # Storage engine and buffer management
│       ├── index/           # Indexing structures
│       ├── query/           # Query processing
│       ├── transaction/     # Transaction management
│       └── concurrency/     # Concurrency control
└── docs/                     # Shared documentation
```

## Features

Both implementations provide:

- **Storage Engine**: Page-based storage with buffer management
- **Indexing**: B+ tree implementation with range queries
- **Query Processing**: SQL parsing and execution
- **Transaction Management**: ACID properties with logging
- **Concurrency Control**: Lock management and isolation levels

## Quick Start

### Python
```bash
cd python
pip install -e ".[dev]"
pytest
```

### Java
```bash
cd java
mvn clean test
```

## Learning Path

1. **Storage Layer**: Start with page management and buffer pools
2. **Indexing**: Implement B+ trees for efficient data access
3. **Query Processing**: Build a simple SQL parser and executor
4. **Transactions**: Add ACID compliance with write-ahead logging
5. **Concurrency**: Implement locking and isolation levels

## Development

Each language directory contains its own development setup:

- **Python**: Modern packaging with `pyproject.toml`, pre-commit hooks, type checking
- **Java**: Maven build system with quality gates, formatting, and static analysis

## Contributing

This is an educational project. Feel free to:

- Implement additional database features
- Add performance benchmarks
- Create visualization tools
- Improve documentation and examples

## License

MIT License - see LICENSE file for details.
