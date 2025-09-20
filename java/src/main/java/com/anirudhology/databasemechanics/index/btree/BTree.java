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
        // Special case
        if (isEmpty()) {
            this.root.insertKeyValue(key, value);
            this.size++;
            return null;
        }
        // Reference to the root pointer
        BTreeNode<K, V> current = this.root;
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
                current = current.getChild(current.getChildIndex(key));
                // If it is a leaf node, we need to insert the new pair
                if (current.isLeaf()) {
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

    /**
     * Deletes a key from the tree.
     *
     * @param key The key to delete
     * @return The value that was associated with the key, or null if not found
     */
    public V delete(K key) {
        // TODO(human): Implement deletion operation
        return null;
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