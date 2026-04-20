"""Agent runtime for fleet coordination."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Tile:
    """A unit of knowledge in the PLATO system."""
    question: str
    answer: str
    domain: str = "general"
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "domain": self.domain,
            "confidence": self.confidence,
            "tags": self.tags,
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tile":
        return cls(**data)


@dataclass  
class ValidationResult:
    """Result of a deadband validation check."""
    passed: bool
    level: str  # P0, P1, P2
    reason: str
    

class Agent:
    """Fleet agent with PLATO tile integration."""
    
    def __init__(self, name: str, domain: str = "general"):
        self.name = name
        self.domain = domain
        self.tiles: List[Tile] = []
        self._active = False
        
    def activate(self) -> None:
        """Activate the agent for fleet operations."""
        self._active = True
        
    def deactivate(self) -> None:
        """Deactivate the agent."""
        self._active = False
        
    def is_active(self) -> bool:
        return self._active
        
    def add_tile(self, tile: Tile) -> None:
        """Add a knowledge tile."""
        self.tiles.append(tile)
        
    def query(self, question: str) -> Optional[Tile]:
        """Find best matching tile."""
        for tile in self.tiles:
            if question.lower() in tile.question.lower():
                return tile
        return None
        
    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "domain": self.domain,
            "tiles": [t.to_dict() for t in self.tiles],
            "active": self._active,
        })
