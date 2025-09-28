from typing import Generic, TypeVar, Optional
from .btree_node import BTreeNode

K = TypeVar("K")
V = TypeVar("V")

class BTreeIndex(Generic[K, V]):
    """
    Production-grade B-Tree index implementation with memory optimization.

    Provides O(log n) search, insert, and delete operations with automatic
    rebalancing. Uses memory-efficient design suitable for millions of entries.

    Args:
        min_degree: Minimum degree (t) of the B-Tree, must be >= 2
    """
    __slots__ = ("_min_degree", "_root", "_size")

    def __init__(self, min_degree: int):
        if min_degree < 2:
            raise ValueError("Minimum degree must be at least 2")
        # Make _min_degree immutable
        super().__setattr__("_min_degree", min_degree)
        self._root = BTreeNode(self._min_degree, True)
        self._size = 0


    def search(self, key: K) -> Optional[V]:
        if self.is_empty():
            return None
        
        # Traverse the tree to find the key
        current = self._root
        while True:
            index = current.find_key_index(key)

            if index >= 0: # If key is found in the node
                return current.get_value(index)
            else:
                # If the current node is leaf, it means the key is not present in the tree
                if current.is_leaf:
                    return None
                else:
                    current = current.get_child(current.get_child_index(key))

    def insert(self, key: K, value: V) -> Optional[V]:
        # 1. Handle empty tree
        if self.is_empty():
            self._root.insert_key_value(key, value)
            self._size += 1
            return None
        
        # 2. Split root if it's full (proactive splitting)
        if self._root.is_full():
            new_root = BTreeNode(self._min_degree, False)
            new_root.insert_child(0, self._root)
            self._split_node(self._root, new_root)
            self._root = new_root

        # 3. Simple traversal with proactive splitting
        current = self._root
        while True:
            key_index = current.find_key_index(key)
            # If key already exists in the tree, we will only update the value
            if key_index >= 0:
                old_value = current.get_value(key_index)
                current.get_key_value_pair(key_index).value = value
                return old_value
            
            # If the key doesn't exist in the tree - descent or insert
            if current.is_leaf:
                # Leaf node - insert here (guaranteed to have space)
                current.insert_key_value(key, value)
                self._size += 1
                return None
            else:
                # For internal node, find child or split
                child_index = current.get_child_index(key)
                child = current.get_child(child_index)
                # Split child if full, before descending
                if child.is_full():
                    self._split_node(child, current)
                    child_index = current.get_child_index(key)
                    child = current.get_child(child_index)
                # Descend to child
                current = child
            

    def delete(self, key: K) -> Optional[V]:
        # 1. Handle empty tree
        if self.is_empty():
            return None

        # 2. Handle root
        result = self._delete_from_node(self._root, key)
        # 3. If root is empty but has children, promote child to root
        if len(self._root) == 0 and not self._root.is_leaf:
            self._root = self._root.get_child(0)
        
        return result


    
    def _split_node(self, current: BTreeNode[K, V], parent: BTreeNode[K, V]) -> None:
        # 1. Get the middle index
        middle_index = self._min_degree - 1
        # 2. Remove middle key from the original node
        middle_kv_pair = current.remove_key_value_pair(middle_index)
        # 3. Create new right node
        right = BTreeNode(self._min_degree, current.is_leaf)
        
        # 4. Move keys from middle_index + 1 ... end to the right node
        while len(current) > middle_index:
            key_value_pair = current.remove_key_value_pair(middle_index)
            right.insert_key_value(key_value_pair.key, key_value_pair.value)
        
        # 5. If not leaf (internal node), move all children from middle_index + 1 ... end
        # to the right node
        if not current.is_leaf:
            while len(current.children) > middle_index + 1:
                child = current.remove_child(middle_index + 1)
                right.insert_child(len(right.children), child)

        # 6. If it comes to root split, we create a new internal node and add current and right
        # to its children
        if parent is None:
            split_root = BTreeNode(self._min_degree, False)
            split_root.insert_key_value(middle_kv_pair.key, middle_kv_pair.value)
            split_root.insert_child(0, current)
            split_root.insert_child(1, right)
            self._root = split_root
            return
        
        # 7. If we are splitting internal node, we add right as one of its children
        parent.insert_key_value(middle_kv_pair.key, middle_kv_pair.value)
        insertion_index = parent.find_key_index(middle_kv_pair.key) + 1
        parent.insert_child(insertion_index, right)

    def _delete_from_node(self, current: BTreeNode[K, V], key: K) -> V:
        key_index = current.find_key_index(key)
        if key_index >= 0:
            # Key found in the current node
            if current.is_leaf:
                # Simple leaf deletion
                result = current.remove_key_value_pair(key_index).value
                self._size -= 1
                return result
            else:
                # Internal node deletion - replace with successor
                original_value = current.get_value(key_index)

                # Find successor - leftmost key in right child
                successor_node = current.get_child(key_index + 1)
                while not successor_node.is_leaf:
                    if len(successor_node.children) == 0:
                        # Successor path is broken, try predecessor instead
                        break
                    successor_node = successor_node.get_child(0)

                # Check if successor node has keys
                if len(successor_node) > 0:
                    # Replace with successor
                    successor_key = successor_node.get_key(0)
                    successor_value = successor_node.get_value(0)
                    current.remove_key_value_pair(key_index)
                    current.insert_key_value(successor_key, successor_value)
                    # Delete successor from leaf
                    self._delete_from_node(current.get_child(key_index + 1), successor_key)
                    # Check for underflow in child after deletion
                    if key_index + 1 < len(current.children):
                        child = current.get_child(key_index + 1)
                        if len(child) < (self._min_degree - 1):
                            self._fix_underflow(current, key_index + 1)
                else:
                    # Try predecessor instead
                    predecessor_node = current.get_child(key_index)
                    while not predecessor_node.is_leaf:
                        if len(predecessor_node.children) == 0:
                            break
                        predecessor_node = predecessor_node.get_child(len(predecessor_node.children) - 1)

                    if len(predecessor_node) > 0:
                        # Replace with predecessor
                        pred_key = predecessor_node.get_key(len(predecessor_node) - 1)
                        pred_value = predecessor_node.get_value(len(predecessor_node) - 1)
                        current.remove_key_value_pair(key_index)
                        current.insert_key_value(pred_key, pred_value)
                        # Delete predecessor
                        self._delete_from_node(current.get_child(key_index), pred_key)
                        # Check for underflow
                        if key_index < len(current.children):
                            child = current.get_child(key_index)
                            if len(child) < (self._min_degree - 1):
                                self._fix_underflow(current, key_index)
                    else:
                        # Both successor and predecessor are empty, just remove the key
                        current.remove_key_value_pair(key_index)
                        self._size -= 1

                return original_value
        
        elif not current.is_leaf:
            # Key not found - descend to appropriate child
            child_index = current.get_child_index(key)
            result = self._delete_from_node(current.get_child(child_index), key)
            # Check for underflow in child after deletion
            if child_index < len(current.children) and len(current.get_child(child_index)) < (self._min_degree - 1):
                self._fix_underflow(current, child_index)
            
            return result
        
        return None
    

    def _fix_underflow(self, parent: BTreeNode, child_index: int):
        # Bounds checking
        if child_index >= len(parent.children) or len(parent) == 0:
            return

        child = parent.get_child(child_index)
        # Defensive check - child should be underflowing
        if len(child) >= (self._min_degree - 1):
            return

        # Try to borrow from left sibling first
        if child_index > 0:
            left_sibling = parent.get_child(child_index - 1)
            if len(left_sibling) > (self._min_degree - 1):
                self._borrow_from_left_sibling(child, parent, child_index)
                return

        # Try to borrow from right sibling
        if child_index < (len(parent.children) - 1):
            right_sibling = parent.get_child(child_index + 1)
            if len(right_sibling) > (self._min_degree - 1):
                self._borrow_from_right_sibling(child, parent, child_index)
                return

        # Cannot borrow - must merge with a sibling
        if child_index > 0 and len(parent) > child_index - 1:
            # Merge with left sibling
            self._merge_with_left_sibling(child, parent, child_index)
        elif child_index < (len(parent.children) - 1) and len(parent) > child_index:
            self._merge_with_right_sibling(child, parent, child_index)


    def _borrow_from_left_sibling(self, node: BTreeNode[K, V], parent: BTreeNode[K, V], node_index: int):
        # 1. Get the left sibling
        left_sibling = parent.get_child(node_index - 1)
        separator_index = node_index - 1
        # Remove the separator from the parent
        separator = parent.remove_key_value_pair(separator_index)
        # 3. Get largest key from the left sibling
        borrowed_key = left_sibling.remove_key_value_pair(len(left_sibling) - 1)
        # 4. Move borrowed key to the parent
        parent.insert_key_value(borrowed_key.key, borrowed_key.value)
        # 5. Move separator to the current node at the beginning
        node.insert_key_value(separator.key, separator.value)
        # 6. Handle children for internal nodes
        if not node.is_leaf:
            # Move right most child from the left sibling to current node
            removed_child = left_sibling.remove_child(len(left_sibling.children) - 1)
            node.insert_child(0, removed_child)


    def _borrow_from_right_sibling(self, node: BTreeNode[K, V], parent: BTreeNode[K, V], node_index: int):
        # 1. Get the right sibling
        right_sibling = parent.get_child(node_index + 1)
        # Remove the separator from the parent
        separator = parent.remove_key_value_pair(node_index)
        # 3. Get largest key from the left sibling
        borrowed_key = right_sibling.remove_key_value_pair(0)
        # 4. Move borrowed key to the parent
        parent.insert_key_value(borrowed_key.key, borrowed_key.value)
        # 5. Move separator to the current node at the beginning
        node.insert_key_value(separator.key, separator.value)
        # 6. Handle children for internal nodes
        if not node.is_leaf:
            # Move left most child from the right sibling to current node
            removed_child = right_sibling.remove_child(0)
            node.insert_child(len(node.children), removed_child)

    
    def _merge_with_left_sibling(self, node: BTreeNode[K, V], parent: BTreeNode[K, V], node_index: int):
        # Bounds check
        if node_index <= 0 or node_index - 1 >= len(parent):
            return

        left_sibling = parent.get_child(node_index - 1)
        # Attempt fallback to borrowing if merge is unsafe
        if self._cannot_safely_merge(left_sibling, node) and len(left_sibling) > (self._min_degree - 1):
            self._borrow_from_left_sibling(node, parent, node_index)
            return

        # Safe to merge - check if separator exists
        if node_index - 1 < len(parent):
            separator = parent.remove_key_value_pair(node_index - 1)
            left_sibling.insert_key_value(separator.key, separator.value)

        # Move all nodes from current node to left sibling
        while len(node) > 0:
            removed_key = node.remove_key_value_pair(0)
            left_sibling.insert_key_value(removed_key.key, removed_key.value)

        # Move all children from current node to left sibling
        if not node.is_leaf:
            while len(node.children) > 0:
                left_sibling.insert_child(len(left_sibling.children), node.remove_child(0))

        # Remove current node from parent
        if node_index < len(parent.children):
            parent.remove_child(node_index)

    
    def _merge_with_right_sibling(self, node: BTreeNode[K, V], parent: BTreeNode[K, V], node_index: int):
        # Bounds check
        if node_index >= len(parent.children) - 1 or node_index >= len(parent):
            return

        right_sibling = parent.get_child(node_index + 1)
        # Attempt fallback to borrowing if merge is unsafe
        if self._cannot_safely_merge(node, right_sibling) and len(right_sibling) > (self._min_degree - 1):
            self._borrow_from_right_sibling(node, parent, node_index)
            return

        # Safe to merge - check if separator exists
        if node_index < len(parent):
            separator = parent.remove_key_value_pair(node_index)
            node.insert_key_value(separator.key, separator.value)

        # Move all keys from right sibling to current node
        while len(right_sibling) > 0:
            removed_key = right_sibling.remove_key_value_pair(0)
            node.insert_key_value(removed_key.key, removed_key.value)

        # Move all children from right sibling to current node
        if not node.is_leaf:
            while len(right_sibling.children) > 0:
                node.insert_child(len(node.children), right_sibling.remove_child(0))

        # Remove right sibling from parent
        if node_index + 1 < len(parent.children):
            parent.remove_child(node_index + 1)

    
    def _cannot_safely_merge(self, node1: BTreeNode[K, V], node2: BTreeNode[K, V]) -> bool:
        total_keys = len(node1) + 1 + len(node2)
        return total_keys > (2 * self._min_degree - 1)
    
    @property
    def min_degree(self) -> int:
        return self._min_degree

    @property
    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def __contains__(self, key: K) -> bool:
        return self.search(key) is not None

    def is_empty(self) -> bool:
        return self._size == 0

    def __setattr__(self, name, value):
        if name == "_min_degree":
            raise AttributeError("min_degree is immutable and cannot be modified")
        return super().__setattr__(name, value)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"BTreeIndex(min_degree={self._min_degree}, size={self._size})"
