package com.anirudhology.databasemechanics.index.btree;

import java.util.Optional;

/**
 * B-Tree implementation for database indexing.
 * <p>
 * Key characteristics:
 * - Keys and values stored in both internal and leaf nodes
 * - Self-balancing with guaranteed O(log n) operations
 * - Configurable minimum degree (t)
 * - Each node has between t-1 and 2t-1 keys (except root)
 *
 * @param <K> Key type (must be Comparable)
 * @param <V> Value type
 */
public class BTree<K extends Comparable<K>, V> {

    private final int minDegree; // Minimum degree (t)
    private BTreeNode<K, V> root;
    private int size;

    /**
     * Creates a new B-Tree with the specified minimum degree.
     *
     * @param minDegree Minimum degree (t) - must be >= 2
     */
    public BTree(int minDegree) {
        if (minDegree < 2) {
            throw new IllegalArgumentException("B-Tree minimum degree must be at least 2");
        }
        this.minDegree = minDegree;
        this.root = new BTreeNode<>(minDegree, true); // Start with empty leaf
        this.size = 0;
    }

    /**
     * Searches for a value by key.
     *
     * @param key The key to search for
     * @return Optional containing the value if found, empty otherwise
     */
    public Optional<V> search(K key) {
        // Special case
        if (isEmpty()) {
            return Optional.empty();
        }
        // Start traversing the tree to find the key
        BTreeNode<K, V> current = this.root;
        while (true) {
            final int index = current.findKeyIndex(key);
            if (index >= 0) {
                // Key found in current node
                return Optional.ofNullable(current.getValue(index));
            } else {
                // Key not found in current node
                if (current.isLeaf()) {
                    // Reached a leaf without finding the key
                    return Optional.empty();
                } else {
                    // Follow the appropriate child
                    current = current.getChild(current.getChildIndex(key));
                }
            }
        }
    }

    /**
     * Inserts a key-value pair into the tree.
     *
     * @param key   The key to insert
     * @param value The value to associate with the key
     * @return The previous value associated with the key, or null if none
     */
    public V insert(K key, V value) {
        // 1. Handle empty tree
        if (isEmpty()) {
            this.root.insertKeyValue(key, value);
            this.size++;
            return null; // Return previous value
        }
        // 2. Split root if it's full (proactive splitting)
        if (this.root.isFull()) {
            final BTreeNode<K, V> newRoot = new BTreeNode<>(this.minDegree, false);
            newRoot.insertChild(0, this.root);
            splitNode(this.root, newRoot);
            this.root = newRoot;
        }
        // 3. Simple traversal with proactive splitting
        BTreeNode<K, V> current = this.root;
        while (true) {
            final int keyIndex = current.findKeyIndex(key);
            // If the key already exists in the tree, we will only update the value
            if (keyIndex >= 0) {
                final V oldValue = current.getValue(keyIndex);
                current.getKeyValuePair(keyIndex).setValue(value);
                return oldValue;
            }
            // If the key doesn't exist in the tree - descent or insert
            if (current.isLeaf()) {
                // Leaf node - insert here (guaranteed to have space)
                current.insertKeyValue(key, value);
                this.size++;
                return null;
            }
            // For internal node - find child and split, if needed
            else {
                int childIndex = current.getChildIndex(key);
                BTreeNode<K, V> child = current.getChild(childIndex);
                // Split child if full before descending
                if (child.isFull()) {
                    splitNode(child, current);
                    // Re-determine which child to follow after split
                    childIndex = current.getChildIndex(key);
                    child = current.getChild(childIndex);
                }
                // Descend to child
                current = child;
            }
        }
    }

    private void splitNode(BTreeNode<K, V> current, BTreeNode<K, V> parent) {
        // 1. Get the middle index
        final int middleIndex = this.minDegree - 1;
        // 2. Remove middle key from the original node
        final KeyValuePair<K, V> middleKVPair = current.removeKeyValuePair(middleIndex);
        // 3. Create a new right node
        final BTreeNode<K, V> right = new BTreeNode<>(this.minDegree, current.isLeaf());
        // 4. Move keys from middleIndex + 1 ... end to the right node
        while (current.getKeyCount() > middleIndex) {
            final KeyValuePair<K, V> keyValuePair = current.removeKeyValuePair(middleIndex);
            right.insertKeyValue(keyValuePair.getKey(), keyValuePair.getValue());
        }
        // 5. If not leaf (internal node), move all children from middle + 1 ... end to right node
        if (!current.isLeaf()) {
            while (current.getChildren().size() > middleIndex + 1) {
                final BTreeNode<K, V> child = current.removeChild(middleIndex + 1);
                right.insertChild(right.getChildren().size(), child);
            }
        }
        // 6. If it comes to root split, we create a new internal node and
        // add current and right its children
        if (parent == null) {
            final BTreeNode<K, V> splitRoot = new BTreeNode<>(this.minDegree, false);
            splitRoot.insertKeyValue(middleKVPair.getKey(), middleKVPair.getValue());
            splitRoot.insertChild(0, current);
            splitRoot.insertChild(1, right);
            this.root = splitRoot;
            return;
        }
        // 7. If we are splitting internal node, we add right as its one of the children
        parent.insertKeyValue(middleKVPair.getKey(), middleKVPair.getValue());
        final int insertionIndex = parent.findKeyIndex(middleKVPair.getKey()) + 1;
        parent.insertChild(insertionIndex, right);
    }

