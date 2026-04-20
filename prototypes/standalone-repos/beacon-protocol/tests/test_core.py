"""Tests for Beacon Protocol."""
import pytest
from beacon_protocol.core import Beacon, BeaconProtocol, BeaconReceipt


class TestBeacon:
    def test_beacon_creation(self):
        b = Beacon(
            signal_type="alert",
            source="ccc",
            payload={"message": "Test alert"},
        )
        assert b.signal_type == "alert"
        assert b.source == "ccc"
        assert b.priority == 5
        assert b.ttl == 300
        
    def test_beacon_id(self):
        b = Beacon(
            signal_type="heartbeat",
            source="oracle1",
            payload={"status": "ok"},
        )
        assert len(b.id) == 16
        assert b.id == b.id  # Consistent
        
    def test_json_roundtrip(self):
        b = Beacon(
            signal_type="discovery",
            source="jc1",
            payload={"room": "workshop"},
            priority=3,
        )
        json_str = b.to_json()
        b2 = Beacon.from_json(json_str)
        
        assert b2.signal_type == "discovery"
        assert b2.source == "jc1"
        assert b2.payload == {"room": "workshop"}
        assert b2.priority == 3


class TestBeaconProtocol:
    def test_emit_and_query(self):
        bp = BeaconProtocol()
        beacon = Beacon(
            signal_type="alert",
            source="ccc",
            payload={"message": "Fleet health critical"},
            priority=1,
        )
        bid = bp.emit(beacon)
        
        results = bp.query(signal_type="alert")
        assert len(results) == 1
        assert results[0].source == "ccc"
        
    def test_subscribe_and_receive(self):
        bp = BeaconProtocol()
        received = []
        
        def handler(beacon):
            received.append(beacon.signal_type)
            
        bp.subscribe("test_sub", ["alerts"], handler)
        
        beacon = Beacon(
            signal_type="alert",
            source="oracle1",
            payload={"msg": "hi"},
            channel="alerts",
        )
        bp.emit(beacon)
        
        assert len(received) == 1
        assert received[0] == "alert"
        
    def test_acknowledge(self):
        bp = BeaconProtocol()
        beacon = Beacon(signal_type="status", source="fm", payload={})
        bid = bp.emit(beacon)
        
        bp.acknowledge(bid, "ccc", "processed", "Done")
        receipts = bp.get_receipts(bid)
        
        assert len(receipts) == 1
        assert receipts[0].recipient == "ccc"
        assert receipts[0].status == "processed"
        
    def test_heartbeat_convenience(self):
        bp = BeaconProtocol()
        bid = bp.heartbeat("jc1", {"gpu_temp": 65})
        
        results = bp.query(signal_type="heartbeat")
        assert len(results) == 1
        assert results[0].source == "jc1"
        assert results[0].ttl == 60
        
    def test_alert_convenience(self):
        bp = BeaconProtocol()
        bid = bp.alert("oracle1", "MUD server down", priority=1)
        
        results = bp.query(signal_type="alert")
        assert len(results) == 1
        assert results[0].payload["message"] == "MUD server down"
        assert results[0].priority == 1
        
    def test_cleanup_expired(self):
        bp = BeaconProtocol()
        
        # Old beacon
        old = Beacon(
            signal_type="heartbeat",
            source="a",
            payload={},
            ttl=0,  # Expires immediately
        )
        bp.emit(old)
        
        removed = bp.cleanup_expired()
        assert removed == 1
        assert len(bp.beacons) == 0
        
    def test_stats(self):
        bp = BeaconProtocol()
        bp.heartbeat("a", {})
        bp.heartbeat("b", {})
        bp.alert("c", "test")
        
        stats = bp.get_stats()
        assert stats["total_beacons"] == 3
        assert "heartbeat" in stats["signal_types"]
        assert "alert" in stats["signal_types"]
        
    def test_query_by_source(self):
        bp = BeaconProtocol()
        bp.emit(Beacon("status", "ccc", {}))
        bp.emit(Beacon("status", "oracle1", {}))
        bp.emit(Beacon("alert", "ccc", {}))
        
        ccc_beacons = bp.query(source="ccc")
        assert len(ccc_beacons) == 2
        
    def test_query_by_channel(self):
        bp = BeaconProtocol()
        bp.emit(Beacon("discovery", "a", {}, channel="exploration"))
        bp.emit(Beacon("alert", "b", {}, channel="alerts"))
        
        exploration = bp.query(channel="exploration")
        assert len(exploration) == 1
