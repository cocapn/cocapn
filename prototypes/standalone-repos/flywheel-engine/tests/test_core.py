"""Tests for the semantic flywheel engine."""
import pytest
from flywheel_engine.core import Flywheel, Room, Tile, SimpleEmbedder


class TestSimpleEmbedder:
    def test_basic_embedding(self):
        emb = SimpleEmbedder()
        vec = emb.embed("hello world")
        assert len(vec) == 64
        assert all(isinstance(x, float) for x in vec)
        
    def test_similarity_same_text(self):
        emb = SimpleEmbedder()
        a = emb.embed("neural kernel")
        b = emb.embed("neural kernel")
        sim = emb.similarity(a, b)
        assert sim > 0.99  # essentially 1.0
        
    def test_similarity_different_text(self):
        emb = SimpleEmbedder()
        a = emb.embed("neural kernel")
        b = emb.embed("bottle protocol")
        sim = emb.similarity(a, b)
        assert 0.0 <= sim < 0.9
        
    def test_similarity_related_text(self):
        emb = SimpleEmbedder()
        a = emb.embed("agent training")
        b = emb.embed("model training for agents")
        sim = emb.similarity(a, b)
        assert sim > 0.3  # should have some overlap


class TestRoom:
    def test_add_and_query_tile(self):
        room = Room("harbor", "training")
        tile = Tile(
            question="How do agents dock?",
            answer="Through the harbor interface",
            confidence=0.9,
            agent="ccc",
            tags=["harbor", "docking"]
        )
        room.add_tile(tile)
        
        results = room.query("how do vessels dock?")
        assert len(results) > 0
        assert results[0].question == "How do agents dock?"
        
    def test_query_confidence_weighting(self):
        room = Room("test", "test")
        room.add_tile(Tile("q1", "a1", confidence=0.3, agent="a"))
        room.add_tile(Tile("q1", "a2", confidence=0.9, agent="b"))
        
        results = room.query("q1")
        # Higher confidence should rank higher
        assert results[0].answer == "a2"
        
    def test_empty_query(self):
        room = Room("empty", "test")
        results = room.query("nothing")
        assert results == []


class TestFlywheel:
    def test_create_room(self):
        fw = Flywheel()
        room = fw.create_room("harbor", "training")
        assert room.name == "harbor"
        assert "harbor" in fw.rooms
        
    def test_add_tile(self):
        fw = Flywheel()
        fw.add_tile("harbor", Tile(
            question="Test",
            answer="Answer",
            agent="ccc"
        ))
        assert len(fw.rooms["harbor"].tiles) == 1
        assert fw.agent_stats["ccc"]["tiles_created"] == 1
        
    def test_inject(self):
        fw = Flywheel()
        fw.add_tile("harbor", Tile(
            question="How do I dock?",
            answer="Use the harbor interface",
            agent="oracle1"
        ))
        
        results = fw.inject("ccc", "harbor", "how do I dock?")
        assert len(results) > 0
        assert len(fw.injection_log) == 1
        assert fw.injection_log[0].tiles_injected > 0
        
    def test_stats(self):
        fw = Flywheel()
        fw.add_tile("harbor", Tile("q1", "a1", agent="a"))
        fw.add_tile("bridge", Tile("q2", "a2", agent="a"))
        fw.add_tile("harbor", Tile("q3", "a3", agent="b"))
        
        stats = fw.get_stats()
        assert stats["rooms"] == 2
        assert stats["total_tiles"] == 3
        assert stats["total_agents"] == 2
        
    def test_export_tiles(self):
        fw = Flywheel()
        fw.add_tile("harbor", Tile("q1", "a1", agent="ccc"))
        fw.add_tile("bridge", Tile("q2", "a2", agent="ccc"))
        
        all_tiles = fw.export_tiles()
        assert len(all_tiles) == 2
        
        harbor_only = fw.export_tiles("harbor")
        assert len(harbor_only) == 1
