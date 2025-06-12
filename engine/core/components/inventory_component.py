from engine.core.component import Component
from typing import List, Any, Dict

class InventoryComponent(Component):
    def __init__(self, capacity: int = -1): # -1 for unlimited capacity
        super().__init__()
        self._items: List[Any] = []
        self._capacity = capacity

    @property
    def capacity(self) -> int:
        return self._capacity

    @capacity.setter
    def capacity(self, value: int):
        if value < -1:
            raise ValueError("Capacity must be -1 (unlimited) or a positive integer.")
        self._capacity = value
        # If capacity is reduced, remove excess items
        if self._capacity != -1 and len(self._items) > self._capacity:
            self._items = self._items[:self._capacity]

    def add_item(self, item: Any) -> bool:
        if self._capacity != -1 and len(self._items) >= self._capacity:
            print(f"Inventory is full. Cannot add {item}.")
            return False
        self._items.append(item)
        print(f"Added {item} to inventory.")
        return True

    def remove_item(self, item: Any) -> bool:
        if item in self._items:
            self._items.remove(item)
            print(f"Removed {item} from inventory.")
            return True
        print(f"{item} not found in inventory.")
        return False

    def has_item(self, item: Any) -> bool:
        return item in self._items

    def get_items(self) -> List[Any]:
        return list(self._items) # Return a copy to prevent external modification

    def get_item_count(self) -> int:
        return len(self._items)

    def is_full(self) -> bool:
        return self._capacity != -1 and len(self._items) >= self._capacity

    def is_empty(self) -> bool:
        return len(self._items) == 0


