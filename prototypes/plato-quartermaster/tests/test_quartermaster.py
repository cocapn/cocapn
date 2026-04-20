"""Tests for plato-quartermaster."""

import json
import time
from pathlib import Path

import pytest

from plato_quartermaster import (
    Quartermaster,
    TranscendenceLevel,
    SystemVitals,
    DigestionTask,
    SelfTrainingPipeline,
    DecisionRecord,
    ReflexArc,
    ReflexType,
    register_reflex,
    check_all_reflexes,
    FleetHomunculus,
    Vessel,
    VesselStatus,
    PainSignal,
)


class TestQuartermaster:
    """Test the GC metabolism engine."""
    
    def test_init_default(self, tmp_path):
        """Test GC initialization with defaults."""
        gc = Quartermaster(vitals_path=tmp_path / "vitals.json")
        assert gc.transcendence == TranscendenceLevel.ASSISTED
        assert gc.disk_threshold == 75.0
        assert gc.memory_threshold == 85.0
        assert len(gc.task_queue) == 0
    
    def test_init_custom_thresholds(self, tmp_path):
        """Test GC with custom thresholds."""
        gc = Quartermaster(
            vitals_path=tmp_path / "vitals.json",
            disk_threshold=80.0,
            memory_threshold=90.0,
        )
        assert gc.disk_threshold == 80.0
        assert gc.memory_threshold == 90.0
    
    def test_tick_empty_queue(self, tmp_path):
        """Test tick with empty queue and healthy vitals."""
        gc = Quartermaster(vitals_path=tmp_path / "vitals.json")
        gc.vitals.disk_usage_percent = 50.0  # Healthy
        gc.vitals.memory_usage_percent = 50.0  # Healthy
        
        actions = gc.tick()
        assert len(actions) == 0  # Nothing to do
    
    def test_tick_disk_pressure(self, tmp_path):
        """Test tick triggers compression on disk pressure."""
        gc = Quartermaster(vitals_path=tmp_path / "vitals.json")
        gc.vitals.disk_usage_percent = 80.0  # Above threshold
        gc.vitals.memory_usage_percent = 50.0
        
        actions = gc.tick()
        assert len(actions) >= 1
        assert any(a["type"] == "compress_bilge" for a in actions)
    
    def test_tick_memory_pressure(self, tmp_path):
        """Test tick triggers clearance on memory pressure."""
        gc = Quartermaster(vitals_path=tmp_path / "vitals.json")
        gc.vitals.disk_usage_percent = 50.0
        gc.vitals.memory_usage_percent = 90.0  # Above threshold
        
        actions = gc.tick()
        assert len(actions) >= 1
        assert any(a["type"] == "glymphatic_clearance" for a in actions)
    
    def test_queue_task(self, tmp_path):
        """Test task queuing."""
        gc = Quartermaster(vitals_path=tmp_path / "vitals.json")
        task = DigestionTask(
            task_id="test-1",
            task_type="compress",
            source_path=tmp_path / "logs",
            priority=0.8,
        )
        gc.queue_task(task)
        assert len(gc.task_queue) == 1


class TestFleetHomunculus:
    """Test fleet proprioception."""
    
    def test_register_vessel(self, tmp_path):
        """Test vessel registration."""
        h = FleetHomunculus(state_path=tmp_path / "homunculus.json")
        vessel = Vessel(
            vessel_id="test-vessel",
            vessel_type="cloud",
            memory_gb=32,
        )
        h.register_vessel(vessel)
        assert "test-vessel" in h.vessels
        assert h.vessels["test-vessel"].memory_gb == 32
    
    def test_heartbeat_healthy(self, tmp_path):
        """Test heartbeat with healthy vitals."""
        h = FleetHomunculus(state_path=tmp_path / "homunculus.json")
        h.register_vessel(Vessel(vessel_id="test", vessel_type="edge"))
        
        pain = h.heartbeat("test", {
            "memory_load": 0.3,
            "cpu_load": 0.2,
        })
        assert pain is None  # No pain
        assert h.vessels["test"].status == VesselStatus.HEALTHY
    
    def test_heartbeat_strained(self, tmp_path):
        """Test heartbeat with strained vitals."""
        h = FleetHomunculus(state_path=tmp_path / "homunculus.json")
        h.register_vessel(Vessel(vessel_id="test", vessel_type="edge"))
        
        pain = h.heartbeat("test", {
            "memory_load": 0.6,  # Getting high
            "cpu_load": 0.7,
        })
        # Should be strained but not painful yet
        assert h.vessels["test"].status == VesselStatus.STRAINED
    
    def test_heartbeat_pain(self, tmp_path):
        """Test heartbeat with painful vitals."""
        h = FleetHomunculus(state_path=tmp_path / "homunculus.json")
        h.register_vessel(Vessel(vessel_id="test", vessel_type="edge"))
        
        pain = h.heartbeat("test", {
            "memory_load": 0.95,  # Above 85% threshold
            "cpu_load": 0.5,
        })
        assert pain is not None
        assert pain.vessel_id == "test"
        assert "memory" in pain.symptom
        assert h.vessels["test"].status == VesselStatus.PAIN
    
    def test_body_summary(self, tmp_path):
        """Test body summary generation."""
        h = FleetHomunculus(state_path=tmp_path / "homunculus.json")
        h.register_vessel(Vessel(vessel_id="v1", vessel_type="cloud", memory_gb=64))
        h.register_vessel(Vessel(vessel_id="v2", vessel_type="edge", memory_gb=8))
        
        summary = h.get_body_summary()
        assert summary["vessels"]["total"] == 2
        assert summary["capacity"]["total_memory_gb"] == 72
    
    def test_find_best_host(self, tmp_path):
        """Test finding best host for workload."""
        h = FleetHomunculus(state_path=tmp_path / "homunculus.json")
        h.register_vessel(Vessel(
            vessel_id="healthy",
            vessel_type="cloud",
            memory_gb=32,
            can_train=True,
        ))
        h.vessels["healthy"].cpu_load = 0.2
        h.vessels["healthy"].memory_load = 0.3
        
        best = h.find_best_host(needs_gpu=False, needs_compile=False)
        assert best == "healthy"


