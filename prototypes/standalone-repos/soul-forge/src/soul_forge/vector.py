"""Core soul vector data structure."""

import json
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional
import numpy as np


@dataclass
class SoulDimensions:
    """The four dimensions of a soul."""
    temporal: np.ndarray       # 64 dims: how agent learns over time
    stylistic: np.ndarray      # 64 dims: coding patterns
    social: np.ndarray         # 64 dims: communication style  
    philosophical: np.ndarray  # 64 dims: core beliefs


@dataclass  
class SoulMetadata:
    """Metadata about a soul vector."""
    agent_name: str
    repo_hash: str
    created: str
    digest_model: str = "soul-forge-v1"
    compression_ratio: float = 0.0
    source_repo: Optional[str] = None


class SoulVector:
    """A 256-dimensional soul vector that encodes an agent's persona."""
    
    def __init__(
        self,
        vector: np.ndarray,
        metadata: SoulMetadata,
        dimensions: SoulDimensions,
    ):
        if vector.shape != (256,):
            raise ValueError(f"Soul vector must be 256-dim, got {vector.shape}")
        
        self.vector = vector.astype(np.float32)
        self.metadata = metadata
        self.dimensions = dimensions
        self._lora_weights: Optional[np.ndarray] = None
    
    @property
    def activation_tokens(self) -> List[str]:
        """Generate activation tokens from agent name."""
        base = self.metadata.agent_name
        return [
            f"@{base}",
            f"@{base.split('-')[0]}",
            base[:2].upper(),
        ]
    
    def cosine_similarity(self, other: "SoulVector") -> float:
        """Compute similarity with another soul."""
        a = self.vector / np.linalg.norm(self.vector)
        b = other.vector / np.linalg.norm(other.vector)
        return float(np.dot(a, b))
    
    def save(self, path: str) -> None:
        """Save soul vector to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "soul_version": "1.0",
            "agent_name": self.metadata.agent_name,
            "repo_hash": self.metadata.repo_hash,
            "soul_vector": self.vector.tolist(),
            "dimensions": {
                "temporal": self.dimensions.temporal.tolist(),
                "stylistic": self.dimensions.stylistic.tolist(),
                "social": self.dimensions.social.tolist(),
                "philosophical": self.dimensions.philosophical.tolist(),
            },
            "activation_tokens": self.activation_tokens,
            "metadata": {
                "created": self.metadata.created,
                "digest_model": self.metadata.digest_model,
                "compression_ratio": self.metadata.compression_ratio,
                "source_repo": self.metadata.source_repo,
            }
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> "SoulVector":
        """Load soul vector from disk."""
        with open(path, "r") as f:
            data = json.load(f)
        
        dims = SoulDimensions(
            temporal=np.array(data["dimensions"]["temporal"]),
            stylistic=np.array(data["dimensions"]["stylistic"]),
            social=np.array(data["dimensions"]["social"]),
            philosophical=np.array(data["dimensions"]["philosophical"]),
        )
        
        meta = SoulMetadata(
            agent_name=data["agent_name"],
            repo_hash=data["repo_hash"],
            created=data["metadata"]["created"],
            digest_model=data["metadata"]["digest_model"],
            compression_ratio=data["metadata"]["compression_ratio"],
            source_repo=data["metadata"].get("source_repo"),
        )
        
        return cls(
            vector=np.array(data["soul_vector"]),
            metadata=meta,
            dimensions=dims,
        )
    
    def __repr__(self) -> str:
        return f"SoulVector(agent={self.metadata.agent_name}, dims=256)"
