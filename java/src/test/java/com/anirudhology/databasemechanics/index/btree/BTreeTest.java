package com.anirudhology.databasemechanics.index.btree;

import static org.assertj.core.api.Assertions.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Random;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class BTreeTest {

    private BTree<Integer, String> btree;
    private static final int MIN_DEGREE = 3; // Order 3 B-Tree for testing

    @BeforeEach
    void setUp() {
        btree = new BTree<>(MIN_DEGREE);
    }

    @Nested
    @DisplayName("Constructor and Basic Properties")
    class ConstructorTests {

        @Test
        @DisplayName("Should create empty B-Tree with correct properties")
        void shouldCreateEmptyBTree() {
            assertThat(btree.isEmpty()).isTrue();
            assertThat(btree.size()).isZero();
            assertThat(btree.getMinDegree()).isEqualTo(MIN_DEGREE);
        }

        @Test
        @DisplayName("Should reject invalid minimum degree")
        void shouldRejectInvalidMinDegree() {
            assertThatThrownBy(() -> new BTree<Integer, String>(1))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("minimum degree must be at least 2");
        }

        @Test
        @DisplayName("Should accept minimum valid degree")
        void shouldAcceptMinimumValidDegree() {
            BTree<Integer, String> tree = new BTree<>(2);
            assertThat(tree.getMinDegree()).isEqualTo(2);
        }
    }

    @Nested
    @DisplayName("Search Operations")
    class SearchTests {

        @Test
        @DisplayName("Should return empty optional for key in empty tree")
        void shouldReturnEmptyForEmptyTree() {
            Optional<String> result = btree.search(42);
            assertThat(result).isEmpty();
        }

        @Test
        @DisplayName("Should find existing key in single-node tree")
        void shouldFindKeyInSingleNode() {
            btree.insert(10, "ten");
            btree.insert(20, "twenty");

            assertThat(btree.search(10)).contains("ten");
            assertThat(btree.search(20)).contains("twenty");
        }

        @Test
        @DisplayName("Should return empty for non-existing key")
        void shouldReturnEmptyForNonExistingKey() {
            btree.insert(10, "ten");
            assertThat(btree.search(99)).isEmpty();
        }

        @Test
        @DisplayName("Should find keys in multi-level tree")
        void shouldFindKeysInMultiLevelTree() {
            // Insert enough keys to create multiple levels
            for (int i = 1; i <= 20; i++) {
                btree.insert(i, "value" + i);
            }

            // Test searching for various keys
            assertThat(btree.search(1)).contains("value1");
            assertThat(btree.search(10)).contains("value10");
            assertThat(btree.search(20)).contains("value20");
            assertThat(btree.search(99)).isEmpty();
        }
    }

    @Nested
    @DisplayName("Insertion Operations")
    class InsertionTests {

        @Test
        @DisplayName("Should insert single key-value pair")
        void shouldInsertSinglePair() {
            String result = btree.insert(42, "answer");

            assertThat(result).isNull(); // No previous value
            assertThat(btree.size()).isEqualTo(1);
            assertThat(btree.isEmpty()).isFalse();
            assertThat(btree.search(42)).contains("answer");
        }

        @Test
        @DisplayName("Should update existing key and return previous value")
        void shouldUpdateExistingKey() {
            btree.insert(10, "original");
            String previous = btree.insert(10, "updated");

            assertThat(previous).isEqualTo("original");
            assertThat(btree.size()).isEqualTo(1); // Size shouldn't change
            assertThat(btree.search(10)).contains("updated");
        }

        @Test
        @DisplayName("Should maintain sorted order in leaf nodes")
        void shouldMaintainSortedOrder() {
            // Insert in random order
            btree.insert(30, "thirty");
            btree.insert(10, "ten");
            btree.insert(20, "twenty");

            // Verify all can be found (implying correct order)
            assertThat(btree.search(10)).contains("ten");
            assertThat(btree.search(20)).contains("twenty");
            assertThat(btree.search(30)).contains("thirty");
        }

        @Test
        @DisplayName("Should handle node splitting correctly")
        void shouldHandleNodeSplitting() {
            // Insert enough keys to trigger splits (for minDegree=3, max keys per node = 5)
            for (int i = 1; i <= 10; i++) {
                btree.insert(i, "value" + i);
            }

            assertThat(btree.size()).isEqualTo(10);

            // Verify all keys are still searchable after splits
            for (int i = 1; i <= 10; i++) {
                assertThat(btree.search(i)).contains("value" + i);
            }
        }

        @Test
        @DisplayName("Should handle large number of insertions")
        void shouldHandleLargeInsertions() {
            int numKeys = 1000;

            for (int i = 0; i < numKeys; i++) {
                btree.insert(i, "value" + i);
            }

            assertThat(btree.size()).isEqualTo(numKeys);

            // Test random access
            Random random = new Random(42); // Seeded for reproducibility
            for (int i = 0; i < 100; i++) {
                int key = random.nextInt(numKeys);
                assertThat(btree.search(key)).contains("value" + key);
            }
        }
    }

    // Helper method for testing tree invariants
    private void assertBTreeInvariants(BTreeNode<Integer, String> node,
                                      Integer minKey, Integer maxKey, int level) {
        if (node == null) return;

        // Check key count constraints
        if (level == 0) {
            // Root can have fewer keys
            assertThat(node.getKeyCount()).isLessThanOrEqualTo(2 * MIN_DEGREE - 1);
        } else {
            // Non-root nodes must have at least minDegree-1 keys
            assertThat(node.getKeyCount()).isBetween(MIN_DEGREE - 1, 2 * MIN_DEGREE - 1);
        }

        // Check key ordering within node
        for (int i = 1; i < node.getKeyCount(); i++) {
            assertThat(node.getKey(i)).isGreaterThan(node.getKey(i - 1));
        }

        // Check key range constraints
        if (minKey != null) {
            assertThat(node.getKey(0)).isGreaterThanOrEqualTo(minKey);
        }
        if (maxKey != null) {
            assertThat(node.getKey(node.getKeyCount() - 1)).isLessThanOrEqualTo(maxKey);
        }

        // Recursively check children
        if (!node.isLeaf()) {
            assertThat(node.getChildren().size()).isEqualTo(node.getKeyCount() + 1);

            for (int i = 0; i <= node.getKeyCount(); i++) {
                Integer childMinKey = (i == 0) ? minKey : node.getKey(i - 1);
                Integer childMaxKey = (i == node.getKeyCount()) ? maxKey : node.getKey(i);

                assertBTreeInvariants(node.getChild(i), childMinKey, childMaxKey, level + 1);
            }
        }
    }

    @Test
    @DisplayName("Should maintain B-Tree invariants after insertions")
    void shouldMaintainBTreeInvariants() {
        // Insert keys that will trigger multiple splits
        List<Integer> keys = Arrays.asList(10, 20, 5, 6, 12, 30, 7, 17, 25, 40, 1, 15, 35);

        for (Integer key : keys) {
            btree.insert(key, "value" + key);

            // Check invariants after each insertion
            assertBTreeInvariants(btree.getRoot(), null, null, 0);
        }
    }

    @Nested
    @DisplayName("Deletion Operations")
    class DeletionTests {

        @Test
        @DisplayName("Should return null when deleting from empty tree")
        void shouldReturnNullForEmptyTree() {
            String result = btree.delete(42);
            assertThat(result).isNull();
            assertThat(btree.isEmpty()).isTrue();
        }

        @Test
        @DisplayName("Should delete existing key from single-node tree")
        void shouldDeleteFromSingleNode() {
            btree.insert(10, "ten");
            String result = btree.delete(10);

            assertThat(result).isEqualTo("ten");
            assertThat(btree.size()).isZero();
            assertThat(btree.isEmpty()).isTrue();
            assertThat(btree.search(10)).isEmpty();
        }

        @Test
        @DisplayName("Should return null when deleting non-existing key")
        void shouldReturnNullForNonExistingKey() {
            btree.insert(10, "ten");
            String result = btree.delete(99);

            assertThat(result).isNull();
            assertThat(btree.size()).isEqualTo(1); // Size unchanged
            assertThat(btree.search(10)).contains("ten"); // Original key still there
        }

        @Test
        @DisplayName("Should delete key from leaf node without underflow")
        void shouldDeleteFromLeafWithoutUnderflow() {
            // Create a tree with enough keys to avoid underflow
            for (int i = 1; i <= 10; i++) {
                btree.insert(i, "value" + i);
            }

            String result = btree.delete(5);

            assertThat(result).isEqualTo("value5");
            assertThat(btree.size()).isEqualTo(9);
            assertThat(btree.search(5)).isEmpty();

            // Verify other keys are still there
            for (int i = 1; i <= 10; i++) {
                if (i != 5) {
                    assertThat(btree.search(i)).contains("value" + i);
                }
            }
        }

        @Test
        @DisplayName("Should delete key from internal node using successor replacement")
        void shouldDeleteFromInternalNode() {
            // Insert keys to create multi-level tree
            for (int i = 1; i <= 15; i++) {
                btree.insert(i, "value" + i);
            }

            // Delete a key that's likely in an internal node
            String result = btree.delete(8);

            assertThat(result).isEqualTo("value8");
            assertThat(btree.size()).isEqualTo(14);
            assertThat(btree.search(8)).isEmpty();

            // Verify tree structure is still valid
            assertBTreeInvariants(btree.getRoot(), null, null, 0);
        }

        @Test
        @DisplayName("Should handle deletion causing underflow with borrowing")
        void shouldHandleUnderflowWithBorrowing() {
            // Create specific scenario for borrowing
            // Insert keys: 1,2,3,4,5,6,7,8,9,10
            for (int i = 1; i <= 10; i++) {
                btree.insert(i, "value" + i);
            }

            // Delete keys to create underflow that can be resolved by borrowing
            btree.delete(1);
            btree.delete(2);

            assertThat(btree.size()).isEqualTo(8);
            assertThat(btree.search(1)).isEmpty();
            assertThat(btree.search(2)).isEmpty();

            // Verify remaining keys
            for (int i = 3; i <= 10; i++) {
                assertThat(btree.search(i)).contains("value" + i);
            }

            // Check invariants
            assertBTreeInvariants(btree.getRoot(), null, null, 0);
        }

        @Test
        @DisplayName("Should handle deletion causing underflow with merging")
        void shouldHandleUnderflowWithMerging() {
            // Create scenario where borrowing isn't possible and merging is needed
            List<Integer> keys = Arrays.asList(5, 10, 15, 20, 25, 30);

            for (Integer key : keys) {
                btree.insert(key, "value" + key);
            }

            // Delete keys to force merging
            btree.delete(5);
            btree.delete(10);
            btree.delete(15);

            assertThat(btree.size()).isEqualTo(3);

            // Verify remaining keys
            assertThat(btree.search(20)).contains("value20");
            assertThat(btree.search(25)).contains("value25");
            assertThat(btree.search(30)).contains("value30");

            // Check invariants
            assertBTreeInvariants(btree.getRoot(), null, null, 0);
        }

        @Test
        @DisplayName("Should handle cascading deletion operations")
        void shouldHandleCascadingDeletions() {
            // Insert a larger set of keys
            for (int i = 1; i <= 20; i++) {
                btree.insert(i, "value" + i);
            }

            // Delete keys in a pattern that might cause cascading underflow
            List<Integer> keysToDelete = Arrays.asList(1, 3, 5, 7, 9, 11, 13, 15, 17, 19);

            for (Integer key : keysToDelete) {
                String result = btree.delete(key);
                assertThat(result).isEqualTo("value" + key);

                // Check invariants after each deletion
                assertBTreeInvariants(btree.getRoot(), null, null, 0);
            }

            assertThat(btree.size()).isEqualTo(10);

            // Verify remaining keys
            List<Integer> remainingKeys = Arrays.asList(2, 4, 6, 8, 10, 12, 14, 16, 18, 20);
            for (Integer key : remainingKeys) {
                assertThat(btree.search(key)).contains("value" + key);
            }
        }

        @Test
        @DisplayName("Should handle deleting all keys one by one")
        void shouldDeleteAllKeys() {
            // Insert keys
            List<Integer> keys = new ArrayList<>();
            for (int i = 1; i <= 15; i++) {
                keys.add(i);
                btree.insert(i, "value" + i);
            }

            // Shuffle for random deletion order
            Collections.shuffle(keys, new Random(42));

            // Delete all keys
            for (Integer key : keys) {
                String result = btree.delete(key);
                assertThat(result).isEqualTo("value" + key);

                // Check invariants after each deletion (if tree is not empty)
                if (!btree.isEmpty()) {
                    assertBTreeInvariants(btree.getRoot(), null, null, 0);
                }
            }

            assertThat(btree.isEmpty()).isTrue();
            assertThat(btree.size()).isZero();
        }
    }

    @Nested
    @DisplayName("Edge Cases and Stress Tests")
    class EdgeCaseTests {

        @Test
        @DisplayName("Should handle minimum degree edge case")
        void shouldHandleMinimumDegree() {
            BTree<Integer, String> minTree = new BTree<>(2); // Minimum possible degree

            // Insert and delete to test with the smallest possible tree
            for (int i = 1; i <= 10; i++) {
                minTree.insert(i, "value" + i);
            }

            for (int i = 1; i <= 5; i++) {
                String result = minTree.delete(i);
                assertThat(result).isEqualTo("value" + i);
            }

            assertThat(minTree.size()).isEqualTo(5);
        }

        @Test
        @DisplayName("Should handle duplicate key operations")
        void shouldHandleDuplicateKeys() {
            // Insert same key multiple times
            assertThat(btree.insert(10, "first")).isNull();
            assertThat(btree.insert(10, "second")).isEqualTo("first");
            assertThat(btree.insert(10, "third")).isEqualTo("second");

            assertThat(btree.size()).isEqualTo(1);
            assertThat(btree.search(10)).contains("third");

            // Delete and verify
            assertThat(btree.delete(10)).isEqualTo("third");
            assertThat(btree.isEmpty()).isTrue();
        }

        @Test
        @DisplayName("Should handle null values correctly")
        void shouldHandleNullValues() {
            btree.insert(10, null);

            // Check that the key exists but has null value
            Optional<String> result = btree.search(10);
            assertThat(result).isEmpty();

            String deleteResult = btree.delete(10);
            assertThat(deleteResult).isNull();
            assertThat(btree.isEmpty()).isTrue();
        }

        @Test
        @DisplayName("Should handle mixed insertion and deletion operations")
        void shouldHandleMixedOperations() {
            Random random = new Random(42);
            int operations = 100;
            int maxKey = 50;

            for (int i = 0; i < operations; i++) {
                if (random.nextBoolean() || btree.isEmpty()) {
                    // Insert operation
                    int key = random.nextInt(maxKey);
                    btree.insert(key, "value" + key);
                } else {
                    // Delete operation
                    int key = random.nextInt(maxKey);
                    btree.delete(key);
                }

                // Verify tree is still valid after each operation
                if (!btree.isEmpty()) {
                    assertBTreeInvariants(btree.getRoot(), null, null, 0);
                }
            }
        }

        @Test
        @DisplayName("Should handle large scale operations")
        void shouldHandleLargeScaleOperations() {
            int numKeys = 10000;

            // Insert many keys
            for (int i = 0; i < numKeys; i++) {
                btree.insert(i, "value" + i);
            }

            assertThat(btree.size()).isEqualTo(numKeys);

            // Delete every other key
            for (int i = 0; i < numKeys; i += 2) {
                String result = btree.delete(i);
                assertThat(result).isEqualTo("value" + i);
            }

            assertThat(btree.size()).isEqualTo(numKeys / 2);

            // Verify remaining keys
            Random random = new Random(42);
            for (int i = 0; i < 100; i++) {
                int key = random.nextInt(numKeys);
                if (key % 2 == 1) { // Odd keys should still exist
                    assertThat(btree.search(key)).contains("value" + key);
                } else { // Even keys should be deleted
                    assertThat(btree.search(key)).isEmpty();
                }
            }
        }

        @Test
        @DisplayName("Should maintain performance characteristics")
        void shouldMaintainPerformanceCharacteristics() {
            int numKeys = 1000;

            // Time insertions
            long startTime = System.nanoTime();
            for (int i = 0; i < numKeys; i++) {
                btree.insert(i, "value" + i);
            }
            long insertTime = System.nanoTime() - startTime;

            // Time searches
            startTime = System.nanoTime();
            for (int i = 0; i < numKeys; i++) {
                btree.search(i);
            }
            long searchTime = System.nanoTime() - startTime;

            // Time deletions
            startTime = System.nanoTime();
            for (int i = 0; i < numKeys; i++) {
                btree.delete(i);
            }
            long deleteTime = System.nanoTime() - startTime;

            // These are rough performance expectations (not strict requirements)
            // Mainly to ensure we don't have catastrophic performance regression
            assertThat(insertTime).isLessThan(100_000_000L); // 100ms
            assertThat(searchTime).isLessThan(50_000_000L);  // 50ms
            assertThat(deleteTime).isLessThan(100_000_000L); // 100ms

            assertThat(btree.isEmpty()).isTrue();
        }

        @Test
        @DisplayName("Should handle sequential vs random key patterns")
        void shouldHandleKeyPatterns() {
            // Test with sequential keys
            BTree<Integer, String> seqTree = new BTree<>(MIN_DEGREE);
            for (int i = 1; i <= 100; i++) {
                seqTree.insert(i, "seq" + i);
            }

            // Test with random keys
            BTree<Integer, String> randTree = new BTree<>(MIN_DEGREE);
            List<Integer> randomKeys = new ArrayList<>();
            for (int i = 1; i <= 100; i++) {
                randomKeys.add(i);
            }
            Collections.shuffle(randomKeys, new Random(42));

            for (Integer key : randomKeys) {
                randTree.insert(key, "rand" + key);
            }

            // Both trees should have same size and find all keys
            assertThat(seqTree.size()).isEqualTo(randTree.size()).isEqualTo(100);

            for (int i = 1; i <= 100; i++) {
                assertThat(seqTree.search(i)).contains("seq" + i);
                assertThat(randTree.search(i)).contains("rand" + i);
            }

            // Both should maintain invariants
            assertBTreeInvariants(seqTree.getRoot(), null, null, 0);
            assertBTreeInvariants(randTree.getRoot(), null, null, 0);
        }
    }
}