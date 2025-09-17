# Database Mechanics - Java Implementation

This directory contains Java implementations of core database concepts and internals.

## Features

- **Storage Engine**: Page-based storage with buffer pool management
- **Indexing**: B+ tree implementation with concurrent access
- **Query Processing**: SQL parser and query execution engine
- **Transaction Management**: ACID compliance with WAL
- **Concurrency Control**: Lock manager and deadlock detection

## Quick Start

```bash
# Compile and run tests
mvn clean test

# Run with coverage
mvn clean test -Pcoverage

# Format code
mvn spotless:apply

# Static analysis
mvn spotbugs:check

# Run all quality checks
mvn clean verify -Pcoverage
```

## Project Structure

```
src/main/java/com/databasemechanics/
├── storage/              # Storage engine and buffer management
│   ├── page/            # Page management
│   ├── buffer/          # Buffer pool
│   └── file/            # File I/O operations
├── index/               # Indexing structures
│   ├── btree/          # B+ tree implementation
│   └── hash/           # Hash index
├── query/              # Query processing
│   ├── parser/         # SQL parsing
│   ├── planner/        # Query planning
│   └── executor/       # Query execution
├── transaction/        # Transaction management
│   ├── log/            # Write-ahead logging
│   └── recovery/       # Recovery mechanisms
└── concurrency/        # Concurrency control
    ├── lock/           # Lock management
    └── isolation/      # Isolation levels

src/test/java/           # Unit and integration tests
```

## Development

This project follows modern Java development practices:

- **Java 17**: Modern language features and performance
- **Maven**: Dependency management and build lifecycle
- **JUnit 5**: Modern testing framework with parameterized tests
- **AssertJ**: Fluent assertions for better test readability
- **Mockito**: Mocking framework for unit tests
- **JaCoCo**: Code coverage analysis
- **Spotless**: Code formatting with Google Java Style
- **SpotBugs**: Static analysis for bug detection

## Building

```bash
# Clean build
mvn clean compile

# Run tests
mvn test

# Integration tests
mvn integration-test

# Package
mvn package

# Install to local repository
mvn install
```