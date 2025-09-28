"""Test suite for KeyValuePair implementation."""

import pytest
from database_mechanics.indexing.btree.key_value_pair import KeyValuePair


class TestKeyValuePairBasics:
    """Test basic KeyValuePair functionality."""

    def test_valid_initialization(self):
        """Test creation of KeyValuePair with valid parameters."""
        kvp = KeyValuePair("key1", "value1")
        assert kvp.key == "key1"
        assert kvp.value == "value1"

        # Test with different types
        kvp_int = KeyValuePair(42, "answer")
        assert kvp_int.key == 42
        assert kvp_int.value == "answer"

        # Test with None value (should be allowed)
        kvp_none = KeyValuePair("key", None)
        assert kvp_none.key == "key"
        assert kvp_none.value is None

    def test_invalid_initialization(self):
        """Test creation with invalid parameters."""
        # None key should raise ValueError
        with pytest.raises(ValueError, match="Key cannot be null"):
            KeyValuePair(None, "value")

    def test_key_immutability(self):
        """Test that key is immutable after creation."""
        kvp = KeyValuePair("original_key", "value")

        # Direct assignment to key should fail
        with pytest.raises(AttributeError):
            kvp.key = "new_key"

        # Direct assignment to _key should also fail
        with pytest.raises(AttributeError, match="Key is immutable"):
            kvp._key = "new_key"

        # Key should remain unchanged
        assert kvp.key == "original_key"

    def test_value_mutability(self):
        """Test that value can be changed after creation."""
        kvp = KeyValuePair("key", "original_value")

        # Value should be changeable
        kvp.value = "new_value"
        assert kvp.value == "new_value"
        assert kvp.key == "key"  # Key should remain unchanged

        # Change to different type
        kvp.value = 42
        assert kvp.value == 42

        # Change to None
        kvp.value = None
        assert kvp.value is None


class TestKeyValuePairEquality:
    """Test equality and hashing behavior."""

    def test_equality_same_values(self):
        """Test equality when key and value are the same."""
        kvp1 = KeyValuePair("key", "value")
        kvp2 = KeyValuePair("key", "value")

        assert kvp1 == kvp2
        assert kvp2 == kvp1

    def test_equality_different_values(self):
        """Test inequality when values differ."""
        kvp1 = KeyValuePair("key", "value1")
        kvp2 = KeyValuePair("key", "value2")

        assert kvp1 != kvp2
        assert kvp2 != kvp1

    def test_equality_different_keys(self):
        """Test inequality when keys differ."""
        kvp1 = KeyValuePair("key1", "value")
        kvp2 = KeyValuePair("key2", "value")

        assert kvp1 != kvp2
        assert kvp2 != kvp1

    def test_equality_different_types(self):
        """Test inequality when comparing with different types."""
        kvp = KeyValuePair("key", "value")

        assert kvp != "not_a_kvp"
        assert kvp != {"key": "value"}
        assert kvp != ("key", "value")
        assert kvp != None

    def test_equality_with_none_values(self):
        """Test equality when values are None."""
        kvp1 = KeyValuePair("key", None)
        kvp2 = KeyValuePair("key", None)
        kvp3 = KeyValuePair("key", "value")

        assert kvp1 == kvp2
        assert kvp1 != kvp3

    def test_equality_after_value_change(self):
        """Test equality behavior after changing mutable value."""
        kvp1 = KeyValuePair("key", "original")
        kvp2 = KeyValuePair("key", "original")

        assert kvp1 == kvp2

        # Change value in one
        kvp1.value = "changed"
        assert kvp1 != kvp2

        # Change value in the other to match
        kvp2.value = "changed"
        assert kvp1 == kvp2


class TestKeyValuePairHashing:
    """Test hashing behavior for use in sets and dictionaries."""

    def test_hash_consistency(self):
        """Test that hash is consistent for same key-value pairs."""
        kvp1 = KeyValuePair("key", "value")
        kvp2 = KeyValuePair("key", "value")

        assert hash(kvp1) == hash(kvp2)

    def test_hash_changes_with_value(self):
        """Test that hash changes when value changes."""
        kvp = KeyValuePair("key", "original")
        original_hash = hash(kvp)

        kvp.value = "changed"
        new_hash = hash(kvp)

        # Hash should change when value changes
        assert original_hash != new_hash

    def test_hashable_in_set(self):
        """Test that KeyValuePair can be used in sets."""
        kvp1 = KeyValuePair("key1", "value1")
        kvp2 = KeyValuePair("key2", "value2")
        kvp3 = KeyValuePair("key1", "value1")  # Duplicate of kvp1

        # Create set
        kvp_set = {kvp1, kvp2, kvp3}

        # Should only contain 2 unique elements
        assert len(kvp_set) == 2
        assert kvp1 in kvp_set
        assert kvp2 in kvp_set

    def test_hashable_as_dict_key(self):
        """Test that KeyValuePair can be used as dictionary key."""
        kvp1 = KeyValuePair("key1", "value1")
        kvp2 = KeyValuePair("key2", "value2")

        # Use as dictionary keys
        test_dict = {kvp1: "data1", kvp2: "data2"}

        assert test_dict[kvp1] == "data1"
        assert test_dict[kvp2] == "data2"

        # Test with equivalent KeyValuePair
        kvp1_copy = KeyValuePair("key1", "value1")
        assert test_dict[kvp1_copy] == "data1"  # Should work due to equality

    def test_hash_with_none_value(self):
        """Test hashing when value is None."""
        kvp1 = KeyValuePair("key", None)
        kvp2 = KeyValuePair("key", None)

        assert hash(kvp1) == hash(kvp2)

        # Should be usable in sets
        kvp_set = {kvp1, kvp2}
        assert len(kvp_set) == 1