    /**
     * Deletes a key from the tree.
     *
     * @param key The key to delete
     * @return The value that was associated with the key, or null if not found
     */
    public V delete(K key) {
        // 1. Handle empty tree
        if (isEmpty()) {
            return null;
        }
        // 2. Handle root special case, if not empty
        final V result = deleteFromNode(this.root, key);
        // Note: deleteFromNode now handles size decrement internally when successful

        // 3. If root is empty but has children, promote child to root
        if (this.root.getKeyCount() == 0 && !this.root.isLeaf()) {
            this.root = this.root.getChild(0);
        }

        return result;
    }

    private V deleteFromNode(BTreeNode<K, V> current, K key) {
        int keyIndex = current.findKeyIndex(key);

        if (keyIndex >= 0) {
            // Key found in current node
            if (current.isLeaf()) {
                // Simple leaf deletion
                V result = current.removeKeyValuePair(keyIndex).getValue();
                this.size--; // Decrement size for successful deletion
                return result;
            } else {
                // Internal node deletion - replace with successor
                V originalValue = current.getValue(keyIndex);

                // Find successor (leftmost key in right subtree)
                BTreeNode<K, V> successorNode = current.getChild(keyIndex + 1);
                while (!successorNode.isLeaf()) {
                    successorNode = successorNode.getChild(0);
                }

                // Replace with successor
                K successorKey = successorNode.getKey(0);
                V successorValue = successorNode.getValue(0);
                current.removeKeyValuePair(keyIndex);
                current.insertKeyValue(successorKey, successorValue);

                // Delete successor from leaf (this will decrement size)
                deleteFromNode(current.getChild(keyIndex + 1), successorKey);

                // Check for underflow in child after deletion
                BTreeNode<K, V> child = current.getChild(keyIndex + 1);
                if (child.getKeyCount() < minDegree - 1) {
                    fixUnderflow(current, keyIndex + 1);
                }

                return originalValue;
            }
        } else if (!current.isLeaf()) {
            // Key not found - descend to appropriate child
            int childIndex = current.getChildIndex(key);
            V result = deleteFromNode(current.getChild(childIndex), key);

            // Check for underflow in child after deletion
            if (childIndex < current.getChildren().size() &&
                    current.getChild(childIndex).getKeyCount() < minDegree - 1) {
                fixUnderflow(current, childIndex);
            }

            return result;
        }

        return null; // Key not found
    }

    /**
     * Fixes underflow in a child node by borrowing from siblings or merging.
     * This is called after a deletion has caused a child to have fewer than minDegree-1 keys.
     */
    private void fixUnderflow(BTreeNode<K, V> parent, int childIndex) {
        BTreeNode<K, V> child = parent.getChild(childIndex);

        // Defensive check - child should be under-flowing
        if (child.getKeyCount() >= minDegree - 1) {
            return; // No underflow to fix
        }

        // Try to borrow from left sibling first
        if (childIndex > 0) {
            BTreeNode<K, V> leftSibling = parent.getChild(childIndex - 1);
            if (leftSibling.getKeyCount() > minDegree - 1) {
                borrowFromLeftSibling(child, parent, childIndex);
                return;
            }
        }

        // Try to borrow from right sibling
        if (childIndex < parent.getChildren().size() - 1) {
            BTreeNode<K, V> rightSibling = parent.getChild(childIndex + 1);
            if (rightSibling.getKeyCount() > minDegree - 1) {
                borrowFromRightSibling(child, parent, childIndex);
                return;
            }
        }

        // Cannot borrow - must merge with a sibling
        if (childIndex > 0) {
            // Merge with left sibling
            mergeWithLeftSibling(child, parent, childIndex);
        } else if (childIndex < parent.getChildren().size() - 1) {
            // Merge with right sibling
            mergeWithRightSibling(child, parent, childIndex);
        }
        // If no siblings available, this indicates a structural problem,
        // but we'll let the tree continue rather than throw an exception
    }

    private void borrowFromLeftSibling(BTreeNode<K, V> node, BTreeNode<K, V> parent, int nodeIndex) {
        // 1. Get the left sibling
        final BTreeNode<K, V> leftSibling = parent.getChild(nodeIndex - 1);
        final int separatorIndex = nodeIndex - 1;
        // 2. Remove the separator from the parent
        final KeyValuePair<K, V> separator = parent.removeKeyValuePair(separatorIndex);
        // 3. Get the largest key from left sibling
        final KeyValuePair<K, V> borrowedKey = leftSibling.removeKeyValuePair(leftSibling.getKeyCount() - 1);
        // 4. Move borrowed key to the parent
        parent.insertKeyValue(borrowedKey.getKey(), borrowedKey.getValue());
        // 5. Move separator to current node at the beginning
        node.insertKeyValue(separator.getKey(), separator.getValue());
        // 6. Handle children for internal nodes
        if (!node.isLeaf()) {
            // Move right most child from the left sibling to current node
            final BTreeNode<K, V> removedChild = leftSibling.removeChild(leftSibling.getChildren().size() - 1);
            node.insertChild(0, removedChild);
        }
    }

