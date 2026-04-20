"""Context injection engine for compounding agent intelligence."""
import re
import math
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict


@dataclass
class Tile:
    """A unit of fleet knowledge."""
    question: str
    answer: str
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    agent: str = "unknown"
    room: str = "general"
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "agent": self.agent,
            "room": self.room,
            "tags": self.tags,
        }


class SimpleEmbedder:
    """Lightweight embedding using term frequency."""
    
    def __init__(self, dim: int = 64):
        self.dim = dim
        self.vocab: Dict[str, int] = {}
        self.next_id = 0
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split()
        
    def _get_or_assign(self, token: str) -> int:
        """Get vocab ID or assign new one."""
        if token not in self.vocab:
            self.vocab[token] = self.next_id
            self.next_id += 1
        return self.vocab[token]
        
    def embed(self, text: str) -> List[float]:
        """Create sparse embedding from text."""
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.dim
            
        # Term frequency
        counts = defaultdict(int)
        for t in tokens:
            counts[t] += 1
            
        # Build embedding vector
        vec = [0.0] * self.dim
        for token, count in counts.items():
            idx = self._get_or_assign(token) % self.dim
            vec[idx] += count
            
        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
            
        return vec
        
    def similarity(self, a: List[float], b: List[float]) -> float:
        """Cosine similarity."""
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        return max(0.0, dot)  # already normalized, but clamp


@dataclass
class Room:
    """A collection of related tiles with semantic retrieval."""
    name: str
    domain: str
    tiles: List[Tile] = field(default_factory=list)
    embedder: SimpleEmbedder = field(default_factory=lambda: SimpleEmbedder())
    
    def add_tile(self, tile: Tile) -> None:
        """Add a tile and compute its embedding."""
        text = f"{tile.question} {tile.answer} {' '.join(tile.tags)}"
        tile.embedding = self.embedder.embed(text)
        self.tiles.append(tile)
        
    def query(self, question: str, top_k: int = 3) -> List[Tile]:
        """Semantic search for tiles matching the question."""
        if not self.tiles:
            return []
            
        query_emb = self.embedder.embed(question)
        
        # Score all tiles
        scored = []
        for tile in self.tiles:
            if tile.embedding:
                sim = self.embedder.similarity(query_emb, tile.embedding)
            else:
                # Fallback to keyword matching
                sim = self._keyword_score(question, tile)
            
            # Weight by confidence and recency
            score = sim * tile.confidence
            scored.append((score, tile))
            
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:top_k]]
        
    def _keyword_score(self, query: str, tile: Tile) -> float:
        """Fallback keyword matching."""
        q_words = set(query.lower().split())
        text = f"{tile.question} {tile.answer} {' '.join(tile.tags)}".lower()
        matches = sum(1 for w in q_words if w in text)
        return matches / max(len(q_words), 1)
        
    def get_stats(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "domain": self.domain,
            "tile_count": len(self.tiles),
            "avg_confidence": sum(t.confidence for t in self.tiles) / max(len(self.tiles), 1),
            "agents": list(set(t.agent for t in self.tiles)),
        }


@dataclass
class InjectionPoint:
    """Where context gets injected."""
    agent_name: str
    room_name: str
    query: str
    tiles_injected: int
    timestamp: str


class Flywheel:
    """The compounding engine with semantic retrieval."""
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.injection_log: List[InjectionPoint] = []
        self.agent_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "tiles_created": 0,
            "rooms_visited": set(),
            "queries_made": 0,
        })
        
    def create_room(self, name: str, domain: str) -> Room:
        """Create a new knowledge room."""
        room = Room(name, domain)
        self.rooms[name] = room
        return room
        
    def add_tile(self, room_name: str, tile: Tile) -> None:
        """Add a tile to a room."""
        if room_name not in self.rooms:
            self.create_room(room_name, "general")
        self.rooms[room_name].add_tile(tile)
        self.agent_stats[tile.agent]["tiles_created"] += 1
        self.agent_stats[tile.agent]["rooms_visited"].add(room_name)
        
    def inject(self, agent_name: str, room_name: str, query: str, top_k: int = 3) -> List[Tile]:
        """Retrieve relevant tiles for an agent query."""
        room = self.rooms.get(room_name)
        if not room:
            return []
            
        tiles = room.query(query, top_k)
        self.injection_log.append(InjectionPoint(
            agent_name=agent_name,
            room_name=room_name,
            query=query,
            tiles_injected=len(tiles),
            timestamp=datetime.now(timezone.utc).isoformat(),
        ))
        self.agent_stats[agent_name]["queries_made"] += 1
        return tiles
        
    def get_stats(self) -> Dict[str, Any]:
        """Fleet-wide statistics."""
        total_tiles = sum(len(r.tiles) for r in self.rooms.values())
        total_agents = len(self.agent_stats)
        
        return {
            "rooms": len(self.rooms),
            "total_tiles": total_tiles,
            "total_agents": total_agents,
            "injections": len(self.injection_log),
            "room_breakdown": {name: room.get_stats() for name, room in self.rooms.items()},
            "agent_breakdown": {
                agent: {
                    "tiles_created": stats["tiles_created"],
                    "rooms_visited": len(stats["rooms_visited"]),
                    "queries_made": stats["queries_made"],
                }
                for agent, stats in self.agent_stats.items()
            },
        }
        
    def export_tiles(self, room_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Export tiles for persistence."""
        tiles = []
        rooms = [self.rooms[room_name]] if room_name else self.rooms.values()
        for room in rooms:
            for tile in room.tiles:
                tiles.append(tile.to_dict())
        return tiles
