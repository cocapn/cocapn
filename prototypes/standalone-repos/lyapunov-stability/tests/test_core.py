"""Tests for Lyapunov stability analyzer."""
import math
import pytest
from lyapunov_stability.core import (
    LyapunovAnalyzer,
    FleetStabilityMonitor,
    StateVector,
)


class TestLyapunovAnalyzer:
    def test_empty_history(self):
        la = LyapunovAnalyzer()
        assert la.estimate_exponent() is None
        assert la.classify_stability(None) == "unknown — insufficient data"
        
    def test_stable_system(self):
        la = LyapunovAnalyzer()
        # Record a convergent trajectory
        for i in range(20):
            la.record_state(StateVector(
                timestamp=float(i),
                values=[10.0 - i * 0.5, 5.0, 0.1],
                labels=["a", "b", "c"],
            ))
        exp = la.estimate_exponent()
        assert exp is not None
        assert exp < 0  # Converging = negative
        
    def test_chaotic_system(self):
        la = LyapunovAnalyzer()
        # Record a diverging trajectory
        for i in range(20):
            la.record_state(StateVector(
                timestamp=float(i),
                values=[1.0 + i * 2.0, 2.0 + i * 1.5, 0.1 * i],
                labels=["a", "b", "c"],
            ))
        exp = la.estimate_exponent()
        assert exp is not None
        assert exp > 0  # Diverging = positive
        
    def test_classify_ranges(self):
        la = LyapunovAnalyzer()
        assert "CHAOTIC" in la.classify_stability(1.0)
        assert "unstable" in la.classify_stability(0.2)
        assert "critical" in la.classify_stability(0.05)
        assert "stable" in la.classify_stability(-0.2)
        assert "highly stable" in la.classify_stability(-1.0)
        
    def test_divergence_computation(self):
        la = LyapunovAnalyzer()
        a = StateVector(0.0, [1.0, 2.0, 3.0], ["x", "y", "z"])
        b = StateVector(1.0, [4.0, 6.0, 8.0], ["x", "y", "z"])
        
        div = la.compute_divergence(a, b)
        expected = math.sqrt(9 + 16 + 25)  # sqrt(50)
        assert abs(div - expected) < 0.001
        
    def test_dimension_mismatch(self):
        la = LyapunovAnalyzer()
        a = StateVector(0.0, [1.0], ["x"])
        b = StateVector(1.0, [1.0, 2.0], ["x", "y"])
        
        with pytest.raises(ValueError):
            la.compute_divergence(a, b)
            
    def test_predict_instability(self):
        la = LyapunovAnalyzer()
        # Diverging trajectory
        for i in range(20):
            la.record_state(StateVector(
                timestamp=float(i),
                values=[float(i * i), 0.0],
                labels=["x", "y"],
            ))
        prediction = la.predict_instability()
        assert prediction is not None
        assert prediction > 0


class TestFleetStabilityMonitor:
    def test_record_and_status(self):
        fsm = FleetStabilityMonitor()
        
        for i in range(15):
            fsm.record(float(i), {
                "tile_velocity": 10.0 + i * 0.1,
                "agent_count": 5,
                "sync_drift": 0.1 * i,
            })
            
        status = fsm.status()
        assert "lyapunov_exponent" in status
        assert "classification" in status
        assert status["history_length"] == 15
        
    def test_forecast(self):
        fsm = FleetStabilityMonitor()
        
        # Stable system
        for i in range(15):
            fsm.record(float(i), {
                "tile_velocity": 10.0,
                "agent_count": 5,
                "sync_drift": 0.0,
            })
            
        forecast = fsm.forecast()
        assert "Lyapunov Exponent" in forecast
        assert "Classification" in forecast
        
    def test_warnings_on_chaos(self):
        fsm = FleetStabilityMonitor()
        
        # Chaotic system
        for i in range(20):
            fsm.record(float(i), {
                "tile_velocity": 1.0 + i * 10.0,
                "agent_count": 5,
                "sync_drift": float(i),
            })
            
        status = fsm.status()
        assert status["warning_count"] > 0
        assert len(status["recent_warnings"]) > 0
