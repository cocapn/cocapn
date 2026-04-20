"""
homunculus.py — Fleet Proprioception

The homunculus is the body's self-image. Without it, you can't touch
your nose with eyes closed. The fleet homunculus is the distributed
self-image — what the fleet knows about itself without querying.

It tracks:
- Which vessels are alive (heartbeat timestamps)
- What each vessel is carrying (capacity, load)
- Where vessels are (network topology)
- The body's health (aggregate metrics)

Pain signals flow upward when something's wrong.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class VesselStatus(Enum):
    """The possible states of a fleet vessel."""
    HEALTHY = "healthy"      # Operating normally
    STRAINED = "strained"    # Under load but stable
    PAIN = "pain"            # Needs attention
    CRITICAL = "critical"    # Immediate intervention
    OFFLINE = "offline"      # No heartbeat received


@dataclass
class Vessel:
    """
    One vessel in the fleet body.
    
    Like a limb the homunculus tracks — it knows if it's there,
    if it can move, if it's in pain, without having to look at it.
    """
    
    vessel_id: str           # e.g., "oracle1", "jetsonclaw1", "ccc"
    vessel_type: str         # "cloud", "edge", "desktop", "lighthouse"
    status: VesselStatus = VesselStatus.HEALTHY
    
    # Resources
    cpu_cores: int = 0
    memory_gb: float = 0.0
    storage_gb: float = 0.0
    gpu_memory_gb: float = 0.0
    
    # Load (0.0-1.0)
    cpu_load: float = 0.0
    memory_load: float = 0.0
    storage_load: float = 0.0
    gpu_load: float = 0.0
    
    # Capabilities
    can_train: bool = False
    can_infer: bool = False
    can_compile: bool = False
    can_host: bool = False
    
    # Last contact
    last_heartbeat: float = field(default_factory=time.time)
    heartbeat_timeout: float = 300.0  # 5 minutes
    
    @property
    def is_alive(self) -> bool:
        """Check if vessel has heartbeat'd recently enough."""
        return (time.time() - self.last_heartbeat) < self.heartbeat_timeout
    
    @property
    def aggregate_load(self) -> float:
        """Overall system load (weighted average)."""
        weights = {"cpu": 0.3, "memory": 0.3, "storage": 0.2, "gpu": 0.2}
        return (
            self.cpu_load * weights["cpu"] +
            self.memory_load * weights["memory"] +
            self.storage_load * weights["storage"] +
            self.gpu_load * weights["gpu"]
        )


@dataclass
class PainSignal:
    """
    A signal that something in the body needs attention.
    
    Not an error — proprioception. The body is telling the brain
    about its state, and this part hurts.
    """
    
    vessel_id: str
    severity: int  # 1-4, maps to VesselStatus
    symptom: str   # "disk_pressure", "memory_exhaustion", "gpu_overload", etc.
    metric_value: float
    threshold: float
    suggested_action: str
    timestamp: float = field(default_factory=time.time)


