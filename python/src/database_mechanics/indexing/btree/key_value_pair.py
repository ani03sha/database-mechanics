from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class KeyValuePair(Generic[K, V]):
    """
    Saves memory (important when million of entries)
    """
    __slots__ = ("_key", "value")

    def __init__(self, key: K, value: V):
        if key is None:
            raise ValueError("Key cannot be null")
        super.__setattr__("_key", key) # bypass __setattr__ checks
        self.value = value # mutable

    @property
    def key(self) -> K:
        return self._key
    
    def __setattr__(self, name, value):
        if name == "_key":
            raise AttributeError("Key is immutable and cannot be modified")
        return super().__setattr__(name, value)
    
    def __eq__(self, other):
        if not isinstance(other, KeyValuePair):
            return False
        return self._key == other.key and self.value == other.value
    
    def __hash__(self):
        return hash((self._key, self.value))
    
    def __repr__(self):
        return f"({self.key} -> {self.value})"