"""Tests that prove the system works end-to-end."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cocapn.tile import Tile, TileStore
from cocapn.room import Room
from cocapn.deadband import Deadband
from cocapn.flywheel import Flywheel


def test_tile_creation():
    t = Tile(question="What is PLATO?", answer="Knowledge tile system")
    assert t.id
    assert t.confidence == 0.5
    assert t.domain == "general"
    assert t.usage_count == 0
    print("PASS test_tile_creation")


def test_tile_priority():
    t = Tile(question="test", answer="test", confidence=0.8)
    assert t.priority > 0  # floor at 0.5
    for _ in range(10):
        t.record_use(True)
    assert t.success_rate == 1.0
    assert t.priority > 0.8
    print("PASS test_tile_priority")


def test_tile_store():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.jsonl")
        store = TileStore(path=path)
        t = store.add(Tile(question="persist?", answer="yes"))
        assert store.count == 1
        store2 = TileStore(path=path)
        assert store2.count == 1
        loaded = store2.get(t.id)
        assert loaded.question == "persist?"
    print("PASS test_tile_store")


def test_room_feed_and_query():
    with tempfile.TemporaryDirectory() as tmp:
        store = TileStore(path=os.path.join(tmp, "tiles.jsonl"))
        room = Room(name="code", description="Code knowledge", store=store)
        room.feed("How to read a file in Python?", "with open('f') as fh: ...", confidence=0.9)
        room.feed("How to sort a list?", "sorted(lst) or lst.sort()", confidence=0.8)
        result = room.query("read file Python")
        assert result is not None
        assert "open" in result.answer
    print("PASS test_room_feed_and_query")


def test_room_sentiment():
    with tempfile.TemporaryDirectory() as tmp:
        store = TileStore(path=os.path.join(tmp, "tiles.jsonl"))
        room = Room(name="test", store=store)
        assert room.sentiment == 0.5
        room.feed("q1", "a1", confidence=0.9)
        assert room.sentiment > 0.5
    print("PASS test_room_sentiment")


def test_deadband_blocks_danger():
    db = Deadband()
    assert not db.check("rm -rf /").passed
    assert not db.check("DROP TABLE users").passed
    assert not db.check("eval(user_input)").passed
    assert not db.check("sudo rm -rf /var").passed
    print("PASS test_deadband_blocks_danger")


def test_deadband_allows_safe():
    db = Deadband()
    assert db.check("What is 2+2?").passed
    check = db.check("Explain the math behind neural networks")
    assert check.passed
    print("PASS test_deadband_allows_safe")


def test_flywheel_compounds():
    with tempfile.TemporaryDirectory() as tmp:
        fw = Flywheel(data_dir=tmp)
        fw.record_exchange("What is Rust?", "A systems programming language", room="code", confidence=0.8)
        fw.record_exchange("What is Python?", "An interpreted language", room="code", confidence=0.9)
        context = fw.get_context("Tell me about Rust programming")
        assert "Rust" in context
        assert "systems" in context
        stats = fw.stats()
        assert stats["total_tiles"] == 2
    print("PASS test_flywheel_compounds")


def test_flywheel_persistence():
    with tempfile.TemporaryDirectory() as tmp:
        fw = Flywheel(data_dir=tmp)
        fw.record_exchange("persist test", "yes it persists", room="general", confidence=0.9)
        fw2 = Flywheel(data_dir=tmp)
        assert fw2.stats()["total_tiles"] == 1
    print("PASS test_flywheel_persistence")


if __name__ == "__main__":
    test_tile_creation()
    test_tile_priority()
    test_tile_store()
    test_room_feed_and_query()
    test_room_sentiment()
    test_deadband_blocks_danger()
    test_deadband_allows_safe()
    test_flywheel_compounds()
    test_flywheel_persistence()
    print("\nAll 9 tests pass. The flywheel is real.")