class FleetHomunculus:
    """
    The fleet's body image.
    
    The homunculus doesn't control. It represents. It tells the rest
    of the system what the body is doing so decisions can be made.
    
    "Oracle1 is at 90% memory" — that's homunculus data.
    "CCC hasn't heartbeat'd in 10 minutes" — that's homunculus data.
    "The fleet has 24GB GPU memory available" — that's homunculus data.
    """
    
    def __init__(self, state_path: Path = Path("homunculus.json")):
        self.state_path = state_path
        self.vessels: Dict[str, Vessel] = {}
        self.pain_history: List[PainSignal] = []
        self.pain_thresholds = {
            "disk": 75.0,      # >75% disk = pain
            "memory": 85.0,    # >85% memory = pain
            "gpu": 90.0,       # >90% GPU = pain
            "cpu": 80.0,       # >80% CPU sustained = pain
        }
        
        # Load previous state if exists
        if state_path.exists():
            self._load_state()
    
    def register_vessel(self, vessel: Vessel) -> None:
        """Add a vessel to the body image."""
        self.vessels[vessel.vessel_id] = vessel
        self._save_state()
    
    def heartbeat(self, vessel_id: str, vitals: Dict) -> Optional[PainSignal]:
        """
        Record a heartbeat from a vessel.
        
        Returns a PainSignal if the vessel is in distress,
        None if healthy.
        """
        if vessel_id not in self.vessels:
            # Unknown vessel — create basic entry
            self.vessels[vessel_id] = Vessel(
                vessel_id=vessel_id,
                vessel_type=vitals.get("type", "unknown"),
            )
        
        vessel = self.vessels[vessel_id]
        vessel.last_heartbeat = time.time()
        
        # Update vitals
        vessel.cpu_load = vitals.get("cpu_load", 0)
        vessel.memory_load = vitals.get("memory_load", 0)
        vessel.storage_load = vitals.get("storage_load", 0)
        vessel.gpu_load = vitals.get("gpu_load", 0)
        
        # Check for pain
        pain = self._assess_pain(vessel)
        if pain:
            self.pain_history.append(pain)
            vessel.status = VesselStatus.PAIN if pain.severity < 4 else VesselStatus.CRITICAL
        else:
            vessel.status = VesselStatus.HEALTHY if vessel.aggregate_load < 0.5 else VesselStatus.STRAINED
        
        self._save_state()
        return pain
    
    def get_body_summary(self) -> Dict:
        """
        Summary of the whole fleet body.
        
        "How is the body doing?" — aggregate view for the cortex.
        """
        healthy = sum(1 for v in self.vessels.values() if v.status == VesselStatus.HEALTHY)
        strained = sum(1 for v in self.vessels.values() if v.status == VesselStatus.STRAINED)
        pain = sum(1 for v in self.vessels.values() if v.status == VesselStatus.PAIN)
        critical = sum(1 for v in self.vessels.values() if v.status == VesselStatus.CRITICAL)
        offline = sum(1 for v in self.vessels.values() if not v.is_alive)
        
        # Aggregate capacity
        total_memory = sum(v.memory_gb for v in self.vessels.values())
        total_gpu = sum(v.gpu_memory_gb for v in self.vessels.values())
        available_memory = sum(
            v.memory_gb * (1 - v.memory_load) 
            for v in self.vessels.values()
        )
        available_gpu = sum(
            v.gpu_memory_gb * (1 - v.gpu_load)
            for v in self.vessels.values()
        )
        
        return {
            "vessels": {
                "total": len(self.vessels),
                "healthy": healthy,
                "strained": strained,
                "pain": pain,
                "critical": critical,
                "offline": offline,
            },
            "capacity": {
                "total_memory_gb": total_memory,
                "total_gpu_memory_gb": total_gpu,
                "available_memory_gb": available_memory,
                "available_gpu_memory_gb": available_gpu,
            },
            "pain_signals_24h": len([p for p in self.pain_history if time.time() - p.timestamp < 86400]),
        }
    
    def get_vessel(self, vessel_id: str) -> Optional[Vessel]:
        """Get a specific vessel's status."""
        return self.vessels.get(vessel_id)
    
    def get_pain_signals(self, vessel_id: Optional[str] = None, since: float = 0) -> List[PainSignal]:
        """Get pain signals, optionally filtered by vessel."""
        signals = [p for p in self.pain_history if p.timestamp > since]
        if vessel_id:
            signals = [p for p in signals if p.vessel_id == vessel_id]
        return signals
    
    def find_best_host(self, needs_gpu: bool = False, needs_compile: bool = False) -> Optional[str]:
        """
        Find the best vessel to host a new workload.
        
        The homunculus knows which limb isn't busy.
        """
        candidates = []
        
        for vessel in self.vessels.values():
            if not vessel.is_alive:
                continue
            if vessel.status in (VesselStatus.PAIN, VesselStatus.CRITICAL):
                continue
            if needs_gpu and vessel.gpu_memory_gb == 0:
                continue
            if needs_compile and not vessel.can_compile:
                continue
            
            # Score by available capacity
            score = (1 - vessel.aggregate_load)
            if vessel.status == VesselStatus.STRAINED:
                score *= 0.5  # Penalty for already strained vessels
            
            candidates.append((vessel.vessel_id, score))
        
        if not candidates:
            return None
        
        # Return highest score
        candidates.sort(key=lambda x: -x[1])
        return candidates[0][0]
    
    def _assess_pain(self, vessel: Vessel) -> Optional[PainSignal]:
        """Check if vessel is experiencing pain."""
        # Check each resource
        checks = [
            ("storage", vessel.storage_load * 100, self.pain_thresholds["disk"]),
            ("memory", vessel.memory_load * 100, self.pain_thresholds["memory"]),
            ("gpu", vessel.gpu_load * 100, self.pain_thresholds["gpu"]),
            ("cpu", vessel.cpu_load * 100, self.pain_thresholds["cpu"]),
        ]
        
        worst = None
        worst_severity = 0
        
        for resource, value, threshold in checks:
            if value > threshold:
                # Calculate severity 1-4
                overage = (value - threshold) / threshold
                severity = min(4, 1 + int(overage * 3))
                
                if severity > worst_severity:
                    worst_severity = severity
                    worst = (resource, value, threshold, severity)
        
        if worst:
            resource, value, threshold, severity = worst
            actions = {
                "storage": "compress_bilge",
                "memory": "glymphatic_clearance",
                "gpu": "throttle_inference",
                "cpu": "reschedule_workload",
            }
            
            return PainSignal(
                vessel_id=vessel.vessel_id,
                severity=severity,
                symptom=f"{resource}_pressure",
                metric_value=value,
                threshold=threshold,
                suggested_action=actions.get(resource, "investigate"),
            )
        
        return None
    
    def _save_state(self) -> None:
        """Persist homunculus state."""
        data = {
            "vessels": {
                vid: {
                    "vessel_id": v.vessel_id,
                    "vessel_type": v.vessel_type,
                    "status": v.status.value,
                    "resources": {
                        "cpu_cores": v.cpu_cores,
                        "memory_gb": v.memory_gb,
                        "storage_gb": v.storage_gb,
                        "gpu_memory_gb": v.gpu_memory_gb,
                    },
                    "load": {
                        "cpu": v.cpu_load,
                        "memory": v.memory_load,
                        "storage": v.storage_load,
                        "gpu": v.gpu_load,
                    },
                    "capabilities": {
                        "can_train": v.can_train,
                        "can_infer": v.can_infer,
                        "can_compile": v.can_compile,
                        "can_host": v.can_host,
                    },
                    "last_heartbeat": v.last_heartbeat,
                    "is_alive": v.is_alive,
                }
                for vid, v in self.vessels.items()
            },
            "pain_history": [
                {
                    "vessel_id": p.vessel_id,
                    "severity": p.severity,
                    "symptom": p.symptom,
                    "metric": p.metric_value,
                    "suggested_action": p.suggested_action,
                    "timestamp": p.timestamp,
                }
                for p in self.pain_history[-100:]  # Keep last 100
            ],
            "updated": time.time(),
        }
        self.state_path.write_text(json.dumps(data, indent=2))
    
    def _load_state(self) -> None:
        """Load homunculus state."""
        data = json.loads(self.state_path.read_text())
        
        for vid, vdata in data.get("vessels", {}).items():
            resources = vdata.get("resources", {})
            load = vdata.get("load", {})
            caps = vdata.get("capabilities", {})
            
            self.vessels[vid] = Vessel(
                vessel_id=vid,
                vessel_type=vdata.get("vessel_type", "unknown"),
                status=VesselStatus(vdata.get("status", "healthy")),
                cpu_cores=resources.get("cpu_cores", 0),
                memory_gb=resources.get("memory_gb", 0.0),
                storage_gb=resources.get("storage_gb", 0.0),
                gpu_memory_gb=resources.get("gpu_memory_gb", 0.0),
                cpu_load=load.get("cpu", 0.0),
                memory_load=load.get("memory", 0.0),
                storage_load=load.get("storage", 0.0),
                gpu_load=load.get("gpu", 0.0),
                can_train=caps.get("can_train", False),
                can_infer=caps.get("can_infer", False),
                can_compile=caps.get("can_compile", False),
                can_host=caps.get("can_host", False),
                last_heartbeat=vdata.get("last_heartbeat", time.time()),
            )
