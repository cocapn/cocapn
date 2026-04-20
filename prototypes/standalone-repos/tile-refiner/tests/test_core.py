from tile_refiner.core import TileRefiner, DedupEngine


def test_dedup():
    d = DedupEngine()
    assert not d.is_duplicate("Hello world")
    assert d.is_duplicate("Hello world")
    assert not d.is_duplicate("Different text")


def test_refine():
    r = TileRefiner()
    tiles = [
        {"question": "What is AI?", "answer": "Artificial Intelligence"},
        {"question": "What is AI?", "answer": "Artificial Intelligence"},  # dup
        {"question": "What is ML?", "answer": "Machine Learning"},
    ]
    art = r.refine(tiles, "AI Overview")
    assert art.confidence == 2 / 3  # 2 unique out of 3
    assert len(art.keywords) > 0
