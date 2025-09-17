"""Basic test to verify the project setup works correctly."""

import pytest
from database_mechanics import __version__, VERSION_INFO


def test_version():
    """Test that version information is accessible."""
    assert __version__ == "0.1.0"
    assert VERSION_INFO == (0, 1, 0)


def test_imports():
    """Test that the package can be imported successfully."""
    import database_mechanics
    assert hasattr(database_mechanics, '__version__')
    assert hasattr(database_mechanics, '__author__')