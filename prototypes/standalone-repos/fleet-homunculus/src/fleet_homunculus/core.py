"""Fleet Status Monitor — Integration of deadband, flywheel, and tile-refiner."""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

from flywheel_engine.core import Flywheel, Tile as FlywheelTile
from deadband_protocol.core import MultiChannelObserver, Signal
from tile_refiner.core import TileRefiner, Tile as RefinerTile


@dataclass
class FleetSnapshot:
    """A point-in-time view of fleet health."""
    timestamp: str
    tile_velocity: float  # tiles per hour
    agent_count: int
    active_channels: List[str]
    alerts: List[str]
    health_score: float  # 0.0 to 1.0
    
    def to_markdown(self) -> str:
        lines = [
            f"# Fleet Status — {self.timestamp}",
            "",
            f"**Health Score:** {self.health_score:.2f}",
            f"**Tile Velocity:** {self.tile_velocity:.2f}/hr",
            f"**Active Agents:** {self.agent_count}",
            f"**Channels:** {', '.join(self.active_channels)}",
            "",
            "## Alerts",
        ]
        if self.alerts:
            for alert in self.alerts:
                lines.append(f"- ⚠️ {alert}")
        else:
            lines.append("- ✅ All systems nominal")
        return "\n".join(lines)


class FleetMonitor:
    """Integrated fleet monitoring using all three crate systems.
    
    Architecture:
    - deadband-protocol: Watches for anomalies (observatory)
    - flywheel-engine: Stores and retrieves fleet knowledge (archives)
    - tile-refiner: Compiles status reports from raw data (radio)
    """
    
    def __init__(self):
        self.observer = MultiChannelObserver()
        self.flywheel = Flywheel()
        self.refiner = TileRefiner()
        
        # Register monitoring channels
        self.observer.register_channel(
            "tile-velocity",
            setpoint=10.0,  # expected tiles per hour
            initial_width=8.0,
            min_width=2.0,
        )
        self.observer.register_channel(
            "agent-health",
            setpoint=0.9,  # 90% expected online
            initial_width=0.3,
            min_width=0.05,
        )
        self.observer.register_channel(
            "sync-drift",
            setpoint=0.0,  # zero drift expected
            initial_width=1.0,
            min_width=0.1,
        )
        
        # Create knowledge rooms
        self.flywheel.create_room("harbor", "agent_onboarding")
        self.flywheel.create_room("bridge", "coordination")
        self.flywheel.create_room("observatory", "monitoring")
        
    def record_tile(self, tile: RefinerTile) -> None:
        """Record a tile from fleet activity."""
        # Store in flywheel for retrieval
        fw_tile = FlywheelTile(
            question=tile.question,
            answer=tile.answer,
            confidence=tile.confidence,
            agent=tile.agent,
            room=tile.room,
            tags=tile.tags,
        )
        self.flywheel.add_tile(tile.room, fw_tile)
        
    def check_health(self, metrics: Dict[str, float]) -> FleetSnapshot:
        """Check fleet health and generate snapshot."""
        alerts = []
        now = datetime.now(timezone.utc).isoformat()
        
        # Feed metrics into deadband observer
        for channel, value in metrics.items():
            if channel in self.observer.channels:
                alert = self.observer.observe(
                    channel,
                    Signal(value=value, timestamp=datetime.now(timezone.utc).timestamp(), source="monitor")
                )
                if alert:
                    alerts.append(alert)
                    
        # Compute health score
        health = self._compute_health(metrics)
        
        return FleetSnapshot(
            timestamp=now,
            tile_velocity=metrics.get("tile-velocity", 0.0),
            agent_count=int(metrics.get("agent-count", 0)),
            active_channels=list(self.observer.channels.keys()),
            alerts=alerts,
            health_score=health,
        )
        
    def _compute_health(self, metrics: Dict[str, float]) -> float:
        """Compute overall fleet health score."""
        scores = []
        
        # Tile velocity: 0-20 range mapped to 0-1
        tv = metrics.get("tile-velocity", 0.0)
        scores.append(min(tv / 20.0, 1.0))
        
        # Agent health: direct 0-1
        ah = metrics.get("agent-health", 0.0)
        scores.append(max(0.0, min(ah, 1.0)))
        
        # Sync drift: lower is better, invert
        sd = metrics.get("sync-drift", 0.0)
        scores.append(max(0.0, 1.0 - abs(sd)))
        
        return sum(scores) / len(scores) if scores else 0.0
        
    def generate_status_report(self) -> str:
        """Generate a fleet status report from current knowledge."""
        # Query flywheel for recent tiles
        recent = self.flywheel.inject("ccc", "observatory", "recent fleet activity", top_k=10)
        
        # Convert to refiner tiles
        refiner_tiles = [
            RefinerTile(
                question=t.question,
                answer=t.answer,
                confidence=t.confidence,
                agent=t.agent,
                room=t.room,
                tags=t.tags,
            )
            for t in recent
        ]
        
        # Refine into artifact
        if refiner_tiles:
            artifact = self.refiner.refine_cluster(
                refiner_tiles,
                "Fleet Status Report"
            )
            return artifact.to_markdown()
        
        return "# Fleet Status\n\nNo recent activity recorded."
        
    def get_full_stats(self) -> Dict[str, Any]:
        """Get complete monitoring statistics."""
        return {
            "flywheel": self.flywheel.get_stats(),
            "observer": self.observer.get_all_stats(),
            "refiner": self.refiner.get_stats(),
        }
