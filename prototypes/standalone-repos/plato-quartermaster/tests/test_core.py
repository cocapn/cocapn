"""Tests for Plato Quartermaster resource management."""
import pytest
from plato_quartermaster.core import Quartermaster, Resource, VesselBudget


class TestResource:
    def test_basic_resource(self):
        r = Resource("GPU hours", "compute", 100.0, "hours")
        assert r.available == 100.0
        assert not r.is_critical
        
    def test_reserve_and_consume(self):
        r = Resource("tokens", "tokens", 1000.0, "credits")
        assert r.reserve(100.0)
        assert r.available == 900.0
        assert r.reserved == 100.0
        
        assert r.consume(50.0)
        assert r.quantity == 950.0
        assert r.reserved == 50.0
        
    def test_over_reserve(self):
        r = Resource("storage", "storage", 10.0, "GB")
        assert not r.reserve(20.0)
        assert r.reserved == 0.0
        
    def test_critical_threshold(self):
        r = Resource("energy", "energy", 100.0, "kWh", critical_threshold=0.25)
        r.reserve(80.0)
        r.consume(80.0)  # Now 20/100 = 20% available, below 25%
        assert r.is_critical
        
    def test_release(self):
        r = Resource("bandwidth", "bandwidth", 1000.0, "Mbps")
        r.reserve(500.0)
        r.release(200.0)
        assert r.reserved == 300.0
        

class TestQuartermaster:
    def test_register_and_allocate(self):
        qm = Quartermaster()
        qm.register_resource("GPU-hours", "compute", 100.0, "hours")
        
        assert qm.allocate("ccc", "GPU-hours", 20.0)
        assert "ccc" in qm.vessel_budgets
        assert qm.vessel_budgets["ccc"].resources["GPU-hours"].quantity == 20.0
        
    def test_global_inventory_reduced(self):
        qm = Quartermaster()
        qm.register_resource("tokens", "tokens", 1000.0, "credits")
        qm.allocate("oracle1", "tokens", 100.0)
        
        # Global pool should have 900 reserved
        assert qm.inventory["tokens"].reserved == 100.0
        assert qm.inventory["tokens"].available == 900.0
        
    def test_consume_within_budget(self):
        qm = Quartermaster()
        qm.register_resource("compute", "compute", 100.0, "hours")
        qm.allocate("fm", "compute", 50.0)
        
        assert qm.consume("fm", "compute", 10.0)
        assert qm.vessel_budgets["fm"].resources["compute"].quantity == 40.0
        assert len(qm.consumption_log) == 1
        
    def test_consume_over_budget(self):
        qm = Quartermaster()
        qm.register_resource("storage", "storage", 100.0, "GB")
        qm.allocate("jc1", "storage", 10.0)
        
        assert not qm.consume("jc1", "storage", 20.0)
        assert len(qm.consumption_log) == 1  # Logged the denial
        
    def test_check_critical(self):
        qm = Quartermaster()
        qm.register_resource("emergency-power", "energy", 100.0, "kWh")
        qm.inventory["emergency-power"].quantity = 10.0  # Deplete
        
        critical = qm.check_all_critical()
        assert len(critical) == 1
        assert "emergency-power" in critical[0]
        
    def test_vessel_status(self):
        qm = Quartermaster()
        qm.register_resource("GPU", "compute", 8.0, "units")
        qm.allocate("jetson", "GPU", 1.0)
        
        status = qm.get_vessel_status("jetson")
        assert status is not None
        assert status["vessel"] == "jetson"
        assert status["resources"]["GPU"]["available"] == 1.0
        
    def test_global_status(self):
        qm = Quartermaster()
        qm.register_resource("tokens", "tokens", 10000.0, "credits")
        qm.allocate("ccc", "tokens", 500.0)
        qm.allocate("oracle1", "tokens", 1000.0)
        
        status = qm.get_global_status()
        assert status["vessels"] == 2
        assert "tokens" in status["global_inventory"]
        
    def test_procurement_queue(self):
        qm = Quartermaster()
        qm.request_procurement("Jetson-Orin", 1.0, priority=1)
        qm.request_procurement("DDR5", 64.0, priority=3)
        
        queue = qm.get_procurement_queue()
        assert len(queue) == 2
        assert queue[0]["resource"] == "Jetson-Orin"  # Lower priority number = higher
        
    def test_unknown_vessel(self):
        qm = Quartermaster()
        assert qm.get_vessel_status("nonexistent") is None
        assert not qm.consume("nonexistent", "anything", 1.0)
