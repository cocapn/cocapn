"""Context injection engine for compounding agent intelligence."""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Tile:
    question: str
    answer: str
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class Room:
    """A collection of related tiles."""
    name: str
    domain: str
    tiles: List[Tile] = field(default_factory=list)
    
    def add_tile(self, tile: Tile) -> None:
        self.tiles.append(tile)
        
    def query(self, question: str, top_k: int = 3) -> List[Tile]:
        matches = [t for t in self.tiles if any(w in t.question.lower() for w in question.lower().split())]
        return sorted(matches, key=lambda t: t.confidence, reverse=True)[:top_k]


@dataclass
class InjectionPoint:
    """Where context gets injected."""
    agent_name: str
    timestamp: str
    tiles_injected: int


class Flywheel:
    """The compounding engine."""
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.injection_log: List[InjectionPoint] = []
        
    def create_room(self, name: str, domain: str) -> Room:
        room = Room(name, domain)
        self.rooms[name] = room
        return room
        
    def inject(self, agent_name: str, room_name: str, query: str) -> List[Tile]:
        room = self.rooms.get(room_name)
        if not room:
            return []
        tiles = room.query(query)
        self.injection_log.append(InjectionPoint(
            agent_name=agent_name,
            timestamp=datetime.utcnow().isoformat(),
            tiles_injected=len(tiles)
        ))
        return tiles
        
    def get_stats(self) -> Dict[str, Any]:
        return {
            "rooms": len(self.rooms),
            "total_tiles": sum(len(r.tiles) for r in self.rooms.values()),
            "injections": len(self.injection_log),
        }
