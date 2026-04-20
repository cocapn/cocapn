"""Tests for semantic tile refiner."""
import pytest
from tile_refiner.core import TileRefiner, Tile, SemanticClusterer, DedupEngine


class TestDedupEngine:
    def test_fingerprint_consistency(self):
        d = DedupEngine()
        fp1 = d.fingerprint("The quick brown fox")
        fp2 = d.fingerprint("The quick brown fox")
        assert fp1 == fp2
        
    def test_duplicate_detection(self):
        d = DedupEngine()
        assert d.is_duplicate("First tile") is False
        assert d.is_duplicate("First tile") is True
        assert d.is_duplicate("Second tile") is False
        
    def test_semantic_duplicate(self):
        d = DedupEngine()
        # Same words, different order → same semantic fingerprint
        assert d.is_duplicate("agent training harbor") is False
        assert d.is_duplicate("harbor training agent") is True


class TestSemanticClusterer:
    def test_cluster_similar_tiles(self):
        c = SemanticClusterer(threshold=0.15)  # Lower threshold for test data
        tiles = [
            Tile("What is harbor?", "Agent training port", agent="a", room="harbor"),
            Tile("How to dock?", "Use harbor interface", agent="b", room="harbor"),
            Tile("What is forge?", "Model building room", agent="c", room="forge"),
        ]
        clusters = c.cluster(tiles)
        # Harbor tiles should cluster together, forge separate
        assert len(clusters) == 2
        
    def test_single_tile(self):
        c = SemanticClusterer()
        clusters = c.cluster([Tile("Q", "A")])
        assert len(clusters) == 1
        
    def test_empty_cluster(self):
        c = SemanticClusterer()
        assert c.cluster([]) == []


class TestTileRefiner:
    def test_refine_single_cluster(self):
        r = TileRefiner()
        tiles = [
            Tile("What is harbor?", "Agent training port", agent="ccc", room="harbor", confidence=0.9),
            Tile("How to dock?", "Use harbor interface", agent="kimi-7", room="harbor", confidence=0.8),
        ]
        artifact = r.refine_cluster(tiles, "Harbor Guide")
        
        assert artifact.title == "Harbor Guide"
        assert "ccc" in artifact.content
        assert "kimi-7" in artifact.content
        assert artifact.agent_diversity > 0
        assert len(artifact.keywords) > 0
        
    def test_refine_all(self):
        r = TileRefiner()
        tiles = [
            Tile("Harbor question?", "Harbor answer", agent="ccc", room="harbor"),
            Tile("Harbor question 2?", "Harbor answer 2", agent="kimi-7", room="harbor"),
            Tile("Forge question?", "Forge answer", agent="ccc", room="forge"),
            Tile("Bridge question?", "Bridge answer", agent="grok", room="bridge"),
        ]
        artifacts = r.refine_all(tiles)
        
        assert len(artifacts) >= 2  # Should cluster into at least 2 groups
        assert r.get_stats()["artifacts_created"] == len(artifacts)
        
    def test_deduplication(self):
        r = TileRefiner()
        tiles = [
            Tile("Same question?", "Same answer", agent="a", room="test"),
            Tile("Same question?", "Same answer", agent="b", room="test"),
        ]
        artifact = r.refine_cluster(tiles, "Test")
        # Second tile should be deduplicated
        assert len(artifact.source_tiles) == 1
        
    def test_keyword_extraction(self):
        r = TileRefiner()
        tiles = [
            Tile("Neural kernel?", "Model as OS", tags=["neural", "kernel"]),
            Tile("Flywheel?", "Compounding engine", tags=["flywheel", "engine"]),
        ]
        keywords = r.extract_keywords(tiles)
        assert "neural" in keywords or "kernel" in keywords or "flywheel" in keywords
        
    def test_diversity_score(self):
        r = TileRefiner()
        # 2 agents, 2 rooms, 2 tiles → diversity = 2*2/2 = 2.0, clamped to 1.0
        tiles = [
            Tile("Q1", "A1", agent="a", room="room1"),
            Tile("Q2", "A2", agent="b", room="room2"),
        ]
        div = r.compute_diversity(tiles)
        assert div == 1.0  # Clamped
        
    def test_markdown_output(self):
        r = TileRefiner()
        tiles = [Tile("Q?", "A.", agent="ccc", room="harbor")]
        artifact = r.refine_cluster(tiles, "Test")
        md = artifact.to_markdown()
        
        assert "# Test" in md
        assert "ccc" in md
        assert "harbor" in md
        assert "---" in md
