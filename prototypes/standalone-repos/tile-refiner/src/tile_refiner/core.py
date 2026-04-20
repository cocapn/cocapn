"""Transform raw tiles into structured artifacts with semantic clustering."""
from typing import Any, Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict, Counter
import hashlib
import math
import re


@dataclass
class Tile:
    """Raw input: a unit of fleet knowledge."""
    question: str
    answer: str
    confidence: float = 1.0
    agent: str = "unknown"
    room: str = "general"
    tags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Artifact:
    """Structured output from refined tiles."""
    title: str
    content: str
    source_tiles: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    confidence: float = 0.0
    agent_diversity: float = 0.0  # How many different agents contributed
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_markdown(self) -> str:
        """Format as fleet-standard markdown document."""
        lines = [
            f"# {self.title}",
            "",
            f"**Confidence:** {self.confidence:.2f} | **Diversity:** {self.agent_diversity:.2f} | **Sources:** {len(self.source_tiles)}",
            "",
            f"**Keywords:** {', '.join(self.keywords)}",
            "",
            "---",
            "",
            self.content,
            "",
            "---",
            "",
            f"*Generated: {self.created_at}*",
        ]
        return "\n".join(lines)


class SemanticClusterer:
    """Group related tiles by shared vocabulary overlap."""
    
    # Common stop words to exclude from similarity
    STOP_WORDS = {'question', 'answer', 'what', 'how', 'is', 'the', 'a', 'an', 'to', 'of', 'and', 'in', 'for', 'with', 'on', 'at', 'from', 'by', 'about', 'this', 'that', 'it', 'as', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'shall', 'use', 'using', 'used', 'when', 'where', 'why', 'who', 'which', 'whose', 'whom'}
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
        
    def _vectorize(self, text: str) -> Dict[str, int]:
        """Create term frequency vector with stop word filtering."""
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        filtered = [w for w in words if w not in self.STOP_WORDS]
        return Counter(filtered)
        
    def _similarity(self, a: Dict[str, int], b: Dict[str, int]) -> float:
        """Jaccard-like similarity for term overlap."""
        if not a or not b:
            return 0.0
        a_set = set(a.keys())
        b_set = set(b.keys())
        intersection = len(a_set & b_set)
        union = len(a_set | b_set)
        return intersection / union if union > 0 else 0.0
        
    def cluster(self, tiles: List[Tile]) -> List[List[Tile]]:
        """Group tiles into semantic clusters."""
        if not tiles:
            return []
            
        # Compute all pairwise similarities
        vectors = [self._vectorize(f"{t.question} {t.answer}") for t in tiles]
        n = len(tiles)
        
        # Union-find for clustering
        parent = list(range(n))
        
        def find(x: int) -> int:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
            
        def union(x: int, y: int) -> None:
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
                
        # Merge similar tiles
        for i in range(n):
            for j in range(i + 1, n):
                sim = self._similarity(vectors[i], vectors[j])
                if sim >= self.threshold:
                    union(i, j)
                    
        # Build clusters
        clusters = defaultdict(list)
        for i in range(n):
            clusters[find(i)].append(tiles[i])
            
        return list(clusters.values())


class DedupEngine:
    """Remove near-duplicate tiles using semantic fingerprints."""
    
    def __init__(self):
        self._seen: Set[str] = set()
        
    def fingerprint(self, text: str) -> str:
        """Create semantic fingerprint."""
        # Normalize: lowercase, remove extra whitespace, sort words
        words = sorted(set(re.findall(r'\b[a-z]{4,}\b', text.lower())))
        normalized = ' '.join(words)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
        
    def is_duplicate(self, text: str) -> bool:
        fp = self.fingerprint(text)
        if fp in self._seen:
            return True
        self._seen.add(fp)
        return False


class TileRefiner:
    """Refine raw tiles into structured fleet artifacts."""
    
    def __init__(self, cluster_threshold: float = 0.3):
        self.dedup = DedupEngine()
        self.clusterer = SemanticClusterer(threshold=cluster_threshold)
        self.artifacts: List[Artifact] = []
        
    def extract_keywords(self, tiles: List[Tile]) -> List[str]:
        """Extract salient keywords from a tile collection."""
        all_text = ' '.join(f"{t.question} {t.answer} {' '.join(t.tags)}" for t in tiles)
        words = re.findall(r'\b[a-z]{4,}\b', all_text.lower())
        
        # TF-IDF-like scoring: common in this group, rare globally
        # Simplified: just frequency with length bonus
        counts = Counter(words)
        
        # Score: frequency × length_bonus
        scored = []
        for word, count in counts.most_common(50):
            length_bonus = min(len(word) / 8, 1.5)  # longer words often more specific
            scored.append((word, count * length_bonus))
            
        scored.sort(key=lambda x: x[1], reverse=True)
        return [w for w, _ in scored[:10]]
        
    def compute_diversity(self, tiles: List[Tile]) -> float:
        """Measure how many different agents contributed."""
        agents = set(t.agent for t in tiles)
        rooms = set(t.room for t in tiles)
        # Diversity = unique agents × unique rooms / total tiles
        return min(len(agents) * len(rooms) / max(len(tiles), 1), 1.0)
        
    def refine_cluster(self, tiles: List[Tile], title: str) -> Artifact:
        """Refine a single cluster into an artifact."""
        # Deduplicate
        unique_tiles = []
        for tile in tiles:
            text = f"{tile.question} {tile.answer}"
            if not self.dedup.is_duplicate(text):
                unique_tiles.append(tile)
                
        if not unique_tiles:
            return Artifact(title=title, content="No unique tiles in cluster.")
            
        # Merge content with attribution
        sections = []
        for tile in unique_tiles:
            sections.append(
                f"### {tile.agent} ({tile.room})\n"
                f"**Q:** {tile.question}\n"
                f"**A:** {tile.answer}\n"
                f"*confidence: {tile.confidence:.2f}*"
            )
        content = "\n\n".join(sections)
        
        # Metadata
        keywords = self.extract_keywords(unique_tiles)
        diversity = self.compute_diversity(unique_tiles)
        avg_confidence = sum(t.confidence for t in unique_tiles) / len(unique_tiles)
        
        artifact = Artifact(
            title=title,
            content=content,
            source_tiles=[t.question for t in unique_tiles],
            keywords=keywords,
            confidence=avg_confidence,
            agent_diversity=diversity,
        )
        self.artifacts.append(artifact)
        return artifact
        
    def refine_all(self, tiles: List[Tile]) -> List[Artifact]:
        """Cluster and refine all tiles into artifacts."""
        clusters = self.clusterer.cluster(tiles)
        
        artifacts = []
        for i, cluster in enumerate(clusters):
            # Generate title from cluster keywords
            keywords = self.extract_keywords(cluster)
            title = f"Artifact {i+1}: {', '.join(keywords[:3])}"
            
            artifact = self.refine_cluster(cluster, title)
            artifacts.append(artifact)
            
        return artifacts
        
    def get_stats(self) -> Dict[str, Any]:
        """Refiner statistics."""
        return {
            "artifacts_created": len(self.artifacts),
            "avg_confidence": sum(a.confidence for a in self.artifacts) / max(len(self.artifacts), 1),
            "avg_diversity": sum(a.agent_diversity for a in self.artifacts) / max(len(self.artifacts), 1),
            "total_sources": sum(len(a.source_tiles) for a in self.artifacts),
        }
