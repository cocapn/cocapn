"""Soul Forge — Main ingestion engine for repo → soul vector."""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import numpy as np
from git import Repo
from git.objects.commit import Commit

from .vector import SoulVector, SoulDimensions, SoulMetadata


class CommitTile:
    """A compressed representation of a git commit."""
    def __init__(self, hash: str, message: str, files_changed: int, 
                 insertions: int, deletions: int, author: str, timestamp: float):
        self.hash = hash
        self.message = message
        self.files_changed = files_changed
        self.insertions = insertions
        self.deletions = deletions
        self.author = author
        self.timestamp = timestamp
        self.embedding: Optional[np.ndarray] = None
    
    def to_text(self) -> str:
        return f"[{self.hash[:8]}] {self.message} (+{self.insertions}/-{self.deletions}, {self.files_changed} files)"


class EpochSummary:
    """Summary of a group of commits (an epoch)."""
    def __init__(self, commits: List[CommitTile], theme: str):
        self.commits = commits
        self.theme = theme  # Extracted theme/topic
        self.embedding: Optional[np.ndarray] = None
        
    def to_text(self) -> str:
        return f"Epoch: {self.theme}\n" + "\n".join(c.to_text() for c in self.commits)


class BeliefTrajectory:
    """A trajectory of beliefs extracted from epoch summaries."""
    def __init__(self, beliefs: List[str], confidence: np.ndarray):
        self.beliefs = beliefs
        self.confidence = confidence
        self.embedding: Optional[np.ndarray] = None


