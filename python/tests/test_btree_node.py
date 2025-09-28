"""Test suite for BTreeNode implementation."""

import pytest
from database_mechanics.indexing.btree.btree_node import BTreeNode
from database_mechanics.indexing.btree.key_value_pair import KeyValuePair


class TestBTreeNodeBasics:
    """Test basic BTreeNode functionality."""

    def test_node_initialization(self):
        """Test node initialization with various parameters."""
        # Leaf node
        leaf = BTreeNode[int, str](min_degree=3, is_leaf=True)
        assert leaf.min_degree == 3
        assert leaf.is_leaf
        assert len(leaf) == 0
        assert not leaf.is_full()

        # Internal node
        internal = BTreeNode[int, str](min_degree=5, is_leaf=False)
        assert internal.min_degree == 5
        assert not internal.is_leaf
        assert len(internal) == 0

    def test_invalid_min_degree(self):
        """Test initialization with invalid min_degree."""
        with pytest.raises(ValueError, match="Minimum degress must be at least 2"):
            BTreeNode[int, str](min_degree=1)

    def test_immutable_min_degree(self):
        """Test that min_degree is immutable after creation."""
        node = BTreeNode[int, str](min_degree=3)

        with pytest.raises(AttributeError, match="min_degree is immutable"):
            node._min_degree = 5

    def test_mutable_is_leaf(self):
        """Test that is_leaf can be changed (for node type conversion)."""
        node = BTreeNode[int, str](min_degree=3, is_leaf=True)
        assert node.is_leaf

        # Should be able to change from leaf to internal
        node.is_leaf = False
        assert not node.is_leaf

        # And back to leaf
        node.is_leaf = True
        assert node.is_leaf


class TestBTreeNodeOperations:
    """Test BTreeNode key-value operations."""

    def test_insert_key_value(self):
        """Test insertion of key-value pairs maintaining sorted order."""
        node = BTreeNode[int, str](min_degree=3)

        # Insert in random order
        pairs = [(30, "thirty"), (10, "ten"), (20, "twenty"), (40, "forty")]
        for key, value in pairs:
            node.insert_key_value(key, value)

        assert len(node) == 4

        # Keys should be sorted
        expected_keys = [10, 20, 30, 40]
        for i, expected_key in enumerate(expected_keys):
            assert node.get_key(i) == expected_key

    def test_find_key_index(self):
        """Test binary search for key indices."""
        node = BTreeNode[int, str](min_degree=4)

        # Insert sorted keys
        keys = [10, 30, 50, 70]
        for key in keys:
            node.insert_key_value(key, f"value_{key}")

        # Test exact matches
        assert node.find_key_index(10) == 0
        assert node.find_key_index(30) == 1
        assert node.find_key_index(50) == 2
        assert node.find_key_index(70) == 3

        # Test non-existent keys (should return negative insertion point)
        assert node.find_key_index(5) == -1    # Insert at position 0
        assert node.find_key_index(20) == -2   # Insert at position 1
        assert node.find_key_index(40) == -3   # Insert at position 2
        assert node.find_key_index(60) == -4   # Insert at position 3
        assert node.find_key_index(80) == -5   # Insert at position 4

    def test_get_child_index(self):
        """Test determination of child index for key navigation."""
        node = BTreeNode[int, str](min_degree=4)
        keys = [20, 40, 60]
        for key in keys:
            node.insert_key_value(key, f"value_{key}")

        # Test child index calculation
        assert node.get_child_index(10) == 0  # Less than first key
        assert node.get_child_index(20) == 1  # Equal to first key (go right)
        assert node.get_child_index(30) == 1  # Between first and second
        assert node.get_child_index(40) == 2  # Equal to second key
        assert node.get_child_index(50) == 2  # Between second and third
        assert node.get_child_index(60) == 3  # Equal to third key
        assert node.get_child_index(70) == 3  # Greater than last key

    def test_remove_key_value_pair(self):
        """Test removal of key-value pairs."""
        node = BTreeNode[int, str](min_degree=4)

        # Insert test data
        keys = [10, 20, 30, 40]
        for key in keys:
            node.insert_key_value(key, f"value_{key}")

        original_length = len(node)

        # Remove from middle
        removed = node.remove_key_value_pair(1)  # Remove key 20
        assert removed.key == 20
        assert removed.value == "value_20"
        assert len(node) == original_length - 1

        # Verify remaining keys are still sorted
        remaining_keys = [node.get_key(i) for i in range(len(node))]
        assert remaining_keys == [10, 30, 40]

    def test_is_full_and_underflow(self):
        """Test capacity checking methods."""
        node = BTreeNode[int, str](min_degree=3)  # Max 2*3-1 = 5 keys

        # Empty node
        assert not node.is_full()
        assert node.is_underflow()  # Below minimum (except for root)

        # Add keys up to capacity
        for i in range(5):  # 0, 1, 2, 3, 4
            node.insert_key_value(i * 10, f"value_{i}")
            if i < 4:
                assert not node.is_full()

        # Should be full with 5 keys
        assert node.is_full()
        assert not node.is_underflow()


