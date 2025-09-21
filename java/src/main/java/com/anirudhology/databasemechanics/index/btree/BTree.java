package com.anirudhology.databasemechanics.index.btree;

import java.security.Key;
import java.util.ArrayList;
import java.util.List;
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
        // Special case
        if (isEmpty()) {
            this.root.insertKeyValue(key, value);
            this.size++;
            return null;
        }
        // Reference to the root pointer
        BTreeNode<K, V> current = this.root;
        // Parent to the current node
        BTreeNode<K, V> parent = null;
        while (true) {
            final int index = current.findKeyIndex(key);
            // Key already exists in the tree, so we need to update it
            if (index >= 0) {
                // Get the current value associated with this key
                final KeyValuePair<K, V> existingEntry = current.getKeyValuePair(index);
                final V previousValue = existingEntry.getValue();
                // Update the value
                existingEntry.setValue(value);
                return previousValue;
            }
            // When key isn't found in the current node, navigate to its children
            else {
                parent = current;
                current = current.getChild(current.getChildIndex(key));
                // If it is a leaf node, we need to insert the new pair
                if (current.isLeaf()) {
                    if (current.getKeyCount() >= 2 * minDegree - 1) {
                        // Split the node
                        splitNode(current, parent);
                    }
                    final int keyIndexInLeaf = current.findKeyIndex(key);
                    if (keyIndexInLeaf >= 0) {
                        // Get the current value associated with this key
                        final KeyValuePair<K, V> existingEntry = current.getKeyValuePair(keyIndexInLeaf);
                        final V previousValue = existingEntry.getValue();
                        // Update the value
                        existingEntry.setValue(value);
                        return previousValue;
                    } else {
                        current.insertKeyValue(key, value);
                        this.size++;
                        return null;
                    }
                }
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
        // 1 Traverse the tree to find the key-value pair with key
        BTreeNode<K, V> current = this.root;
        BTreeNode<K, V> parent = null;
        int nodeIndex = 0;
        while (true) {
            final int index = current.findKeyIndex(key);
            // 1.1 Key found in the current node
            if (index >= 0) {
                // Leaf node and it is not under-flowing with keys
                if (current.isLeaf()) {
                    KeyValuePair<K, V> removedNode = current.removeKeyValuePair(index);
                    this.size--;
                    fixUnderflow(current, parent, nodeIndex);
                    return removedNode.getValue();
                } else {
                    // Internal node deletion - replace with successor
                    final V originalValue = current.getValue(index);
                    // Track path to successor for underflow handling
                    final List<BTreeNode<K, V>> successorPath = new ArrayList<>();
                    final List<Integer> successorIndices = new ArrayList<>();
                    // Find successor and track the path
                    BTreeNode<K, V> successor = current.getChild(index + 1);
                    successorPath.add(current);
                    successorIndices.add(index + 1);
                    while (!successor.isLeaf()) {
                        successorPath.add(successor);
                        successorIndices.add(0); // Always go left to find minimum
                        successor = successor.getChild(0);
                    }
                    // Get successor key-value pair and replace in current node
                    final KeyValuePair<K, V> successorKVPair = successor.getKeyValuePair(0);
                    current.removeKeyValuePair(index);
                    current.insertKeyValue(successorKVPair.getKey(), successorKVPair.getValue());
                    // Remove successor from leaf
                    successor.removeKeyValuePair(0);
                    this.size--;
                    // Handle underflow bottom-up along successor path
                    BTreeNode<K, V> currentNode = successor;
                    for (int i = successorPath.size() - 1; i >= 0; i--) {
                        BTreeNode<K, V> parentNode = successorPath.get(i);
                        int nodeIdx = successorIndices.get(i);
                        fixUnderflow(currentNode, parentNode, nodeIdx);
                        currentNode = parentNode;
                    }
                    return originalValue;
                }
            }
            // 1.2 If node is not found in the tree
            else {
                if (current.isLeaf()) {
                    return null;
                }
                parent = current;
                nodeIndex = current.getChildIndex(key);
                current = current.getChild(nodeIndex);
            }
        }
    }

    private void fixUnderflow(BTreeNode<K, V> node, BTreeNode<K, V> parent, int nodeIndex) {
        if (!hasUnderflow(node)) {
            // No underflow to fix
            return;
        }
        // Root underflow
        if (parent == null) {
            if (node.getKeyCount() == 0 && !node.isLeaf()) {
                // Root is empty but has children - make first child new root
                this.root = node.getChild(0);
            }
            return;
        }
        // Try borrowing first
        if (canBorrowFromLeftSibling(node, parent, nodeIndex)) {
            borrowFromLeftSibling(node, parent, nodeIndex);
        } else if (canBorrowFromRightSibling(node, parent, nodeIndex)) {
            borrowFromRightSibling(node, parent, nodeIndex);
        } else {
            // Must merge
            if (nodeIndex > 0) {
                mergeWithLeftSibling(node, parent, nodeIndex);
            } else {
                mergeWithRightSibling(node, parent, nodeIndex);
            }
        }
    }

    private boolean hasUnderflow(BTreeNode<K, V> node) {
        return node.getKeyCount() < this.minDegree - 1;
    }

    private boolean canBorrowFromLeftSibling(BTreeNode<K, V> node, BTreeNode<K, V> parent, int nodeIndex) {
        return nodeIndex > 0 && parent.getChild(nodeIndex - 1).getKeyCount() > this.minDegree - 1;
    }

    private boolean canBorrowFromRightSibling(BTreeNode<K, V> node, BTreeNode<K, V> parent, int nodeIndex) {
        return nodeIndex < parent.getKeyCount() && parent.getChild(nodeIndex + 1).getKeyCount() > this.minDegree - 1;
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
        // 1. Get the left sibling
        final BTreeNode<K, V> leftSibling = parent.getChild(nodeIndex - 1);
        // 2. Remove the separator from parent
        final KeyValuePair<K, V> separator = parent.removeKeyValuePair(nodeIndex - 1);
        // 3. Move separator and all keys in node to leftSibling
        leftSibling.insertKeyValue(separator.getKey(), separator.getValue());
        while (node.getKeyCount() > 0) {
            final KeyValuePair<K, V> removedKey = node.removeKeyValuePair(0);
            leftSibling.insertKeyValue(removedKey.getKey(), removedKey.getValue());
        }
        // 4. Move all children of node to leftSibling
        while (!node.getChildren().isEmpty()) {
            leftSibling.insertChild(leftSibling.getChildren().size(), node.removeChild(0));
        }
        // 5. Remove current node from parent
        parent.removeChild(nodeIndex);
    }

    private void mergeWithRightSibling(BTreeNode<K, V> node, BTreeNode<K, V> parent, int nodeIndex) {
        // 1. Get the right sibling
        final BTreeNode<K, V> rightSibling = parent.getChild(nodeIndex + 1);
        // 2. Remove separator from parent
        final KeyValuePair<K, V> separator = parent.removeKeyValuePair(nodeIndex);
        // 3. Move separator and all keys in node to rightSibling
        rightSibling.insertKeyValue(separator.getKey(), separator.getValue());
        while (node.getKeyCount() > 0) {
            final KeyValuePair<K, V> removedKey = node.removeKeyValuePair(0);
            rightSibling.insertKeyValue(removedKey.getKey(), removedKey.getValue());
        }
        // 4. Move all children of node to rightSibling
        while (!node.getChildren().isEmpty()) {
            rightSibling.insertChild(rightSibling.getChildren().size(), node.removeChild(0));
        }
        // 5. Remove current node from parent
        parent.removeChild(nodeIndex);
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

    // Helper method to set root (used during splits)
    void setRoot(BTreeNode<K, V> newRoot) {
        this.root = newRoot;
    }

    // Helper method to increment size
    void incrementSize() {
        this.size++;
    }

    // Helper method to decrement size
    void decrementSize() {
        this.size--;
    }
}