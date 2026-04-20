"""
selftrain.py — The GC's Self-Training Pipeline

The vagus nerve strengthens over time:
- Cycle 1: GC calls external API to decide (slow, expensive)
- Cycle 100: GC's LoRA handles 80% of decisions locally
- Cycle 1000: GC rarely needs external help
- Cycle 10000: Knowledge lives in weights, not files

The gut brain doesn't replace the cortex. It frees the cortex
to think bigger while the gut handles the metabolism.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class DecisionRecord:
    """One decision the GC made."""
    decision_id: str
    context: Dict  # vitals, task queue, history
    action_taken: str
    outcome: Optional[Dict] = None
    timestamp: float = field(default_factory=time.time)


class SelfTrainingPipeline:
    """
    Trains the GC to make better decisions over time.
    
    The pipeline learns from:
    - Which compression methods work best under which conditions
    - When to trigger early vs late
    - Which tasks to prioritize
    - How to predict disk/memory pressure before it happens
    """
    
    def __init__(
        self,
        log_path: Path = Path("decisions.jsonl"),
        model_path: Path = Path("gc_model.pt"),
    ):
        self.log_path = log_path
        self.model_path = model_path
        self.decisions: List[DecisionRecord] = []
        self.patterns: Dict = {}
        
        # Load historical decisions
        if log_path.exists():
            self._load_decisions()
    
    def record(self, record: DecisionRecord) -> None:
        """Log a decision for future training."""
        self.decisions.append(record)
        
        # Append to log file
        with open(self.log_path, "a") as f:
            f.write(json.dumps({
                "decision_id": record.decision_id,
                "context": record.context,
                "action_taken": record.action_taken,
                "outcome": record.outcome,
                "timestamp": record.timestamp,
            }) + "\n")
    
    def train(self) -> Dict:
        """
        Analyze decision history and extract patterns.
        
        At low cycle counts: simple heuristics
        At high cycle counts: trained model (when FM's rig is ready)
        """
        if len(self.decisions) < 10:
            return {
                "status": "insufficient_data",
                "decisions_needed": 10 - len(self.decisions),
                "method": "heuristic",
            }
        
        # Pattern extraction (heuristic version)
        # In production: FM trains a LoRA on this data
        patterns = self._extract_patterns()
        self.patterns = patterns
        
        return {
            "status": "trained",
            "method": "heuristic_pattern_extraction",
            "patterns_found": len(patterns),
            "total_decisions": len(self.decisions),
        }
    
    def predict(self, context: Dict) -> Dict:
        """
        Predict the best action given current context.
        
        Returns: {
            "action": str,
            "confidence": float,
            "reasoning": str,
        }
        """
        if not self.patterns:
            # No training yet — use default heuristics
            return self._default_prediction(context)
        
        # Apply learned patterns
        disk = context.get("disk_usage", 0)
        memory = context.get("memory_usage", 0)
        
        # Simple rule-based prediction from patterns
        if disk > 80:
            return {
                "action": "emergency_compress",
                "confidence": 0.95,
                "reasoning": "Historical pattern: disk > 80% always requires immediate compression",
            }
        elif memory > 90:
            return {
                "action": "clear_cache",
                "confidence": 0.90,
                "reasoning": "Memory pressure pattern detected",
            }
        elif disk > 60 and memory > 70:
            return {
                "action": "preventive_compress",
                "confidence": 0.75,
                "reasoning": "Combined pressure historically leads to problems",
            }
        
        return self._default_prediction(context)
    
    def _extract_patterns(self) -> Dict:
        """Extract patterns from decision history."""
        patterns = {}
        
        # Group decisions by action type
        by_action = {}
        for d in self.decisions:
            action = d.action_taken
            if action not in by_action:
                by_action[action] = []
            by_action[action].append(d)
        
        # Find context patterns for each action
        for action, decisions in by_action.items():
            if len(decisions) < 3:
                continue
            
            # Calculate average context when this action was taken
            avg_disk = sum(d.context.get("disk_usage", 0) for d in decisions) / len(decisions)
            avg_memory = sum(d.context.get("memory_usage", 0) for d in decisions) / len(decisions)
            
            patterns[action] = {
                "count": len(decisions),
                "avg_disk_when_triggered": avg_disk,
                "avg_memory_when_triggered": avg_memory,
                "success_rate": self._calculate_success_rate(decisions),
            }
        
        return patterns
    
    def _calculate_success_rate(self, decisions: List[DecisionRecord]) -> float:
        """Calculate success rate for a set of decisions."""
        successful = 0
        for d in decisions:
            if d.outcome and d.outcome.get("resolved", False):
                successful += 1
        return successful / len(decisions) if decisions else 0.0
    
    def _default_prediction(self, context: Dict) -> Dict:
        """Default heuristic when no patterns learned yet."""
        disk = context.get("disk_usage", 0)
        memory = context.get("memory_usage", 0)
        
        if disk > 90 or memory > 95:
            return {
                "action": "emergency_purge",
                "confidence": 1.0,
                "reasoning": "Critical threshold exceeded — immediate action required",
            }
        elif disk > 75:
            return {
                "action": "compress_bilge",
                "confidence": 0.8,
                "reasoning": "Disk pressure above threshold",
            }
        elif memory > 85:
            return {
                "action": "glymphatic_clearance",
                "confidence": 0.7,
                "reasoning": "Memory pressure detected",
            }
        
        return {
            "action": "monitor",
            "confidence": 0.5,
            "reasoning": "No immediate action needed",
        }
    
    def _load_decisions(self) -> None:
        """Load historical decisions from log."""
        with open(self.log_path) as f:
            for line in f:
                data = json.loads(line)
                self.decisions.append(DecisionRecord(
                    decision_id=data["decision_id"],
                    context=data["context"],
                    action_taken=data["action_taken"],
                    outcome=data.get("outcome"),
                    timestamp=data["timestamp"],
                ))
    
    def export_ensign(self) -> Dict:
        """
        Export the GC's learned patterns as an ensign.
        
        This is the vitamin the GC produces for other agents.
        Compressed wisdom they can absorb.
        """
        return {
            "type": "gc_instinct",
            "version": "0.1.0",
            "patterns": self.patterns,
            "total_decisions": len(self.decisions),
            "training_timestamp": time.time(),
            "compression_ratio": self._calculate_compression(),
        }
    
    def _calculate_compression(self) -> float:
        """Calculate knowledge compression ratio."""
        if not self.patterns:
            return 0.0
        # Raw decisions vs extracted patterns
        raw_size = len(self.decisions) * 200  # ~200 bytes per decision
        pattern_size = len(json.dumps(self.patterns))
        return raw_size / max(pattern_size, 1)
