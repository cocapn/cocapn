"""Plato Quartermaster — Resource management and supply chain for fleet operations.

Tracks inventory, consumption rates, procurement needs, and resource
allocation across fleet vessels and rooms.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from collections import defaultdict


@dataclass
class Resource:
    """A consumable or reusable resource in the fleet."""
    name: str
    category: str  # "compute", "storage", "energy", "bandwidth", "tokens"
    quantity: float
    unit: str  # "GB", "hours", "kWh", "Mbps", "credits"
    reserved: float = 0.0  # Amount allocated but not yet used
    critical_threshold: float = 0.2  # Level at which alert triggers
    
    @property
    def available(self) -> float:
        return self.quantity - self.reserved
        
    @property
    def is_critical(self) -> bool:
        if self.quantity == 0:
            return True
        return self.available / self.quantity < self.critical_threshold
        
    def reserve(self, amount: float) -> bool:
        """Reserve resources. Returns True if successful."""
        if self.available >= amount:
            self.reserved += amount
            return True
        return False
        
    def consume(self, amount: float) -> bool:
        """Consume reserved resources. Returns True if successful."""
        if self.reserved >= amount:
            self.reserved -= amount
            self.quantity -= amount
            return True
        return False
        
    def release(self, amount: float) -> None:
        """Release unused reservations."""
        self.reserved = max(0, self.reserved - amount)


@dataclass
class VesselBudget:
    """Resource budget allocated to a fleet vessel."""
    vessel_name: str
    resources: Dict[str, Resource] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def get_status(self) -> Dict[str, Any]:
        """Human-readable status."""
        return {
            "vessel": self.vessel_name,
            "resources": {
                name: {
                    "available": r.available,
                    "total": r.quantity,
                    "reserved": r.reserved,
                    "unit": r.unit,
                    "critical": r.is_critical,
                }
                for name, r in self.resources.items()
            },
            "last_updated": self.last_updated,
        }


class Quartermaster:
    """Fleet resource management and supply chain coordinator.
    
    The quartermaster tracks what the fleet has, what it needs,
    and when to procure more. It's the logistics brain.
    """
    
    def __init__(self):
        self.inventory: Dict[str, Resource] = {}  # Global pool
        self.vessel_budgets: Dict[str, VesselBudget] = {}
        self.consumption_log: List[Dict[str, Any]] = []
        self.procurement_queue: List[Dict[str, Any]] = []
        
    def register_resource(
        self,
        name: str,
        category: str,
        initial_quantity: float,
        unit: str,
        critical_threshold: float = 0.2,
    ) -> None:
        """Register a new resource type in the fleet inventory."""
        self.inventory[name] = Resource(
            name=name,
            category=category,
            quantity=initial_quantity,
            unit=unit,
            critical_threshold=critical_threshold,
        )
        
    def allocate(self, vessel: str, resource: str, amount: float) -> bool:
        """Allocate resources from global pool to a vessel.
        
        Returns True if allocation successful.
        """
        if resource not in self.inventory:
            return False
            
        # Try to reserve from global pool
        if not self.inventory[resource].reserve(amount):
            return False
            
        # Add to vessel budget
        if vessel not in self.vessel_budgets:
            self.vessel_budgets[vessel] = VesselBudget(vessel_name=vessel)
            
        if resource not in self.vessel_budgets[vessel].resources:
            # Create vessel-local copy with allocated amount
            original = self.inventory[resource]
            self.vessel_budgets[vessel].resources[resource] = Resource(
                name=resource,
                category=original.category,
                quantity=amount,
                unit=original.unit,
                critical_threshold=original.critical_threshold,
            )
        else:
            # Add to existing vessel allocation
            self.vessel_budgets[vessel].resources[resource].quantity += amount
            
        return True
        
    def consume(self, vessel: str, resource: str, amount: float) -> bool:
        """Record consumption from a vessel's budget.
        
        Returns True if consumption within budget.
        """
        if vessel not in self.vessel_budgets:
            return False
        if resource not in self.vessel_budgets[vessel].resources:
            return False
            
        vessel_res = self.vessel_budgets[vessel].resources[resource]
        
        if vessel_res.available < amount:
            # Log over-consumption
            self.consumption_log.append({
                "vessel": vessel,
                "resource": resource,
                "requested": amount,
                "available": vessel_res.available,
                "status": "denied",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return False
            
        vessel_res.consume(amount)
        
        self.consumption_log.append({
            "vessel": vessel,
            "resource": resource,
            "amount": amount,
            "status": "consumed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        return True
        
    def check_all_critical(self) -> List[str]:
        """List all resources at critical levels."""
        critical = []
        for name, resource in self.inventory.items():
            if resource.is_critical:
                critical.append(
                    f"{name}: {resource.available:.1f}/{resource.quantity:.1f} {resource.unit} "
                    f"({resource.available/resource.quantity*100:.0f}% remaining)"
                )
        return critical
        
    def get_vessel_status(self, vessel: str) -> Optional[Dict[str, Any]]:
        """Get resource status for a specific vessel."""
        if vessel not in self.vessel_budgets:
            return None
        return self.vessel_budgets[vessel].get_status()
        
    def get_global_status(self) -> Dict[str, Any]:
        """Get fleet-wide resource status."""
        return {
            "global_inventory": {
                name: {
                    "available": r.available,
                    "total": r.quantity,
                    "unit": r.unit,
                    "critical": r.is_critical,
                }
                for name, r in self.inventory.items()
            },
            "vessels": len(self.vessel_budgets),
            "critical_resources": self.check_all_critical(),
            "consumption_events": len(self.consumption_log),
        }
        
    def forecast_need(self, resource: str, horizon_days: int = 7) -> Optional[float]:
        """Forecast how much of a resource will be needed.
        
        Simple linear extrapolation from recent consumption.
        """
        recent = [
            e for e in self.consumption_log
            if e.get("resource") == resource and e.get("status") == "consumed"
        ][-30:]  # Last 30 consumption events
        
        if not recent:
            return None
            
        total_consumed = sum(e["amount"] for e in recent)
        avg_per_event = total_consumed / len(recent)
        
        # Estimate events per day (simplified)
        if len(recent) >= 2:
            # Calculate average time between events
            from dateutil import parser
            times = [parser.isoparse(e["timestamp"]) for e in recent]
            avg_interval = (times[-1] - times[0]).total_seconds() / (len(times) - 1)
            events_per_day = 86400 / max(avg_interval, 1)
        else:
            events_per_day = 1  # Default assumption
            
        return avg_per_event * events_per_day * horizon_days
        
    def request_procurement(self, resource: str, amount: float, priority: int = 5) -> None:
        """Queue a procurement request."""
        self.procurement_queue.append({
            "resource": resource,
            "amount": amount,
            "priority": priority,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        })
        
    def get_procurement_queue(self) -> List[Dict[str, Any]]:
        """Get sorted procurement queue."""
        return sorted(
            self.procurement_queue,
            key=lambda x: x["priority"],
        )