class TestKeyValuePairRepresentation:
    """Test string representation."""

    def test_repr_basic(self):
        """Test basic string representation."""
        kvp = KeyValuePair("key", "value")
        repr_str = repr(kvp)

        assert "key" in repr_str
        assert "value" in repr_str
        assert "->" in repr_str

    def test_repr_with_numbers(self):
        """Test representation with numeric types."""
        kvp = KeyValuePair(42, 100)
        repr_str = repr(kvp)

        assert "42" in repr_str
        assert "100" in repr_str
        assert "->" in repr_str

    def test_repr_with_none(self):
        """Test representation when value is None."""
        kvp = KeyValuePair("key", None)
        repr_str = repr(kvp)

        assert "key" in repr_str
        assert "None" in repr_str
        assert "->" in repr_str

    def test_repr_format(self):
        """Test exact format of representation."""
        kvp = KeyValuePair("test_key", "test_value")
        expected = "(test_key -> test_value)"
        assert repr(kvp) == expected


class TestKeyValuePairTypes:
    """Test KeyValuePair with different key and value types."""

    def test_string_key_string_value(self):
        """Test with string key and value."""
        kvp = KeyValuePair("hello", "world")
        assert kvp.key == "hello"
        assert kvp.value == "world"

    def test_int_key_string_value(self):
        """Test with integer key and string value."""
        kvp = KeyValuePair(123, "number")
        assert kvp.key == 123
        assert kvp.value == "number"

    def test_string_key_int_value(self):
        """Test with string key and integer value."""
        kvp = KeyValuePair("count", 456)
        assert kvp.key == "count"
        assert kvp.value == 456

    def test_complex_types(self):
        """Test with more complex types."""
        # List as value
        kvp_list = KeyValuePair("items", [1, 2, 3])
        assert kvp_list.key == "items"
        assert kvp_list.value == [1, 2, 3]

        # Tuple as key (immutable, so valid)
        kvp_tuple = KeyValuePair((1, 2), "coordinate")
        assert kvp_tuple.key == (1, 2)
        assert kvp_tuple.value == "coordinate"

    def test_comparable_keys(self):
        """Test that keys are comparable (important for B-Tree ordering)."""
        kvp1 = KeyValuePair(10, "ten")
        kvp2 = KeyValuePair(20, "twenty")
        kvp3 = KeyValuePair(5, "five")

        # Keys should be comparable
        assert kvp1.key < kvp2.key
        assert kvp3.key < kvp1.key
        assert kvp3.key < kvp2.key

        # String keys should also be comparable
        kvp_str1 = KeyValuePair("apple", 1)
        kvp_str2 = KeyValuePair("banana", 2)
        kvp_str3 = KeyValuePair("cherry", 3)

        assert kvp_str1.key < kvp_str2.key < kvp_str3.key


class TestKeyValuePairMemoryOptimization:
    """Test memory optimization features."""

    def test_slots_memory_optimization(self):
        """Test that __slots__ is working for memory optimization."""
        kvp = KeyValuePair("key", "value")

        # Should not be able to add arbitrary attributes due to __slots__
        with pytest.raises(AttributeError):
            kvp.arbitrary_attribute = "should_fail"

    def test_slots_allowed_attributes(self):
        """Test that only allowed attributes can be set."""
        kvp = KeyValuePair("key", "value")

        # These should work (defined in __slots__)
        kvp.value = "new_value"  # value is mutable

        # Accessing _key should work (read-only)
        assert kvp._key == "key"


class TestKeyValuePairEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string_key(self):
        """Test with empty string as key."""
        kvp = KeyValuePair("", "empty_key")
        assert kvp.key == ""
        assert kvp.value == "empty_key"

    def test_empty_string_value(self):
        """Test with empty string as value."""
        kvp = KeyValuePair("key", "")
        assert kvp.key == "key"
        assert kvp.value == ""

    def test_zero_as_key(self):
        """Test with zero as key (should be valid, not None)."""
        kvp = KeyValuePair(0, "zero")
        assert kvp.key == 0
        assert kvp.value == "zero"

    def test_false_as_key(self):
        """Test with False as key (should be valid, not None)."""
        kvp = KeyValuePair(False, "false")
        assert kvp.key is False
        assert kvp.value == "false"

    def test_large_values(self):
        """Test with large data as values."""
        large_string = "x" * 10000
        kvp = KeyValuePair("large", large_string)
        assert kvp.key == "large"
        assert kvp.value == large_string
        assert len(kvp.value) == 10000


if __name__ == "__main__":
    pytest.main([__file__])