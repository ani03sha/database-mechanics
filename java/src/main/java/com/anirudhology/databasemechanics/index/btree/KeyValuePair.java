package com.anirudhology.databasemechanics.index.btree;

import java.util.Objects;

/**
 * Represents a key-value pair stored in B-Tree nodes.
 *
 * @param <K> Key type
 * @param <V> Value type
 */
public class KeyValuePair<K, V> {
    private final K key;
    private V value;

    public KeyValuePair(K key, V value) {
        this.key = Objects.requireNonNull(key, "Key cannot be null");
        this.value = value;
    }

    public K getKey() {
        return key;
    }

    public V getValue() {
        return value;
    }

    public void setValue(V value) {
        this.value = value;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        KeyValuePair<?, ?> that = (KeyValuePair<?, ?>) obj;
        return Objects.equals(key, that.key) && Objects.equals(value, that.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(key, value);
    }

    @Override
    public String toString() {
        return String.format("(%s -> %s)", key, value);
    }
}