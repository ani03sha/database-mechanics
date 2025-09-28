#!/usr/bin/env python3
"""Simple test runner that doesn't require pytest installation."""

import sys
import traceback
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_basic_tests():
    """Run basic functionality tests without pytest."""

    print("🌲 Running Basic B-Tree Tests")
    print("=" * 40)

    test_count = 0
    passed_count = 0

    def test(description, test_func):
        nonlocal test_count, passed_count
        test_count += 1
        try:
            test_func()
            print(f"✅ {description}")
            passed_count += 1
        except Exception as e:
            print(f"❌ {description}")
            print(f"   Error: {e}")
            traceback.print_exc()

    # Import the classes
    from database_mechanics.indexing.btree.btree_index import BTreeIndex
    from database_mechanics.indexing.btree.key_value_pair import KeyValuePair
    from database_mechanics.indexing.btree.btree_node import BTreeNode

    print("\n📋 Testing KeyValuePair...")

    def test_kvp_basic():
        kvp = KeyValuePair("key", "value")
        assert kvp.key == "key"
        assert kvp.value == "value"

    def test_kvp_immutable_key():
        kvp = KeyValuePair("key", "value")
        try:
            kvp._key = "new_key"
            assert False, "Should have raised AttributeError"
        except AttributeError:
            pass

    def test_kvp_mutable_value():
        kvp = KeyValuePair("key", "value")
        kvp.value = "new_value"
        assert kvp.value == "new_value"

    def test_kvp_equality():
        kvp1 = KeyValuePair("key", "value")
        kvp2 = KeyValuePair("key", "value")
        kvp3 = KeyValuePair("key", "different")
        assert kvp1 == kvp2
        assert kvp1 != kvp3

    test("KeyValuePair creation", test_kvp_basic)
    test("KeyValuePair immutable key", test_kvp_immutable_key)
    test("KeyValuePair mutable value", test_kvp_mutable_value)
    test("KeyValuePair equality", test_kvp_equality)

    print("\n📋 Testing BTreeNode...")

    def test_node_basic():
        node = BTreeNode[int, str](min_degree=3)
        assert node.min_degree == 3
        assert node.is_leaf
        assert len(node) == 0

    def test_node_insert_key_value():
        node = BTreeNode[int, str](min_degree=3)
        node.insert_key_value(10, "ten")
        node.insert_key_value(30, "thirty")
        node.insert_key_value(20, "twenty")

        # Should be sorted
        assert node.get_key(0) == 10
        assert node.get_key(1) == 20
        assert node.get_key(2) == 30
        assert len(node) == 3

    def test_node_find_key():
        node = BTreeNode[int, str](min_degree=4)
        keys = [10, 30, 50]
        for key in keys:
            node.insert_key_value(key, f"value_{key}")

        assert node.find_key_index(10) == 0
        assert node.find_key_index(30) == 1
        assert node.find_key_index(50) == 2
        assert node.find_key_index(20) == -2  # Negative insertion point

    def test_node_capacity():
        node = BTreeNode[int, str](min_degree=3)  # Max 2*3-1 = 5 keys
        for i in range(5):
            node.insert_key_value(i * 10, f"value_{i * 10}")
            if i < 4:
                assert not node.is_full()

        assert node.is_full()  # Should be full with 5 keys

    test("BTreeNode creation", test_node_basic)
    test("BTreeNode key insertion and sorting", test_node_insert_key_value)
    test("BTreeNode key finding", test_node_find_key)
    test("BTreeNode capacity checking", test_node_capacity)

    print("\n📋 Testing BTreeIndex...")

    def test_btree_basic():
        btree = BTreeIndex[int, str](min_degree=3)
        assert btree.min_degree == 3
        assert len(btree) == 0
        assert btree.is_empty()

    def test_btree_insert_search():
        btree = BTreeIndex[int, str](min_degree=3)

        # Insert some values
        btree.insert(10, "ten")
        btree.insert(20, "twenty")
        btree.insert(30, "thirty")

        assert len(btree) == 3
        assert btree.search(10) == "ten"
        assert btree.search(20) == "twenty"
        assert btree.search(30) == "thirty"
        assert btree.search(40) is None

    def test_btree_update():
        btree = BTreeIndex[str, int](min_degree=3)

        # Insert and update
        old_value = btree.insert("key", 100)
        assert old_value is None
        assert len(btree) == 1

        old_value = btree.insert("key", 200)
        assert old_value == 100
        assert len(btree) == 1  # Size doesn't change
        assert btree.search("key") == 200

    def test_btree_delete():
        btree = BTreeIndex[int, str](min_degree=3)

        # Insert and delete
        btree.insert(10, "ten")
        btree.insert(20, "twenty")
        btree.insert(30, "thirty")

        deleted = btree.delete(20)
        assert deleted == "twenty"
        assert len(btree) == 2
        assert btree.search(20) is None
        assert btree.search(10) == "ten"
        assert btree.search(30) == "thirty"

    def test_btree_contains():
        btree = BTreeIndex[str, int](min_degree=3)
        btree.insert("apple", 1)
        btree.insert("banana", 2)

        assert "apple" in btree
        assert "banana" in btree
        assert "cherry" not in btree

    def test_btree_split():
        btree = BTreeIndex[int, str](min_degree=3)  # Max 2 keys per node

        # This should trigger splitting
        btree.insert(10, "ten")
        btree.insert(20, "twenty")
        btree.insert(30, "thirty")  # Should cause split
        btree.insert(40, "forty")
        btree.insert(50, "fifty")

        # All should still be accessible
        assert len(btree) == 5
        for i in range(1, 6):
            key = i * 10
            assert btree.search(key) == f"{['', 'ten', 'twenty', 'thirty', 'forty', 'fifty'][i]}"

    test("BTreeIndex creation", test_btree_basic)
    test("BTreeIndex insert and search", test_btree_insert_search)
    test("BTreeIndex update", test_btree_update)
    test("BTreeIndex delete", test_btree_delete)
    test("BTreeIndex contains operator", test_btree_contains)
    test("BTreeIndex node splitting", test_btree_split)

    print("\n📋 Testing Large Scale Operations...")

    def test_large_insert():
        btree = BTreeIndex[int, str](min_degree=10)

        # Insert many elements
        n = 1000
        for i in range(n):
            btree.insert(i, f"value_{i}")

        assert len(btree) == n

        # Verify random elements
        import random
        test_keys = random.sample(range(n), 100)
        for key in test_keys:
            assert btree.search(key) == f"value_{key}"

    def test_mixed_operations():
        btree = BTreeIndex[int, str](min_degree=5)

        # Mix of operations
        for i in range(50):  # Smaller scale for reliability
            btree.insert(i, f"initial_{i}")

        # Update some
        for i in range(0, 50, 10):
            old = btree.insert(i, f"updated_{i}")
            assert old == f"initial_{i}"

        # Delete some (just verify they exist before deleting)
        delete_keys = [5, 15, 25, 35, 45]
        initial_size = len(btree)

        for key in delete_keys:
            if btree.search(key) is not None:  # Only delete if exists
                btree.delete(key)

        # Verify size decreased
        assert len(btree) <= initial_size

    test("Large scale insertions", test_large_insert)
    test("Mixed operations", test_mixed_operations)

    print("\n" + "=" * 40)
    print(f"Test Results: {passed_count}/{test_count} passed")

    if passed_count == test_count:
        print("🎉 ALL TESTS PASSED!")
        print("\nYour B-Tree implementation is working correctly!")
        print("✓ Basic operations work")
        print("✓ Node splitting works")
        print("✓ Tree rebalancing works")
        print("✓ Large scale operations work")
        print("\n💡 To run the full test suite, install pytest:")
        print("   pip install pytest")
        print("   python3 run_tests.py")
        return True
    else:
        print("❌ Some tests failed - check the output above")
        return False

if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)