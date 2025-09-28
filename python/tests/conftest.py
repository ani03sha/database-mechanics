"""Pytest configuration and shared fixtures for B-Tree tests."""

import pytest
import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (may take several seconds)"
    )


@pytest.fixture
def small_btree():
    """Fixture providing a small B-Tree for testing."""
    from database_mechanics.indexing.btree.btree_index import BTreeIndex

    btree = BTreeIndex[int, str](min_degree=3)
    test_data = [(10, "ten"), (20, "twenty"), (30, "thirty"), (40, "forty")]

    for key, value in test_data:
        btree.insert(key, value)

    return btree


@pytest.fixture
def medium_btree():
    """Fixture providing a medium-sized B-Tree for testing."""
    from database_mechanics.indexing.btree.btree_index import BTreeIndex

    btree = BTreeIndex[int, str](min_degree=5)

    # Insert sequential data
    for i in range(1, 21):  # 1 to 20
        btree.insert(i * 5, f"value_{i * 5}")

    return btree


@pytest.fixture
def string_btree():
    """Fixture providing a B-Tree with string keys."""
    from database_mechanics.indexing.btree.btree_index import BTreeIndex

    btree = BTreeIndex[str, int](min_degree=4)

    words = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape"]
    for i, word in enumerate(words):
        btree.insert(word, i + 1)

    return btree


@pytest.fixture
def empty_btree():
    """Fixture providing an empty B-Tree for testing."""
    from database_mechanics.indexing.btree.btree_index import BTreeIndex
    return BTreeIndex[int, str](min_degree=3)