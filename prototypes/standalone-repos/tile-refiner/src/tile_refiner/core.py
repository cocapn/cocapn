"""Transform raw tiles into structured artifacts."""
from typing import Any, Dict, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import re


@dataclass
class Artifact:
    """A structured output from refined tiles."""
    title: str
    content: str
    source_tiles: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DedupEngine:
    """Remove duplicate tiles."""
    def __init__(self):
        self._seen: Set[str] = set()
        
    def fingerprint(self, text: str) -> str:
        # Simple fingerprinting - normalize and hash
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()[:12]
        
    def is_duplicate(self, text: str) -> bool:
        fp = self.fingerprint(text)
        if fp in self._seen:
            return True
        self._seen.add(fp)
        return False


class TileRefiner:
    """Refine raw tiles into structured artifacts."""
    def __init__(self):
        self.dedup = DedupEngine()
        self.artifacts: List[Artifact] = []
        
    def extract_keywords(self, text: str) -> List[str]:
        # Simple keyword extraction
        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
        # Return most common
        from collections import Counter
        return [w for w, _ in Counter(words).most_common(5)]
        
    def refine(self, tiles: List[Dict[str, str]], title: str) -> Artifact:
        unique_tiles = []
        for tile in tiles:
            text = f"{tile.get('question', '')} {tile.get('answer', '')}"
            if not self.dedup.is_duplicate(text):
                unique_tiles.append(tile)
        
        # Merge content
        content = "\n\n".join(
            f"Q: {t.get('question', '')}\nA: {t.get('answer', '')}"
            for t in unique_tiles
        )
        
        keywords = self.extract_keywords(content)
        
        artifact = Artifact(
            title=title,
            content=content,
            source_tiles=[t.get('question', '') for t in unique_tiles],
            keywords=keywords,
            confidence=len(unique_tiles) / max(len(tiles), 1),
        )
        self.artifacts.append(artifact)
        return artifact
