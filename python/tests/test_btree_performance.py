"""Performance and scalability tests for B-Tree implementation."""

import pytest
import time
import random
from typing import List, Tuple
import gc

from database_mechanics.indexing.btree.btree_index import BTreeIndex


class TestBTreePerformance:
    """Test B-Tree performance characteristics."""

    def measure_operation_time(self, operation_func, *args, **kwargs):
        """Utility to measure operation execution time."""
        gc.collect()  # Clean up before measurement
        start_time = time.perf_counter()
        result = operation_func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time

    def test_large_sequential_insertions(self):
        """Test performance of large sequential insertions."""
        btree = BTreeIndex[int, str](min_degree=50)  # Large degree for performance
        n = 10000

        def insert_sequential():
            for i in range(n):
                btree.insert(i, f"value_{i}")

        _, insertion_time = self.measure_operation_time(insert_sequential)

        assert len(btree) == n
        print(f"Sequential insertion of {n} elements took {insertion_time:.4f} seconds")

        # Performance expectation: should complete in reasonable time
        assert insertion_time < 5.0, f"Sequential insertion too slow: {insertion_time:.4f}s"

    def test_large_random_insertions(self):
        """Test performance of large random insertions."""
        btree = BTreeIndex[int, str](min_degree=50)
        n = 10000
        keys = list(range(n))
        random.shuffle(keys)

        def insert_random():
            for key in keys:
                btree.insert(key, f"value_{key}")

        _, insertion_time = self.measure_operation_time(insert_random)

        assert len(btree) == n
        print(f"Random insertion of {n} elements took {insertion_time:.4f} seconds")

        # Random insertion might be slightly slower than sequential
        assert insertion_time < 10.0, f"Random insertion too slow: {insertion_time:.4f}s"

    def test_search_performance(self):
        """Test search performance in large tree."""
        btree = BTreeIndex[int, str](min_degree=100)
        n = 50000

        # Build large tree
        for i in range(n):
            btree.insert(i, f"value_{i}")

        # Test search performance
        search_keys = random.sample(range(n), 1000)  # 1000 random searches

        def search_many():
            results = []
            for key in search_keys:
                result = btree.search(key)
                results.append(result)
            return results

        results, search_time = self.measure_operation_time(search_many)

        # Verify all searches succeeded
        assert all(result is not None for result in results)

        avg_search_time = search_time / len(search_keys)
        print(f"Average search time in {n}-element tree: {avg_search_time*1000:.4f} ms")

        # Should be very fast - O(log n)
        assert avg_search_time < 0.001, f"Search too slow: {avg_search_time:.6f}s per search"

    def test_mixed_operations_performance(self):
        """Test performance of mixed insert/search/delete operations."""
        btree = BTreeIndex[int, str](min_degree=20)
        n = 5000

        def mixed_operations():
            # Phase 1: Insert many elements
            for i in range(n):
                btree.insert(i, f"initial_{i}")

            # Phase 2: Mixed operations
            for i in range(n // 2):
                # Search
                btree.search(random.randint(0, n - 1))

                # Update
                key = random.randint(0, n - 1)
                btree.insert(key, f"updated_{key}_{i}")

                # Insert new
                new_key = n + i
                btree.insert(new_key, f"new_{new_key}")

            # Phase 3: Delete some elements
            delete_keys = random.sample(range(n + n // 2), n // 4)
            for key in delete_keys:
                btree.delete(key)

        _, total_time = self.measure_operation_time(mixed_operations)

        print(f"Mixed operations on {n} elements took {total_time:.4f} seconds")
        assert total_time < 15.0, f"Mixed operations too slow: {total_time:.4f}s"

    def test_deletion_performance(self):
        """Test deletion performance in large tree."""
        btree = BTreeIndex[int, str](min_degree=30)
        n = 20000

        # Build tree
        for i in range(n):
            btree.insert(i, f"value_{i}")

        # Delete half the elements
        delete_keys = random.sample(range(n), n // 2)

        def delete_many():
            for key in delete_keys:
                btree.delete(key)

        _, deletion_time = self.measure_operation_time(delete_many)

        assert len(btree) == n - len(delete_keys)
        print(f"Deletion of {len(delete_keys)} elements took {deletion_time:.4f} seconds")

        assert deletion_time < 10.0, f"Deletion too slow: {deletion_time:.4f}s"


class TestBTreeScalability:
    """Test how B-Tree scales with different sizes and configurations."""

    def test_scaling_with_size(self):
        """Test how performance scales with tree size."""
        sizes = [1000, 5000, 10000, 25000]
        min_degree = 50

        insertion_times = []
        search_times = []

        for size in sizes:
            # Test insertion scaling
            btree = BTreeIndex[int, str](min_degree=min_degree)

            start_time = time.perf_counter()
            for i in range(size):
                btree.insert(i, f"value_{i}")
            insertion_time = time.perf_counter() - start_time
            insertion_times.append(insertion_time)

            # Test search scaling
            search_keys = random.sample(range(size), min(100, size))
            start_time = time.perf_counter()
            for key in search_keys:
                btree.search(key)
            search_time = time.perf_counter() - start_time
            search_times.append(search_time / len(search_keys))

            print(f"Size {size}: Insert {insertion_time:.4f}s, "
                  f"Avg Search {search_time/len(search_keys)*1000:.4f}ms")

        # Verify logarithmic scaling for search (approximately)
        # Search time shouldn't increase dramatically with size
        assert search_times[-1] / search_times[0] < 5, "Search scaling too poor"

    def test_different_min_degrees(self):
        """Test performance with different min_degree values."""
        degrees = [3, 10, 50, 100]
        n = 10000

        for degree in degrees:
            btree = BTreeIndex[int, str](min_degree=degree)

            # Test insertion time
            start_time = time.perf_counter()
            for i in range(n):
                btree.insert(i, f"value_{i}")
            insertion_time = time.perf_counter() - start_time

            # Test search time
            search_keys = random.sample(range(n), 100)
            start_time = time.perf_counter()
            for key in search_keys:
                btree.search(key)
            search_time = time.perf_counter() - start_time

            print(f"Degree {degree}: Insert {insertion_time:.4f}s, "
                  f"Search {search_time:.4f}s")

            # All degrees should perform reasonably
            assert insertion_time < 10.0
            assert search_time < 1.0


class TestBTreeMemoryUsage:
    """Test memory usage characteristics."""

    @pytest.mark.skipif(not hasattr(gc, 'get_objects'), reason="GC introspection not available")
    def test_memory_efficiency(self):
        """Test that B-Tree doesn't have memory leaks."""
        initial_objects = len(gc.get_objects())

        # Create and populate tree
        btree = BTreeIndex[int, str](min_degree=20)
        n = 5000

        for i in range(n):
            btree.insert(i, f"value_{i}")

        mid_objects = len(gc.get_objects())

        # Delete all elements
        for i in range(n):
            btree.delete(i)

        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())

        print(f"Objects: Initial {initial_objects}, Mid {mid_objects}, Final {final_objects}")

        # After cleanup, object count should be close to initial
        # Allow some tolerance for test infrastructure
        object_increase = final_objects - initial_objects
        assert object_increase < 100, f"Possible memory leak: {object_increase} extra objects"

    def test_large_tree_memory_stability(self):
        """Test memory stability with large trees."""
        btree = BTreeIndex[int, str](min_degree=100)

        # Create large tree
        n = 50000
        for i in range(n):
            btree.insert(i, f"value_{i}")

        # Perform many operations
        for _ in range(1000):
            # Search random elements
            btree.search(random.randint(0, n - 1))

            # Update random elements
            key = random.randint(0, n - 1)
            btree.insert(key, f"updated_{key}")

        # Tree should still be functional
        assert len(btree) == n
        assert btree.search(0) == "updated_0" or btree.search(0) == "value_0"


class TestBTreeConcurrencyReadiness:
    """Test patterns that would be important for concurrent access."""

    def test_iteration_stability(self):
        """Test that searches are stable during modifications."""
        btree = BTreeIndex[int, str](min_degree=10)

        # Build initial tree
        base_keys = list(range(0, 1000, 2))  # Even numbers
        for key in base_keys:
            btree.insert(key, f"base_{key}")

        # Simulate concurrent-like access pattern
        # (Note: actual concurrency would require proper synchronization)
        search_keys = random.sample(base_keys, 100)

        for i, search_key in enumerate(search_keys):
            # Search existing key
            result = btree.search(search_key)
            assert result is not None

            # Insert new key
            new_key = 1000 + i
            btree.insert(new_key, f"new_{new_key}")

            # Search the same key again
            result2 = btree.search(search_key)
            assert result2 is not None
            assert result == result2 or result2.startswith("base_")

    def test_high_frequency_operations(self):
        """Test high frequency of operations."""
        btree = BTreeIndex[int, str](min_degree=50)
        n_operations = 10000

        # Rapid-fire mixed operations
        start_time = time.perf_counter()

        for i in range(n_operations):
            operation = i % 4
            key = random.randint(0, n_operations)

            if operation == 0:  # Insert
                btree.insert(key, f"value_{key}_{i}")
            elif operation == 1:  # Search
                btree.search(key)
            elif operation == 2:  # Update
                btree.insert(key, f"updated_{key}_{i}")
            else:  # Delete (if exists)
                btree.delete(key)

        total_time = time.perf_counter() - start_time
        ops_per_second = n_operations / total_time

        print(f"High frequency test: {ops_per_second:.0f} operations/second")
        assert ops_per_second > 1000, f"Too slow: {ops_per_second:.0f} ops/sec"


@pytest.mark.slow
class TestBTreeStressTests:
    """Long-running stress tests (marked as slow)."""

    def test_extreme_scale(self):
        """Test with very large datasets."""
        btree = BTreeIndex[int, str](min_degree=200)
        n = 100000

        print(f"Starting extreme scale test with {n} elements...")

        # Insert
        start_time = time.perf_counter()
        for i in range(n):
            btree.insert(i, f"value_{i}")
            if i % 10000 == 0:
                print(f"Inserted {i} elements...")
        insertion_time = time.perf_counter() - start_time

        # Search sample
        search_sample = random.sample(range(n), 1000)
        start_time = time.perf_counter()
        for key in search_sample:
            result = btree.search(key)
            assert result == f"value_{key}"
        search_time = time.perf_counter() - start_time

        print(f"Extreme scale: {n} insertions in {insertion_time:.2f}s, "
              f"1000 searches in {search_time:.4f}s")

        assert len(btree) == n
        assert insertion_time < 60.0  # Should complete within a minute
        assert search_time < 1.0

    def test_longevity(self):
        """Test long-running operations for stability."""
        btree = BTreeIndex[int, str](min_degree=30)
        deleted_keys = set()  # Track deleted keys

        # Run for many iterations
        for iteration in range(100):
            batch_size = 500
            base_key = iteration * batch_size

            # Insert batch
            current_batch_keys = []
            for i in range(batch_size):
                key = base_key + i
                btree.insert(key, f"iter_{iteration}_key_{key}")
                current_batch_keys.append(key)

            # Search random elements from current batch (guaranteed to exist)
            search_keys = random.sample(current_batch_keys, min(50, len(current_batch_keys)))
            for key in search_keys:
                result = btree.search(key)
                assert result is not None, f"Key {key} should exist but was not found"

            # Delete some old elements
            if iteration > 10:
                old_base = (iteration - 10) * batch_size
                delete_candidates = range(old_base, old_base + batch_size)
                # Only delete keys that haven't been deleted yet
                available_keys = [k for k in delete_candidates if k not in deleted_keys]
                if available_keys:
                    delete_keys = random.sample(available_keys, min(batch_size // 4, len(available_keys)))
                    for key in delete_keys:
                        btree.delete(key)
                        deleted_keys.add(key)

            if iteration % 20 == 0:
                print(f"Longevity test: completed {iteration} iterations, "
                      f"tree size: {len(btree)}")

        print(f"Longevity test completed: final tree size {len(btree)}")
        assert len(btree) > 0  # Should have remaining elements


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s"])  # -s to show print statements