class TestBTreeNodeChildren:
    """Test BTreeNode child node management."""

    def test_insert_and_remove_children(self):
        """Test insertion and removal of child nodes."""
        parent = BTreeNode[int, str](min_degree=3, is_leaf=False)
        child1 = BTreeNode[int, str](min_degree=3)
        child2 = BTreeNode[int, str](min_degree=3)
        child3 = BTreeNode[int, str](min_degree=3)

        # Insert children
        parent.insert_child(0, child1)
        parent.insert_child(1, child2)
        parent.insert_child(2, child3)

        assert len(parent.children) == 3
        assert parent.get_child(0) is child1
        assert parent.get_child(1) is child2
        assert parent.get_child(2) is child3

        # Remove child from middle
        removed = parent.remove_child(1)
        assert removed is child2
        assert len(parent.children) == 2
        assert parent.get_child(0) is child1
        assert parent.get_child(1) is child3

    def test_children_property(self):
        """Test children property access."""
        node = BTreeNode[int, str](min_degree=3, is_leaf=False)
        child1 = BTreeNode[int, str](min_degree=3)
        child2 = BTreeNode[int, str](min_degree=3)

        node.insert_child(0, child1)
        node.insert_child(1, child2)

        children = node.children
        assert len(children) == 2
        assert children[0] is child1
        assert children[1] is child2


class TestBTreeNodeStringRepresentation:
    """Test string representation of BTreeNode."""

    def test_empty_node_repr(self):
        """Test string representation of empty nodes."""
        leaf = BTreeNode[int, str](min_degree=3, is_leaf=True)
        internal = BTreeNode[int, str](min_degree=3, is_leaf=False)

        leaf_repr = str(leaf)
        internal_repr = str(internal)

        assert "[]" in leaf_repr
        assert "(leaf)" in leaf_repr
        assert "[]" in internal_repr
        assert "(leaf)" not in internal_repr

    def test_populated_node_repr(self):
        """Test string representation of nodes with data."""
        node = BTreeNode[int, str](min_degree=3)

        node.insert_key_value(10, "ten")
        node.insert_key_value(30, "thirty")
        node.insert_key_value(20, "twenty")

        repr_str = str(node)
        assert "[10, 20, 30]" in repr_str
        assert "(leaf)" in repr_str


class TestBTreeNodeEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_node_operations(self):
        """Test operations on empty nodes."""
        node = BTreeNode[int, str](min_degree=3)

        # find_key_index on empty node
        assert node.find_key_index(42) == -1

        # Length of empty node
        assert len(node) == 0

    def test_access_beyond_bounds(self):
        """Test accessing keys/values beyond node bounds."""
        node = BTreeNode[int, str](min_degree=3)
        node.insert_key_value(10, "ten")

        # These should raise IndexError for out-of-bounds access
        with pytest.raises(IndexError):
            node.get_key(1)

        with pytest.raises(IndexError):
            node.get_value(1)

        with pytest.raises(IndexError):
            node.get_key_value_pair(1)

    def test_remove_from_empty_children(self):
        """Test removing children when none exist."""
        node = BTreeNode[int, str](min_degree=3, is_leaf=False)

        with pytest.raises(IndexError):
            node.remove_child(0)

    def test_large_key_capacity(self):
        """Test node with larger capacity."""
        node = BTreeNode[int, str](min_degree=10)  # Can hold 2*10-1 = 19 keys

        # Fill to capacity
        for i in range(19):
            node.insert_key_value(i * 10, f"value_{i * 10}")

        assert len(node) == 19
        assert node.is_full()

        # Verify all keys are accessible
        for i in range(19):
            assert node.get_key(i) == i * 10
            assert node.get_value(i) == f"value_{i * 10}"


class TestBTreeNodeBisectOptimization:
    """Test that bisect optimization works correctly."""

    def test_bisect_insertion_order(self):
        """Test that bisect maintains correct order regardless of insertion sequence."""
        node = BTreeNode[int, str](min_degree=5)

        # Insert in various orders
        test_cases = [
            [1, 2, 3, 4, 5],           # Ascending
            [5, 4, 3, 2, 1],           # Descending
            [3, 1, 4, 2, 5],           # Random
            [1, 5, 2, 4, 3],           # Another random
        ]

        for keys in test_cases:
            # Clear node for each test
            node = BTreeNode[int, str](min_degree=5)

            for key in keys:
                node.insert_key_value(key, f"value_{key}")

            # Verify final order is always sorted
            final_keys = [node.get_key(i) for i in range(len(node))]
            assert final_keys == sorted(keys)

    def test_find_key_performance_correctness(self):
        """Test that find_key_index works correctly with bisect optimization."""
        node = BTreeNode[int, str](min_degree=20)  # Large node

        # Insert many keys
        keys = list(range(0, 100, 5))  # [0, 5, 10, 15, ..., 95]
        for key in keys:
            node.insert_key_value(key, f"value_{key}")

        # Test finding each key
        for i, key in enumerate(keys):
            found_index = node.find_key_index(key)
            assert found_index == i
            assert node.get_key(found_index) == key

        # Test finding non-existent keys
        non_existent = [1, 3, 7, 12, 98, 101]
        for key in non_existent:
            index = node.find_key_index(key)
            assert index < 0  # Should be negative (insertion point)


if __name__ == "__main__":
    pytest.main([__file__])