"""Tests for fleet monitoring integration."""
import pytest
from fleet_homunculus.core import FleetMonitor, FleetSnapshot


class TestFleetMonitor:
    def test_initialization(self):
        fm = FleetMonitor()
        assert len(fm.observer.channels) == 3
        assert "tile-velocity" in fm.observer.channels
        assert "agent-health" in fm.observer.channels
        assert "sync-drift" in fm.observer.channels
        
    def test_check_health_nominal(self):
        fm = FleetMonitor()
        metrics = {
            "tile-velocity": 12.0,
            "agent-health": 0.95,
            "sync-drift": 0.1,
            "agent-count": 5,
        }
        snapshot = fm.check_health(metrics)
        
        assert snapshot.health_score > 0.7
        assert snapshot.agent_count == 5
        assert len(snapshot.alerts) == 0  # All within deadband
        
    def test_check_health_alert(self):
        fm = FleetMonitor()
        metrics = {
            "tile-velocity": 2.0,  # Way below 10.0 setpoint
            "agent-health": 0.95,
            "sync-drift": 0.1,
            "agent-count": 5,
        }
        snapshot = fm.check_health(metrics)
        
        assert len(snapshot.alerts) > 0  # Tile velocity should trigger
        
    def test_compute_health(self):
        fm = FleetMonitor()
        
        # Perfect health
        health = fm._compute_health({
            "tile-velocity": 20.0,
            "agent-health": 1.0,
            "sync-drift": 0.0,
        })
        assert health == 1.0
        
        # Zero health
        health = fm._compute_health({
            "tile-velocity": 0.0,
            "agent-health": 0.0,
            "sync-drift": 5.0,
        })
        assert health < 0.5
        
    def test_generate_status_report_empty(self):
        fm = FleetMonitor()
        report = fm.generate_status_report()
        assert "Fleet Status" in report
        
    def test_full_stats(self):
        fm = FleetMonitor()
        stats = fm.get_full_stats()
        
        assert "flywheel" in stats
        assert "observer" in stats
        assert "refiner" in stats
        

class TestFleetSnapshot:
    def test_snapshot_markdown(self):
        snapshot = FleetSnapshot(
            timestamp="2026-04-20T12:00:00+00:00",
            tile_velocity=15.0,
            agent_count=5,
            active_channels=["tv", "ah", "sd"],
            alerts=["Slow tile generation"],
            health_score=0.85,
        )
        md = snapshot.to_markdown()
        
        assert "Fleet Status" in md
        assert "0.85" in md
        assert "Slow tile generation" in md
        assert "15.0" in md or "15" in md
        
    def test_snapshot_nominal(self):
        snapshot = FleetSnapshot(
            timestamp="2026-04-20T12:00:00+00:00",
            tile_velocity=10.0,
            agent_count=4,
            active_channels=["a"],
            alerts=[],
            health_score=0.9,
        )
        md = snapshot.to_markdown()
        assert "All systems nominal" in md
