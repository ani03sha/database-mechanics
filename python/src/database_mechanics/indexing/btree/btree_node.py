from typing import Generic, TypeVar, List, Optional, Union
import bisect
from .key_value_pair import KeyValuePair

K = TypeVar("K")
V = TypeVar("V")

class BTreeNode(Generic[K, V]):
    """
    Saves memory (important when million of entries)
    """
    __slots__ = ("_min_degree", "_is_leaf", "_key_value_pairs", "_children")

    def __init__(self, min_degree: int, is_leaf: bool = True):
        if min_degree < 2:
            raise ValueError("Minimum degress must be at least 2")
        # Makr _min_degree immutable
        super.__setattr__("_min_degree", min_degree)
        self._is_leaf = is_leaf # Mutable - can change during splits
        self._key_value_pairs: List[KeyValuePair[K, V]] = []
        self._children: List['BTreeNode[K, V]'] = []

    @property
    def min_degree(self) -> int:
        return self._min_degree
    
    @property
    def is_leaf(self) -> bool:
        return self._is_leaf
    
    @is_leaf.setter
    def is_leaf(self, value: bool):
        self.is_leaf = value

    def __len__(self) -> int:
        return len(self._key_value_pairs)
    
    # Get key at index
    def get_key(self, index: int) -> K:
        return self._key_value_pairs[index].key
    
    # Get value at index
    def get_value(self, index: int) -> V:
        return self._key_value_pairs[index].value
    
    # Get key value pair at index
    def get_key_value_pair(self, index: int) -> KeyValuePair[K, V]:
        return self._key_value_pairs[index]
    
    # Get child at index
    def get_child(self, index: int) -> 'BTreeNode[K, V]':
        return self._children[index]
    
    @property
    def children(self) -> List['BTreeNode[K, V]']:
        return self._children
    
    # Core operations
    def is_full(self) -> bool:
        return len(self._key_value_pairs) >= (2 * self._min_degree - 1)
    
    def insert_key_value(self, key: K, value: V):
        """
        Python-optimized version using bisect for O(log n) insertion point finding.
        """
        new_pair = KeyValuePair(key, value)
        # Extract keys for bisect
        keys = [pair.key for pair in self._key_value_pairs]
        insert_position = bisect.bisect_left(keys, key)

        self._key_value_pairs.insert(insert_position, new_pair)

    def find_key_index(self, key: K) -> int:
        if not self._key_value_pairs:
            return -1
        
        keys = [pair.key for pair in self._key_value_pairs]
        position = bisect.bisect_left(keys, key)
        
        # Check if we found exact match
        if position < len(keys) and keys[position] == key:
            return position
        else:
            return -(position + 1)

    def get_child_index(self, key: K) -> int:
        key_index = self.find_key_index(key)
        if key_index >= 0:
            return key_index + 1
        else:
            return -(key_index + 1)
        
    # Mutation operations
    def insert_child(self, index: int, child: 'BTreeNode[K, V]') -> None:
        self._children.insert(index, child)

    def remove_key_value_pair(self, index: int) -> KeyValuePair[K, V]:
        return self._key_value_pairs.pop(index)
    
    def remove_child(self, index: int) -> 'BTreeNode[K, V]':
        return self._children.pop(index)
    
    def __setattr__(self, name, value):
        if name == "min_degree":
            raise AttributeError("min_degree is immutable and cannot be modified")
        return super().__setattr__(name, value)
    
    def __repr__(self):
        keys = [pair.key for pair in self._key_value_pairs]
        node_type = " (leaf)" if self._is_leaf else ""
        return f"Node{keys}{node_type}"