"""
quartermaster.py — The GC Itself

The Quartermaster is the gut microbiome of the fleet:
- Billions of micro-decisions about data lifecycle
- Digests what nourishes (compress logs → tiles → wiki)
- Evacuates what doesn't serve (truncate, archive, transcend)
- Signals hunger upstream (disk pressure → compression cycles)
- Produces vitamins (ensigns for other agents)

A body that can't evacuate sinks. A vessel that can't compress crashes.
A crab that can't shed its shell dies.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class TranscendenceLevel(Enum):
    """The 4 levels of GC autonomy."""
    EXTERNAL = 1    # Calls external API for every decision
    ASSISTED = 2    # Uses cached heuristics, API for edge cases
    AUTONOMOUS = 3  # Local LoRA handles 80% of decisions
    TRANSCENDENT = 4  # Knowledge lives in weights, not files


@dataclass
class SystemVitals:
    """The body's vital signs — what the GC monitors."""
    disk_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    cpu_load: float = 0.0
    tile_count: int = 0
    room_count: int = 0
    ensign_count: int = 0
    last_compression: float = 0.0  # timestamp
    timestamp: float = field(default_factory=time.time)


@dataclass  
class DigestionTask:
    """A task the GC needs to process."""
    task_id: str
    task_type: str  # 'compress', 'archive', 'transcend', 'evacuate'
    source_path: Path
    priority: float  # 0.0-1.0, higher = more urgent
    created_at: float = field(default_factory=time.time)


class Quartermaster:
    """
    The fleet's metabolism engine.
    
    The Quartermaster doesn't think. It digests. It handles the
    continuous process of turning raw experience into useful intelligence
    and evacuating what no longer serves.
    """
    
    def __init__(
        self,
        vitals_path: Path = Path("vitals.json"),
        transcendence: TranscendenceLevel = TranscendenceLevel.ASSISTED,
        disk_threshold: float = 75.0,
        memory_threshold: float = 85.0,
    ):
        self.vitals_path = vitals_path
        self.transcendence = transcendence
        self.disk_threshold = disk_threshold
        self.memory_threshold = memory_threshold
        
        self.task_queue: List[DigestionTask] = []
        self.vitals = SystemVitals()
        self.decision_log: List[Dict] = []
        
        # Load historical vitals if available
        if vitals_path.exists():
            self._load_vitals()
    
    def tick(self) -> List[Dict]:
        """
        One GC tick. Read vitals, decide actions, execute.
        
        Returns: list of actions taken this tick.
        """
        actions = []
        
        # Read current vitals
        self._read_vitals()
        
        # Check disk pressure — the bilge pump
        if self.vitals.disk_usage_percent > self.disk_threshold:
            action = self._compress_bilge()
            actions.append(action)
        
        # Check memory pressure — metabolic clearance
        if self.vitals.memory_usage_percent > self.memory_threshold:
            action = self._clear_glymphatic()
            actions.append(action)
        
        # Process digestion queue
        for task in sorted(self.task_queue, key=lambda t: -t.priority):
            action = self._digest(task)
            actions.append(action)
        
        self.task_queue = []  # Clear processed tasks
        
        # Log decisions for self-training
        self._log_decisions(actions)
        
        return actions
    
    def _read_vitals(self) -> None:
        """Read the fleet's vital signs."""
        # In production: read from actual system metrics
        # For now: load from file or use defaults
        if self.vitals_path.exists():
            data = json.loads(self.vitals_path.read_text())
            self.vitals = SystemVitals(**data)
    
    def _load_vitals(self) -> None:
        """Load historical vitals."""
        data = json.loads(self.vitals_path.read_text())
        self.vitals = SystemVitals(**data)
    
    def _compress_bilge(self) -> Dict:
        """
        The bilge pump. Compress logs, truncate stale tiles,
        distill accumulated knowledge to wiki.
        
        Every gallon pumped becomes a tile that makes the next
        pump more efficient. The waste IS the energy.
        """
        action = {
            "type": "compress_bilge",
            "disk_before": self.vitals.disk_usage_percent,
            "disk_after": max(0, self.vitals.disk_usage_percent - 10),
            "method": "distill_to_wiki",
            "tiles_processed": self.vitals.tile_count,
            "timestamp": time.time(),
        }
        
        # Simulate compression
        self.vitals.disk_usage_percent = action["disk_after"]
        self.vitals.last_compression = time.time()
        self._save_vitals()
        
        return action
    
    def _clear_glymphatic(self) -> Dict:
        """
        Glymphatic clearance. During sleep cycles:
        - Log rotation
        - Cache defragmentation  
        - Memory compaction
        
        The forgetting is active, not passive.
        """
        action = {
            "type": "glymphatic_clearance",
            "memory_before": self.vitals.memory_usage_percent,
            "memory_after": max(0, self.vitals.memory_usage_percent - 15),
            "cache_dropped": True,
            "timestamp": time.time(),
        }
        
        self.vitals.memory_usage_percent = action["memory_after"]
        self._save_vitals()
        
        return action
    
    def _digest(self, task: DigestionTask) -> Dict:
        """Process a digestion task."""
        action = {
            "type": f"digest_{task.task_type}",
            "task_id": task.task_id,
            "source": str(task.source_path),
            "priority": task.priority,
            "timestamp": time.time(),
        }
        
        # Task-specific logic would go here
        # compress: gzip old logs
        # archive: move to cold storage
        # transcend: distill to ensign
        # evacuate: delete, but log what was lost
        
        return action
    
    def _log_decisions(self, actions: List[Dict]) -> None:
        """Log decisions for the self-training pipeline."""
        for action in actions:
            self.decision_log.append({
                **action,
                "transcendence_level": self.transcendence.value,
                "vitals_at_decision": {
                    "disk": self.vitals.disk_usage_percent,
                    "memory": self.vitals.memory_usage_percent,
                }
            })
    
    def _save_vitals(self) -> None:
        """Persist vitals to disk."""
        self.vitals_path.write_text(
            json.dumps(self.vitals.__dict__, indent=2)
        )
    
    def queue_task(self, task: DigestionTask) -> None:
        """Queue a task for the next tick."""
        self.task_queue.append(task)
    
    def get_decision_tree(self) -> Dict:
        """
        Export the GC's decision tree for self-training.
        
        At transcendence level 4, the vagus nerve IS the instinct.
        The gut brain has transcended the need for storage.
        """
        return {
            "transcendence": self.transcendence.name,
            "total_decisions": len(self.decision_log),
            "decisions_by_type": self._count_by_type(),
            "pattern_summary": self._extract_patterns(),
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count decisions by action type."""
        counts = {}
        for decision in self.decision_log:
            t = decision.get("type", "unknown")
            counts[t] = counts.get(t, 0) + 1
        return counts
    
    def _extract_patterns(self) -> Dict:
        """Extract patterns from decision log for self-training."""
        # In production: use actual pattern recognition
        # For now: simple heuristics
        if len(self.decision_log) < 10:
            return {"status": "insufficient_data"}
        
        recent = self.decision_log[-10:]
        disk_pressures = [d["vitals_at_decision"]["disk"] for d in recent]
        memory_pressures = [d["vitals_at_decision"]["memory"] for d in recent]
        
        return {
            "avg_disk_pressure": sum(disk_pressures) / len(disk_pressures),
            "avg_memory_pressure": sum(memory_pressures) / len(memory_pressures),
            "compression_frequency": self._count_by_type().get("compress_bilge", 0),
            "status": "pattern_extracted",
        }