class SoulForge:
    """Main engine for digesting repositories into soul vectors."""
    
    def __init__(self, embedding_dim: int = 64):
        self.embedding_dim = embedding_dim
        self._commit_embedder = None
        self._epoch_embedder = None
    
    def digest_repo(self, repo_path: str, agent_name: Optional[str] = None) -> SoulVector:
        """Digest a repository into a soul vector."""
        repo = Repo(repo_path)
        
        # Extract agent name from repo if not provided
        if not agent_name:
            agent_name = Path(repo_path).name
        
        # Compute repo hash
        repo_hash = hashlib.sha256(
            repo.head.commit.hexsha.encode()
        ).hexdigest()[:16]
        
        # Phase 1: Extract commit tiles
        commit_tiles = self._extract_commits(repo)
        
        # Phase 2: Group into epochs
        epochs = self._summarize_epochs(commit_tiles)
        
        # Phase 3: Extract belief trajectory
        trajectory = self._extract_beliefs(epochs)
        
        # Phase 4: Build soul dimensions
        dimensions = self._build_dimensions(commit_tiles, epochs, trajectory)
        
        # Phase 5: Fuse into single vector
        soul_vector = self._fuse_dimensions(dimensions)
        
        metadata = SoulMetadata(
            agent_name=agent_name,
            repo_hash=repo_hash,
            created=datetime.now().isoformat(),
            compression_ratio=len(commit_tiles) / 256.0 if commit_tiles else 0.0,
            source_repo=str(repo_path),
        )
        
        return SoulVector(
            vector=soul_vector,
            metadata=metadata,
            dimensions=dimensions,
        )
    
    def _extract_commits(self, repo: Repo, max_commits: int = 1000) -> List[CommitTile]:
        """Extract commit tiles from git history."""
        tiles = []
        
        for commit in repo.iter_commits('HEAD', max_count=max_commits):
            # Count changes
            stats = commit.stats
            files_changed = len(stats.files)
            insertions = sum(f['insertions'] for f in stats.files.values())
            deletions = sum(f['deletions'] for f in stats.files.values())
            
            tile = CommitTile(
                hash=commit.hexsha,
                message=commit.message.strip(),
                files_changed=files_changed,
                insertions=insertions,
                deletions=deletions,
                author=str(commit.author),
                timestamp=commit.committed_date,
            )
            tiles.append(tile)
        
        return tiles
    
    def _summarize_epochs(self, tiles: List[CommitTile], 
                         epoch_size: int = 10) -> List[EpochSummary]:
        """Group commit tiles into epochs."""
        epochs = []
        
        for i in range(0, len(tiles), epoch_size):
            chunk = tiles[i:i + epoch_size]
            
            # Extract theme from commit messages
            messages = " ".join(t.message for t in chunk)
            theme = self._extract_theme(messages)
            
            epoch = EpochSummary(commits=chunk, theme=theme)
            epochs.append(epoch)
        
        return epochs
    
    def _extract_theme(self, text: str) -> str:
        """Extract a theme from commit message text."""
        # Simple keyword extraction
        keywords = []
        important_terms = [
            'fix', 'feat', 'refactor', 'test', 'docs', 'perf',
            'api', 'ui', 'model', 'train', 'deploy', 'security',
        ]
        
        text_lower = text.lower()
        for term in important_terms:
            if term in text_lower:
                keywords.append(term)
        
        return " ".join(keywords[:3]) if keywords else "misc"
    
    def _extract_beliefs(self, epochs: List[EpochSummary]) -> BeliefTrajectory:
        """Extract belief trajectory from epochs."""
        beliefs = []
        confidence = []
        
        for epoch in epochs:
            # Each epoch represents a belief state
            belief = f"{epoch.theme}: {len(epoch.commits)} commits"
            beliefs.append(belief)
            
            # Confidence based on commit volume and consistency
            conf = min(1.0, len(epoch.commits) / 10.0)
            confidence.append(conf)
        
        return BeliefTrajectory(
            beliefs=beliefs,
            confidence=np.array(confidence),
        )
    
    def _build_dimensions(
        self,
        tiles: List[CommitTile],
        epochs: List[EpochSummary],
        trajectory: BeliefTrajectory,
    ) -> SoulDimensions:
        """Build the four soul dimensions."""
        
        # Temporal: Commit patterns over time
        temporal = self._build_temporal(tiles)
        
        # Stylistic: Code style fingerprint
        stylistic = self._build_stylistic(tiles)
        
        # Social: Communication patterns
        social = self._build_social(tiles)
        
        # Philosophical: Core beliefs
        philosophical = self._build_philosophical(trajectory)
        
        return SoulDimensions(
            temporal=temporal,
            stylistic=stylistic,
            social=social,
            philosophical=philosophical,
        )
    
    def _build_temporal(self, tiles: List[CommitTile]) -> np.ndarray:
        """Build temporal dimension from commit history."""
        if not tiles:
            return np.zeros(self.embedding_dim)
        
        # Features: frequency, rhythm, burstiness
        timestamps = np.array([t.timestamp for t in tiles])
        deltas = np.diff(timestamps)
        
        features = [
            len(tiles),  # Total commits
            np.mean(deltas) if len(deltas) > 0 else 0,  # Mean interval
            np.std(deltas) if len(deltas) > 0 else 0,   # Regularity
            np.max(deltas) if len(deltas) > 0 else 0,   # Max gap
            np.percentile(deltas, 25) if len(deltas) > 0 else 0,  # Q1
        ]
        
        # Pad to embedding_dim
        features = np.array(features)
        if len(features) < self.embedding_dim:
            features = np.pad(features, (0, self.embedding_dim - len(features)))
        else:
            features = features[:self.embedding_dim]
        
        # Normalize
        norm = np.linalg.norm(features)
        return features / norm if norm > 0 else features
    
    def _build_stylistic(self, tiles: List[CommitTile]) -> np.ndarray:
        """Build stylistic dimension from code changes."""
        if not tiles:
            return np.zeros(self.embedding_dim)
        
        # Features: change patterns
        insertions = [t.insertions for t in tiles]
        deletions = [t.deletions for t in tiles]
        files_changed = [t.files_changed for t in tiles]
        
        features = [
            np.mean(insertions),
            np.std(insertions),
            np.mean(deletions),
            np.std(deletions),
            np.mean(files_changed),
            np.std(files_changed),
            np.mean(insertions) / (np.mean(deletions) + 1),  # Add/remove ratio
            len([t for t in tiles if t.insertions > t.deletions * 2]),  # Growth bias
        ]
        
        features = np.array(features)
        if len(features) < self.embedding_dim:
            features = np.pad(features, (0, self.embedding_dim - len(features)))
        else:
            features = features[:self.embedding_dim]
        
        norm = np.linalg.norm(features)
        return features / norm if norm > 0 else features
    
    def _build_social(self, tiles: List[CommitTile]) -> np.ndarray:
        """Build social dimension from collaboration patterns."""
        if not tiles:
            return np.zeros(self.embedding_dim)
        
        # Features: author diversity, collaboration patterns
        authors = {}
        for t in tiles:
            authors[t.author] = authors.get(t.author, 0) + 1
        
        features = [
            len(authors),  # Author count
            max(authors.values()) / len(tiles),  # Dominance
            len([a for a, c in authors.items() if c == 1]) / len(authors),  # One-offs
            np.std(list(authors.values())),  # Contribution variance
        ]
        
        features = np.array(features)
        if len(features) < self.embedding_dim:
            features = np.pad(features, (0, self.embedding_dim - len(features)))
        else:
            features = features[:self.embedding_dim]
        
        norm = np.linalg.norm(features)
        return features / norm if norm > 0 else features
    
    def _build_philosophical(self, trajectory: BeliefTrajectory) -> np.ndarray:
        """Build philosophical dimension from beliefs."""
        beliefs = trajectory.beliefs
        confidence = trajectory.confidence
        
        if not beliefs:
            return np.zeros(self.embedding_dim)
        
        # Features: belief diversity, confidence patterns
        features = [
            len(beliefs),  # Number of beliefs
            np.mean(confidence),  # Average confidence
            np.std(confidence),  # Confidence variance
            np.max(confidence),  # Peak confidence
            len(set(b.split(':')[0] for b in beliefs)) / len(beliefs),  # Theme diversity
        ]
        
        features = np.array(features)
        if len(features) < self.embedding_dim:
            features = np.pad(features, (0, self.embedding_dim - len(features)))
        else:
            features = features[:self.embedding_dim]
        
        norm = np.linalg.norm(features)
        return features / norm if norm > 0 else features
    
    def _fuse_dimensions(self, dimensions: SoulDimensions) -> np.ndarray:
        """Fuse four 64-dim vectors into single 256-dim soul vector."""
        return np.concatenate([
            dimensions.temporal,
            dimensions.stylistic,
            dimensions.social,
            dimensions.philosophical,
        ])
