package com.anirudhology.databasemechanics.index.btree;

import java.util.ArrayList;
import java.util.List;

/**
 * Represents a node in a B-Tree.
 * <p>
 * Each node contains:
 * - A list of key-value pairs (sorted by key)
 * - A list of child pointers (for internal nodes)
 * - A flag indicating if this is a leaf node
 *
 * @param <K> Key type (must be Comparable)
 * @param <V> Value type
 */
public class BTreeNode<K extends Comparable<K>, V> {

    private final int minDegree; // Minimum degree (t)
    private final List<KeyValuePair<K, V>> keyValuePairs;
    private final List<BTreeNode<K, V>> children;
    private boolean isLeaf;

    /**
     * Creates a new B-Tree node.
     *
     * @param minDegree Minimum degree of the B-Tree
     * @param isLeaf    True if this is a leaf node, false otherwise
     */
    public BTreeNode(int minDegree, boolean isLeaf) {
        this.minDegree = minDegree;
        this.isLeaf = isLeaf;
        this.keyValuePairs = new ArrayList<>();
        this.children = new ArrayList<>();
    }

    /**
     * Returns the number of keys in this node.
     */
    public int getKeyCount() {
        return keyValuePairs.size();
    }

    /**
     * Returns the key at the specified index.
     */
    public K getKey(int index) {
        return getKeyValuePair(index).getKey();
    }

    /**
     * Returns the value at the specified index.
     */
    public V getValue(int index) {
        return getKeyValuePair(index).getValue();
    }

    /**
     * Returns the key-value pair at the specified index.
     */
    public KeyValuePair<K, V> getKeyValuePair(int index) {
        return keyValuePairs.get(index);
    }

    /**
     * Returns the child at the specified index.
     */
    public BTreeNode<K, V> getChild(int index) {
        return children.get(index);
    }

    /**
     * Returns true if this is a leaf node.
     */
    public boolean isLeaf() {
        return isLeaf;
    }

    /**
     * Sets whether this node is a leaf.
     */
    public void setLeaf(boolean leaf) {
        this.isLeaf = leaf;
    }

    /**
     * Returns true if this node is full (has maximum number of keys).
     */
    public boolean isFull() {
        return keyValuePairs.size() == (2 * minDegree - 1);
    }

    /**
     * Returns true if this node has minimum number of keys.
     */
    public boolean hasMinimumKeys() {
        return keyValuePairs.size() >= (minDegree - 1);
    }

    /**
     * Adds a key-value pair to this node at the appropriate position.
     * Assumes the node is not full.
     */
    public void insertKeyValue(K key, V value) {
        this.keyValuePairs.add(new KeyValuePair<>(key, value));
    }

    /**
     * Adds a child at the specified index.
     */
    public void insertChild(int index, BTreeNode<K, V> child) {
        children.add(index, child);
    }

    /**
     * Removes and returns the key-value pair at the specified index.
     */
    public KeyValuePair<K, V> removeKeyValuePair(int index) {
        return keyValuePairs.remove(index);
    }

    /**
     * Removes and returns the child at the specified index.
     */
    public BTreeNode<K, V> removeChild(int index) {
        return children.remove(index);
    }

    /**
     * Finds the index of a key in this node using binary search.
     *
     * @param key The key to search for
     * @return If found: the index of the key (>= 0)
     * If not found: negative insertion point (-insertionIndex - 1)
     */
    public int findKeyIndex(K key) {
        if (this.keyValuePairs.isEmpty()) {
            return -1; // Insert at position 0: -(0) - 1 = -1
        }
        // Perform Binary Search on this node
        int left = 0;
        int right = this.keyValuePairs.size() - 1;
        while (left <= right) {
            final int middle = left + (right - left) / 2;
            final int comparison = this.keyValuePairs.get(middle).getKey().compareTo(key);
            if (comparison == 0) {
                return middle; // Found exact match
            } else if (comparison < 0) {
                left = middle + 1; // Key is in right half
            } else {
                right = middle - 1; // Key is in left half
            }
        }
        // Not found - return negative insertion point
        return -(left + 1);
    }

    /**
     * Helper method to get child index for a given key.
     * For internal nodes, this tells us which child to follow.
     */
    public int getChildIndex(K key) {
        final int keyIndex = findKeyIndex(key);
        if (keyIndex >= 0) {
            // Key found - could go to either child, typically go right
            return keyIndex + 1;
        } else {
            // Key not found - convert negative insertion point to child index
            return -(keyIndex + 1);
        }
    }
    // TODO(human): Add methods for splitting this node when full
    // TODO(human): Add methods for merging nodes during deletion

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("Node[");
        for (int i = 0; i < keyValuePairs.size(); i++) {
            if (i > 0) sb.append(", ");
            sb.append(keyValuePairs.get(i).getKey());
        }
        sb.append("]");
        if (isLeaf) sb.append(" (leaf)");
        return sb.toString();
    }
}