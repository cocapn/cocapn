"""Body image, pain signals, and reflex arcs for fleet vessels."""
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PainLevel(Enum):
    NONE = 0
    DISCOMFORT = 1
    PAIN = 2
    CRITICAL = 3


@dataclass
class PainSignal:
    """Something is wrong with the vessel."""
    source: str
    level: PainLevel
    message: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BodyState:
    """Current state of a vessel."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    network_ok: bool = True
    last_heartbeat: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def is_healthy(self) -> bool:
        return (
            self.cpu_percent < 90 and
            self.memory_percent < 90 and
            self.disk_percent < 95 and
            self.network_ok
        )


@dataclass
class ReflexArc:
    """Automatic response to a condition."""
    name: str
    condition: Callable[[BodyState], bool]
    action: Callable[[], None]
    cooldown_seconds: int = 60
    last_triggered: Optional[str] = None
    
    def check(self, state: BodyState) -> bool:
        if not self.condition(state):
            return False
        if self.last_triggered:
            from datetime import datetime as dt
            last = dt.fromisoformat(self.last_triggered)
            now = dt.utcnow()
            if (now - last).seconds < self.cooldown_seconds:
                return False
        self.last_triggered = dt.utcnow().isoformat()
        self.action()
        return True


class Homunculus:
    """Body image for a fleet vessel."""
    def __init__(self, vessel_name: str):
        self.name = vessel_name
        self.state = BodyState()
        self.reflexes: List[ReflexArc] = []
        self.pain_history: List[PainSignal] = []
        
    def update_state(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        self._check_reflexes()
        
    def add_reflex(self, reflex: ReflexArc) -> None:
        self.reflexes.append(reflex)
        
    def feel_pain(self, source: str, level: PainLevel, message: str) -> None:
        pain = PainSignal(source, level, message)
        self.pain_history.append(pain)
        
    def _check_reflexes(self) -> None:
        for reflex in self.reflexes:
            reflex.check(self.state)
            
    def get_health_report(self) -> Dict[str, Any]:
        return {
            "vessel": self.name,
            "healthy": self.state.is_healthy(),
            "state": self.state.__dict__,
            "active_pains": [
                {"source": p.source, "level": p.level.name, "message": p.message}
                for p in self.pain_history[-5:]
            ],
            "reflexes": len(self.reflexes),
        }
