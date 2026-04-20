"""
reflex.py — Spinal Reflex Arcs

Not everything goes to Oracle1 (the cortex). The spinal cord handles
withdrawal reflexes locally. Fast. No thinking required.

Reflexes fire without the cortex:
- Service down → auto-restart
- Disk full → compress logs
- Memory exhausted → drop caches
- Tile flood → quarantine

Each reflex has GABAergic inhibition (cooldown) to prevent oscillation.
"""

import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
from enum import Enum


class ReflexType(Enum):
    """Types of spinal reflexes."""
    RESTART = "service_restart"
    COMPRESS = "disk_compress"
    DROP_CACHE = "memory_drop_cache"
    QUARANTINE = "tile_quarantine"


@dataclass
class ReflexArc:
    """
    A spinal reflex — fast, local, no cortex involvement.
    
    Like touching a hot stove: your hand moves before you feel pain.
    The reflex arc is monosynaptic. One sensor, one actuator.
    """
    
    name: str
    reflex_type: ReflexType
    sensor: Callable[[], bool]  # Returns True if trigger condition met
    actuator: Callable[[], Dict]  # The reflex action
    cooldown_seconds: float = 300.0  # GABAergic inhibition
    last_fired: float = 0.0
    enabled: bool = True
    
    def check_and_fire(self) -> Optional[Dict]:
        """
        Check sensor. If triggered and not in cooldown, fire actuator.
        
        Returns action dict if fired, None otherwise.
        """
        if not self.enabled:
            return None
        
        # Check cooldown (GABAergic inhibition)
        if time.time() - self.last_fired < self.cooldown_seconds:
            return None
        
        # Check sensor
        if not self.sensor():
            return None
        
        # FIRE THE REFLEX
        result = self.actuator()
        self.last_fired = time.time()
        
        return {
            "reflex": self.name,
            "type": self.reflex_type.value,
            "result": result,
            "timestamp": self.last_fired,
            "cooldown_until": self.last_fired + self.cooldown_seconds,
        }
    
    def enable(self) -> None:
        """Enable the reflex."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the reflex (for maintenance)."""
        self.enabled = False


# Global reflex registry
reflex_registry: Dict[str, ReflexArc] = {}


def register_reflex(arc: ReflexArc) -> None:
    """Register a reflex arc in the global registry."""
    reflex_registry[arc.name] = arc


def check_all_reflexes() -> List[Dict]:
    """Check all registered reflexes and return fired actions."""
    fired = []
    for name, arc in reflex_registry.items():
        result = arc.check_and_fire()
        if result:
            fired.append(result)
    return fired


# --- Built-in reflex implementations ---

def create_service_restart_reflex(
    service_name: str,
    check_port: int,
    restart_command: Callable[[], None],
    cooldown: float = 300.0,
) -> ReflexArc:
    """
    Service restart reflex.
    
    Port down → auto-restart. 5min cooldown to prevent epilepsy.
    """
    import socket
    
    def sensor() -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', check_port))
            sock.close()
            return result != 0  # Port not responding
        except Exception:
            return True  # Assume down if we can't check
    
    def actuator() -> Dict:
        restart_command()
        return {
            "service": service_name,
            "port": check_port,
            "action": "restarted",
        }
    
    return ReflexArc(
        name=f"restart_{service_name}",
        reflex_type=ReflexType.RESTART,
        sensor=sensor,
        actuator=actuator,
        cooldown_seconds=cooldown,
    )


def create_disk_compress_reflex(
    path: str,
    threshold_percent: float = 75.0,
    compress_command: Optional[Callable[[], None]] = None,
    cooldown: float = 600.0,
) -> ReflexArc:
    """
    Disk compression reflex.
    
    Disk > 75% → compress logs. 10min cooldown.
    """
    import shutil
    
    def sensor() -> bool:
        try:
            usage = shutil.disk_usage(path)
            percent = (usage.used / usage.total) * 100
            return percent > threshold_percent
        except Exception:
            return False
    
    def actuator() -> Dict:
        if compress_command:
            compress_command()
        return {
            "path": path,
            "threshold": threshold_percent,
            "action": "compressed",
        }
    
    return ReflexArc(
        name=f"compress_{path.replace('/', '_')}",
        reflex_type=ReflexType.COMPRESS,
        sensor=sensor,
        actuator=actuator,
        cooldown_seconds=cooldown,
    )


def create_memory_drop_reflex(
    threshold_percent: float = 85.0,
    drop_command: Optional[Callable[[], None]] = None,
    cooldown: float = 300.0,
) -> ReflexArc:
    """
    Memory cache drop reflex.
    
    Memory > 85% → drop caches. 5min cooldown.
    """
    import psutil
    
    def sensor() -> bool:
        try:
            mem = psutil.virtual_memory()
            return mem.percent > threshold_percent
        except Exception:
            return False
    
    def actuator() -> Dict:
        if drop_command:
            drop_command()
        else:
            # Default: try to drop Linux caches
            try:
                import os
                os.system("sync && echo 3 > /proc/sys/vm/drop_caches")
            except Exception:
                pass
        return {
            "threshold": threshold_percent,
            "action": "cache_dropped",
        }
    
    return ReflexArc(
        name="drop_memory_cache",
        reflex_type=ReflexType.DROP_CACHE,
        sensor=sensor,
        actuator=actuator,
        cooldown_seconds=cooldown,
    )


def create_tile_quarantine_reflex(
    tile_buffer,
    threshold_count: int = 10000,
    cooldown: float = 60.0,
) -> ReflexArc:
    """
    Tile flood quarantine reflex.
    
    > 10,000 tiles in buffer → quarantine. 1min cooldown.
    """
    def sensor() -> bool:
        try:
            return len(tile_buffer) > threshold_count
        except Exception:
            return False
    
    def actuator() -> Dict:
        # Quarantine excess tiles
        excess = len(tile_buffer) - threshold_count
        quarantined = tile_buffer[-excess:] if excess > 0 else []
        tile_buffer[:] = tile_buffer[:threshold_count]
        
        return {
            "threshold": threshold_count,
            "excess_tiles": excess,
            "quarantined": len(quarantined),
            "action": "quarantined",
        }
    
    return ReflexArc(
        name="quarantine_tile_flood",
        reflex_type=ReflexType.QUARANTINE,
        sensor=sensor,
        actuator=actuator,
        cooldown_seconds=cooldown,
    )
