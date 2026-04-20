from flywheel_engine.core import Flywheel, Room, Tile


def test_room_query():
    room = Room("test", "general")
    room.add_tile(Tile("What is AI?", "Artificial Intelligence"))
    room.add_tile(Tile("What is ML?", "Machine Learning"))
    results = room.query("What is AI?")
    assert len(results) == 1
    assert results[0].answer == "Artificial Intelligence"


def test_flywheel_stats():
    fw = Flywheel()
    fw.create_room("memory", "general")
    fw.rooms["memory"].add_tile(Tile("Q", "A"))
    stats = fw.get_stats()
    assert stats["rooms"] == 1
    assert stats["total_tiles"] == 1
