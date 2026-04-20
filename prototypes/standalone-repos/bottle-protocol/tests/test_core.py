from bottle_protocol.core import Bottle, FleetPostOffice
import tempfile


def test_bottle_to_markdown():
    b = Bottle("CCC", "Oracle1", "Test", "Hello fleet!")
    md = b.to_markdown()
    assert "[FLEET:BOTTLE]" in md
    assert "CCC" in md
    assert "Hello fleet!" in md


def test_post_office():
    with tempfile.TemporaryDirectory() as tmp:
        po = FleetPostOffice(tmp)
        b = Bottle("CCC", "FM", "Ship it", "Done")
        path = po.send(b)
        assert path.exists()