    private void borrowFromRightSibling(BTreeNode<K, V> node, BTreeNode<K, V> parent, int nodeIndex) {
        // 1. Get the right sibling
        final BTreeNode<K, V> rightSibling = parent.getChild(nodeIndex + 1);
        // 2. Remove the separator from parent
        final KeyValuePair<K, V> separator = parent.removeKeyValuePair(nodeIndex);
        // 3. Get the smallest key from the right sibling
        final KeyValuePair<K, V> borrowedKey = rightSibling.removeKeyValuePair(0);
        // 4. Move borrowed key to the parent
        parent.insertKeyValue(borrowedKey.getKey(), borrowedKey.getValue());
        // 5. Move separator to the current node at the last
        node.insertKeyValue(separator.getKey(), separator.getValue());
        // 6. Handle children for internal nodes
        if (!node.isLeaf()) {
            // Move left most child from the right sibling to the current node
            final BTreeNode<K, V> removedChild = rightSibling.removeChild(0);
            node.insertChild(node.getChildren().size(), removedChild);
        }
    }

    private void mergeWithLeftSibling(BTreeNode<K, V> node, BTreeNode<K, V> parent, int nodeIndex) {
        final BTreeNode<K, V> leftSibling = parent.getChild(nodeIndex - 1);

        // Check if merge is safe (won't exceed maximum capacity)
        int totalKeys = leftSibling.getKeyCount() + 1 + node.getKeyCount(); // +1 for separator
        if (totalKeys > 2 * minDegree - 1) {
            // Merge would create oversized node - this shouldn't happen with proper invariants
            // Fall back to borrowing instead
            if (leftSibling.getKeyCount() > minDegree - 1) {
                borrowFromLeftSibling(node, parent, nodeIndex);
                return;
            }
        }

        // Safe to merge
        final KeyValuePair<K, V> separator = parent.removeKeyValuePair(nodeIndex - 1);
        leftSibling.insertKeyValue(separator.getKey(), separator.getValue());

        // Move all keys from current node to left sibling
        while (node.getKeyCount() > 0) {
            final KeyValuePair<K, V> removedKey = node.removeKeyValuePair(0);
            leftSibling.insertKeyValue(removedKey.getKey(), removedKey.getValue());
        }

        // Move all children from current node to left sibling
        while (!node.getChildren().isEmpty()) {
            leftSibling.insertChild(leftSibling.getChildren().size(), node.removeChild(0));
        }

        // Remove current node from parent
        parent.removeChild(nodeIndex);
    }

    private void mergeWithRightSibling(BTreeNode<K, V> node, BTreeNode<K, V> parent, int nodeIndex) {
        final BTreeNode<K, V> rightSibling = parent.getChild(nodeIndex + 1);

        // Check if merge is safe (won't exceed maximum capacity)
        int totalKeys = node.getKeyCount() + 1 + rightSibling.getKeyCount(); // +1 for separator
        if (totalKeys > 2 * minDegree - 1) {
            // Merge would create oversized node - this shouldn't happen with proper invariants
            // Fall back to borrowing instead
            if (rightSibling.getKeyCount() > minDegree - 1) {
                borrowFromRightSibling(node, parent, nodeIndex);
                return;
            }
        }

        // Safe to merge - move everything to current node first, then replace right sibling
        final KeyValuePair<K, V> separator = parent.removeKeyValuePair(nodeIndex);
        node.insertKeyValue(separator.getKey(), separator.getValue());

        // Move all keys from right sibling to current node
        while (rightSibling.getKeyCount() > 0) {
            final KeyValuePair<K, V> removedKey = rightSibling.removeKeyValuePair(0);
            node.insertKeyValue(removedKey.getKey(), removedKey.getValue());
        }

        // Move all children from right sibling to current node
        while (!rightSibling.getChildren().isEmpty()) {
            node.insertChild(node.getChildren().size(), rightSibling.removeChild(0));
        }

        // Remove right sibling from parent
        parent.removeChild(nodeIndex + 1);
    }

    /**
     * Returns the number of key-value pairs in the tree.
     */
    public int size() {
        return size;
    }

    /**
     * Returns true if the tree is empty.
     */
    public boolean isEmpty() {
        return size == 0;
    }

    /**
     * Returns the minimum degree of this tree.
     */
    public int getMinDegree() {
        return minDegree;
    }

    // Package-private getter for testing
    BTreeNode<K, V> getRoot() {
        return root;
    }

}