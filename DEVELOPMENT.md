# Development Guide

## Project Structure

This is a multi-language educational project implementing database internals in Python and Java.

### Git Ignore Strategy

Our `.gitignore` setup follows a hierarchical approach for maintainability:

```
.gitignore              # Global patterns (IDE, OS, database files)
├── python/.gitignore   # Python-specific patterns
└── java/.gitignore     # Java-specific patterns
```

**Global patterns (.gitignore):**
- IDE files (VSCode, IntelliJ, Vim)
- OS files (.DS_Store, Thumbs.db)
- Environment files (.env)
- Database artifacts (*.db, *.sqlite)
- Documentation builds

**Language-specific patterns:**
- `python/.gitignore`: Python bytecode, virtual environments, type checker cache
- `java/.gitignore`: Java class files, Maven artifacts, JAR files

This approach prevents duplication while keeping language-specific rules organized.

### Development Commands

Use the provided `Makefile` for consistent development workflows:

```bash
# Setup
make setup-python    # Install Python dependencies + pre-commit
make setup-java      # Resolve Java dependencies

# Development
make test            # Run tests for both languages
make format          # Format code in both languages
make lint            # Run linting for both languages
make check-all       # Comprehensive quality checks
make clean           # Clean build artifacts
```

### Language-Specific Development

**Python:**
```bash
cd python
pip install -e ".[dev]"        # Install in development mode
pre-commit install             # Install git hooks
pytest                         # Run tests
black src/ tests/              # Format code
mypy src/                      # Type checking
```

**Java:**
```bash
cd java
mvn clean test                 # Clean build and test
mvn spotless:apply            # Format code
mvn spotbugs:check            # Static analysis
mvn clean verify -Pcoverage   # Full quality checks
```

## Adding New Ignore Patterns

When adding new ignore patterns:

1. **Global patterns** → Add to root `.gitignore`
   - Cross-language tools (Docker, IDE configs)
   - Project artifacts (databases, logs)
   - OS-specific files

2. **Language-specific patterns** → Add to `{language}/.gitignore`
   - Build artifacts specific to that language
   - Language-specific tool cache directories
   - Package manager files

This keeps the ignore rules organized and maintainable as the project grows.