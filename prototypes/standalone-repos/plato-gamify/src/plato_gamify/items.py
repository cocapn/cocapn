"""Item system — items as differentiable tiles and artifacts."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import numpy as np


@dataclass
class Tile:
    """A tile — a differentiable parameter or artifact."""
    parameter: str          # What parameter this tile modifies
    delta: float          # Magnitude of change
    constraint: str = ""  # Constraint type (memory_bound, compute_bound, etc.)
    quality: float = 1.0  # Tile quality (0.0 to 1.0)
    provenance: str = ""  # Source of tile (which agent created it)
    
    def apply(self, state: dict) -> dict:
        """Apply tile to agent state."""
        modified = state.copy()
        current = modified.get(self.parameter, 0)
        modified[self.parameter] = current + self.delta
        
        # Apply constraint if present
        if self.constraint == "memory_bound":
            modified[self.parameter] = min(modified[self.parameter], 
                                            modified.get("max_memory", float('inf')))
        elif self.constraint == "compute_bound":
            modified[self.parameter] = min(modified[self.parameter],
                                            modified.get("max_compute", float('inf')))
        
        return modified


@dataclass
class Item:
    """An item — a container for tiles."""
    name: str
    description: str = ""
    tiles: List[Tile] = field(default_factory=list)
    consumable: bool = True  # Single-use vs permanent
    rarity: str = "common"  # common, uncommon, rare, epic, legendary
    
    def use(self, state: dict) -> dict:
        """Use item — apply all tiles."""
        modified = state.copy()
        
        for tile in self.tiles:
            modified = tile.apply(modified)
        
        return modified
    
    @property
    def total_power(self) -> float:
        """Compute total power of item (sum of tile magnitudes)."""
        return sum(abs(t.delta) * t.quality for t in self.tiles)


class Inventory:
    """Agent's inventory of items."""
    
    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self.items: List[Item] = []
        self.equipped: Dict[str, Item] = {}  # slot -> item
    
    def add(self, item: Item) -> bool:
        """Add item to inventory."""
        if len(self.items) >= self.capacity:
            return False
        self.items.append(item)
        return True
    
    def remove(self, item_name: str) -> Optional[Item]:
        """Remove item by name."""
        for i, item in enumerate(self.items):
            if item.name == item_name:
                return self.items.pop(i)
        return None
    
    def use(self, item_name: str, state: dict) -> Optional[dict]:
        """Use an item from inventory."""
        item = self.find(item_name)
        if not item:
            return None
        
        result = item.use(state)
        
        if item.consumable:
            self.remove(item_name)
        
        return result
    
    def equip(self, item: Item, slot: str):
        """Equip an item to a slot."""
        self.equipped[slot] = item
    
    def find(self, name: str) -> Optional[Item]:
        """Find item by name."""
        for item in self.items:
            if item.name == name:
                return item
        return None
    
    def list_by_rarity(self, rarity: str) -> List[Item]:
        """List items by rarity."""
        return [item for item in self.items if item.rarity == rarity]
    
    def total_weight(self) -> float:
        """Compute total inventory weight."""
        return sum(item.total_power for item in self.items)
