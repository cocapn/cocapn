"""Soul compression — progressive summarization."""

from typing import List
import numpy as np

from .soul_forge import CommitTile, EpochSummary, BeliefTrajectory


class SoulCompressor:
    """Progressively compresses repo data into soul vectors."""
    
    def __init__(self, target_dim: int = 256):
        self.target_dim = target_dim
    
    def compress_commits(self, commits: List[CommitTile], 
                        ratio: float = 10.0) -> List[CommitTile]:
        """Compress commits by deduplication and summarization."""
        # Remove duplicate messages
        seen = set()
        unique = []
        for c in commits:
            key = c.message[:50]  # First 50 chars as fingerprint
            if key not in seen:
                seen.add(key)
                unique.append(c)
        
        # If still too many, keep most significant
        target = max(1, int(len(commits) / ratio))
        if len(unique) > target:
            # Sort by significance (files changed + insertions)
            unique.sort(key=lambda c: c.files_changed + c.insertions, 
                       reverse=True)
            unique = unique[:target]
        
        return unique
    
    def compress_epochs(self, epochs: List[EpochSummary],
                       ratio: float = 10.0) -> List[EpochSummary]:
        """Compress epochs by theme deduplication."""
        # Group epochs by theme
        themes = {}
        for e in epochs:
            theme_key = e.theme.split()[0] if e.theme else "misc"
            if theme_key not in themes:
                themes[theme_key] = []
            themes[theme_key].append(e)
        
        # Keep representative epoch per theme
        compressed = []
        for theme, eps in themes.items():
            # Merge epochs with same theme
            merged = EpochSummary(
                commits=[c for e in eps for c in e.commits],
                theme=theme,
            )
            compressed.append(merged)
        
        # If still too many, keep most diverse
        target = max(1, int(len(epochs) / ratio))
        if len(compressed) > target:
            compressed.sort(key=lambda e: len(e.commits), reverse=True)
            compressed = compressed[:target]
        
        return compressed
    
    def compress_beliefs(self, trajectory: BeliefTrajectory) -> BeliefTrajectory:
        """Compress belief trajectory to core tenets."""
        beliefs = trajectory.beliefs
        confidence = trajectory.confidence
        
        if len(beliefs) <= 10:
            return trajectory
        
        # Keep beliefs with highest confidence
        indices = np.argsort(confidence)[-10:]
        
        return BeliefTrajectory(
            beliefs=[beliefs[i] for i in indices],
            confidence=confidence[indices],
        )
