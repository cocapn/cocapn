import pytest
from deadband_protocol.core import Deadband, Priority, SafetyGate


def test_p0_failure_stops_validation():
    db = Deadband()
    db.add_gate(SafetyGate("never", lambda x: False, Priority.P0, "Always fails"))
    db.add_gate(SafetyGate("always", lambda x: True, Priority.P2, "Always passes"))
    results = db.validate("test")
    assert len(results) == 1  # P2 gate never reached
    assert not results[0].passed


def test_priority_ordering():
    db = Deadband()
    db.add_gate(SafetyGate("p2", lambda x: True, Priority.P2, "P2"))
    db.add_gate(SafetyGate("p0", lambda x: True, Priority.P0, "P0"))
    db.add_gate(SafetyGate("p1", lambda x: True, Priority.P1, "P1"))
    assert db._gates[0].priority == Priority.P0
    assert db._gates[1].priority == Priority.P1
    assert db._gates[2].priority == Priority.P2
