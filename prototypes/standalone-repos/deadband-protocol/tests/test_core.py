"""Tests for adaptive deadband protocol."""
import pytest
from deadband_protocol.core import (
    AdaptiveDeadband,
    MultiChannelObserver,
    Signal,
)


class TestAdaptiveDeadband:
    def test_signal_inside_deadband(self):
        db = AdaptiveDeadband(setpoint=10.0, initial_width=2.0)
        # Signal at setpoint — definitely inside
        should_act, reason = db.evaluate(Signal(value=10.0, timestamp=0.0))
        assert should_act is False
        assert "inside deadband" in reason
        
    def test_signal_outside_deadband_high(self):
        db = AdaptiveDeadband(setpoint=10.0, initial_width=2.0)
        # Signal at 12.0 — upper bound is 11.0, so outside
        should_act, reason = db.evaluate(Signal(value=12.0, timestamp=0.0))
        assert should_act is True
        assert "exited deadband" in reason
        assert "high" in reason
        
    def test_signal_outside_deadband_low(self):
        db = AdaptiveDeadband(setpoint=10.0, initial_width=2.0)
        # Signal at 8.0 — lower bound is 9.0, so outside
        should_act, reason = db.evaluate(Signal(value=8.0, timestamp=0.0))
        assert should_act is True
        assert "exited deadband" in reason
        assert "low" in reason
        
    def test_adaptive_narrowing(self):
        db = AdaptiveDeadband(setpoint=0.0, initial_width=4.0, min_width=1.0)
        initial_width = db.state.deadband_width
        
        # Trigger action — should narrow
        db.evaluate(Signal(value=10.0, timestamp=0.0))
        assert db.state.deadband_width < initial_width
        
    def test_min_width_respected(self):
        db = AdaptiveDeadband(setpoint=0.0, initial_width=1.0, min_width=0.5, adaptation_rate=0.9)
        # Trigger action multiple times to force narrowing
        for i in range(10):
            db.evaluate(Signal(value=10.0, timestamp=float(i)))
        assert db.state.deadband_width >= 0.5
        
    def test_stats(self):
        db = AdaptiveDeadband(setpoint=5.0, initial_width=2.0)
        db.evaluate(Signal(value=10.0, timestamp=1.0))
        db.evaluate(Signal(value=5.0, timestamp=2.0))  # Inside deadband [4.0, 6.0]
        
        stats = db.get_stats()
        assert stats["setpoint"] == 5.0
        assert stats["actions_triggered"] == 1  # Only 10.0 exits deadband
        

class TestMultiChannelObserver:
    def test_register_and_observe(self):
        obs = MultiChannelObserver()
        obs.register_channel("agent-health", setpoint=0.8, initial_width=0.2)
        
        # Healthy signal — no alert
        alert = obs.observe("agent-health", Signal(value=0.81, timestamp=0.0))
        assert alert is None
        
        # Unhealthy signal — alert
        alert = obs.observe("agent-health", Signal(value=0.5, timestamp=1.0))
        assert alert is not None
        assert "ALERT" in alert
        
    def test_multiple_channels(self):
        obs = MultiChannelObserver()
        obs.register_channel("temperature", setpoint=25.0, initial_width=5.0)
        obs.register_channel("tile-velocity", setpoint=10.0, initial_width=4.0)
        
        obs.observe("temperature", Signal(value=20.0, timestamp=0.0))
        obs.observe("tile-velocity", Signal(value=15.0, timestamp=0.0))
        
        stats = obs.get_all_stats()
        assert "temperature" in stats
        assert "tile-velocity" in stats
        
    def test_summary(self):
        obs = MultiChannelObserver()
        obs.register_channel("sync-drift", setpoint=0.0, initial_width=1.0)
        obs.observe("sync-drift", Signal(value=2.0, timestamp=0.0))
        
        summary = obs.summary()
        assert "Observatory Status" in summary
        assert "sync-drift" in summary
        assert "Total alerts: 1" in summary
        
    def test_unregistered_channel_raises(self):
        obs = MultiChannelObserver()
        with pytest.raises(KeyError):
            obs.observe("unknown", Signal(value=0.0, timestamp=0.0))