class TestSelfTrainingPipeline:
    """Test the self-training system."""
    
    def test_init_empty(self, tmp_path):
        """Test initialization with no history."""
        p = SelfTrainingPipeline(
            log_path=tmp_path / "decisions.jsonl",
            model_path=tmp_path / "model.pt",
        )
        assert len(p.decisions) == 0
    
    def test_record_decision(self, tmp_path):
        """Test recording a decision."""
        p = SelfTrainingPipeline(log_path=tmp_path / "decisions.jsonl")
        record = DecisionRecord(
            decision_id="test-1",
            context={"disk": 80},
            action_taken="compress",
            outcome={"resolved": True},
        )
        p.record(record)
        assert len(p.decisions) == 1
    
    def test_train_insufficient_data(self, tmp_path):
        """Test training with insufficient data."""
        p = SelfTrainingPipeline(log_path=tmp_path / "decisions.jsonl")
        result = p.train()
        assert result["status"] == "insufficient_data"
    
    def test_predict_default(self, tmp_path):
        """Test prediction with no training."""
        p = SelfTrainingPipeline(log_path=tmp_path / "decisions.jsonl")
        prediction = p.predict({"disk_usage": 95, "memory_usage": 50})
        assert prediction["action"] == "emergency_purge"
        assert prediction["confidence"] == 1.0


class TestReflexArc:
    """Test spinal reflexes."""
    
    def test_reflex_fires_when_triggered(self):
        """Test reflex fires when sensor returns True."""
        reflex = ReflexArc(
            name="test-reflex",
            reflex_type=ReflexType.RESTART,
            sensor=lambda: True,
            actuator=lambda: {"action": "restarted"},
            cooldown_seconds=0,  # No cooldown for testing
        )
        result = reflex.check_and_fire()
        assert result is not None
        assert result["reflex"] == "test-reflex"
    
    def test_reflex_respects_cooldown(self):
        """Test reflex doesn't fire during cooldown."""
        reflex = ReflexArc(
            name="test-reflex",
            reflex_type=ReflexType.RESTART,
            sensor=lambda: True,
            actuator=lambda: {"action": "restarted"},
            cooldown_seconds=300,
        )
        # Fire once
        reflex.check_and_fire()
        # Try to fire again immediately
        result = reflex.check_and_fire()
        assert result is None  # Cooldown prevents second fire
    
    def test_reflex_disabled(self):
        """Test disabled reflex doesn't fire."""
        reflex = ReflexArc(
            name="test-reflex",
            reflex_type=ReflexType.RESTART,
            sensor=lambda: True,
            actuator=lambda: {"action": "restarted"},
            cooldown_seconds=0,
        )
        reflex.disable()
        result = reflex.check_and_fire()
        assert result is None


class TestIntegration:
    """Integration tests across components."""
    
    def test_gc_with_homunculus(self, tmp_path):
        """Test GC using homunculus data."""
        h = FleetHomunculus(state_path=tmp_path / "homunculus.json")
        h.register_vessel(Vessel(vessel_id="fleet-node", vessel_type="edge"))
        
        # Simulate high load
        h.heartbeat("fleet-node", {
            "memory_load": 0.9,
            "cpu_load": 0.5,
        })
        
        # GC should respond to pain signal
        pain = h.get_pain_signals(vessel_id="fleet-node")
        assert len(pain) >= 1
    
    def test_full_tick_cycle(self, tmp_path):
        """Test a full GC tick cycle."""
        gc = Quartermaster(vitals_path=tmp_path / "vitals.json")
        
        # Set up stressful conditions
        gc.vitals.disk_usage_percent = 78
        gc.vitals.memory_usage_percent = 88
        
        # Add a task
        gc.queue_task(DigestionTask(
            task_id="cleanup",
            task_type="compress",
            source_path=tmp_path / "logs",
            priority=0.9,
        ))
        
        # Tick
        actions = gc.tick()
        
        # Should have actions for disk, memory, and task
        assert len(actions) >= 2  # At least disk and memory


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
