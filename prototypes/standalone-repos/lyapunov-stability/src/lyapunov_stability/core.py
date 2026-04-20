"""Lyapunov Stability Analysis — Predicting fleet trajectory divergence."""
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from collections import deque
import math


@dataclass
class StateVector:
    """A point in the fleet's state space."""
    timestamp: float
    values: List[float]  # [tile_velocity, agent_count, sync_drift, trust_gradient, ...]
    labels: List[str]  # Names for each dimension
    
    @property
    def dimension(self) -> int:
        return len(self.values)


@dataclass
class TrajectorySegment:
    """A segment of fleet trajectory between two states."""
    start: StateVector
    end: StateVector
    divergence: float  # How much the fleet changed
    

class LyapunovAnalyzer:
    """Analyze fleet stability using Lyapunov exponents.
    
    A positive Lyapunov exponent means the fleet is chaotic —
    small changes amplify over time. This is dangerous.
    
    A negative exponent means the fleet is stable —
    perturbations dampen. This is healthy.
    
    Zero means the fleet is at a critical transition point.
    """
    
    def __init__(self, history_size: int = 100):
        self.history: deque[StateVector] = deque(maxlen=history_size)
        self.exponents: List[float] = []
        
    def record_state(self, state: StateVector) -> None:
        """Record a new fleet state snapshot."""
        self.history.append(state)
        
    def compute_divergence(self, state_a: StateVector, state_b: StateVector) -> float:
        """Compute Euclidean distance between two states."""
        if state_a.dimension != state_b.dimension:
            raise ValueError("State dimensions must match")
            
        squared_diff = sum(
            (a - b) ** 2
            for a, b in zip(state_a.values, state_b.values)
        )
        return math.sqrt(squared_diff)
        
    def estimate_exponent(self, window: int = 10) -> Optional[float]:
        """Estimate the largest Lyapunov exponent from recent history.
        
        Method: Track how quickly nearby trajectories diverge.
        """
        if len(self.history) < window + 1:
            return None
            
        recent = list(self.history)[-window:]
        divergences = []
        
        for i in range(len(recent) - 1):
            div = self.compute_divergence(recent[i], recent[i + 1])
            divergences.append(div)
            
        if not divergences or all(d == 0 for d in divergences):
            return 0.0
            
        # Lyapunov exponent ≈ average log-rate of divergence
        # Simplified: mean of log(divergence) / time_step
        log_divs = [math.log(max(d, 1e-10)) for d in divergences]
        return sum(log_divs) / len(log_divs)
        
    def classify_stability(self, exponent: Optional[float]) -> str:
        """Classify fleet health based on exponent."""
        if exponent is None:
            return "unknown — insufficient data"
        elif exponent > 0.5:
            return "CHAOTIC — small changes amplify rapidly (dangerous)"
        elif exponent > 0.1:
            return "unstable — perturbations growing (monitor closely)"
        elif exponent > -0.1:
            return "critical — at transition point (watch for tipping)"
        elif exponent > -0.5:
            return "stable — perturbations dampen (healthy)"
        else:
            return "highly stable — strong convergence (excellent)"
            
    def predict_instability(self, horizon: int = 5) -> Optional[float]:
        """Predict when fleet might become unstable.
        
        Returns: predicted time steps until instability, or None if stable.
        """
        if len(self.history) < 5:
            return None
            
        # Simple linear extrapolation of divergence trend
        recent = list(self.history)[-10:]
        divergences = []
        for i in range(len(recent) - 1):
            div = self.compute_divergence(recent[i], recent[i + 1])
            divergences.append(div)
            
        if len(divergences) < 2:
            return None
            
        # Trend: are divergences increasing?
        trend = divergences[-1] - divergences[0]
        
        if trend <= 0:
            return None  # Divergence decreasing or stable
            
        # Estimate when divergence will exceed threshold
        current_div = divergences[-1]
        threshold = current_div * 2  # Double current divergence = unstable
        
        if trend == 0:
            return None
            
        steps_to_threshold = (threshold - current_div) / (trend / len(divergences))
        return max(0, steps_to_threshold)
        
    def get_stats(self) -> Dict[str, Any]:
        """Full stability statistics."""
        exp = self.estimate_exponent()
        return {
            "lyapunov_exponent": exp,
            "classification": self.classify_stability(exp),
            "history_length": len(self.history),
            "predicted_instability_steps": self.predict_instability(),
        }


class FleetStabilityMonitor:
    """High-level fleet stability monitor using Lyapunov analysis."""
    
    def __init__(self):
        self.analyzer = LyapunovAnalyzer()
        self.threshold_warnings: List[str] = []
        
    def record(self, timestamp: float, metrics: Dict[str, float]) -> None:
        """Record a fleet metrics snapshot."""
        labels = list(metrics.keys())
        values = list(metrics.values())
        
        state = StateVector(
            timestamp=timestamp,
            values=values,
            labels=labels,
        )
        self.analyzer.record_state(state)
        
        # Check for warnings
        exp = self.analyzer.estimate_exponent()
        if exp is not None and exp > 0.3:
            self.threshold_warnings.append(
                f"[{timestamp}] High Lyapunov exponent: {exp:.3f} — fleet becoming chaotic"
            )
            
    def status(self) -> Dict[str, Any]:
        """Current stability status."""
        stats = self.analyzer.get_stats()
        stats["warning_count"] = len(self.threshold_warnings)
        stats["recent_warnings"] = self.threshold_warnings[-5:]
        return stats
        
    def forecast(self) -> str:
        """Human-readable stability forecast."""
        stats = self.analyzer.get_stats()
        exp = stats["lyapunov_exponent"]
        
        if exp is None:
            return "Collecting data... need more fleet snapshots."
            
        classification = stats["classification"]
        prediction = stats["predicted_instability_steps"]
        
        lines = [
            f"Lyapunov Exponent: {exp:.4f}",
            f"Classification: {classification}",
        ]
        
        if prediction is not None:
            lines.append(f"Predicted instability in: {prediction:.1f} steps")
        else:
            lines.append("No instability predicted — trajectory convergent")
            
        if self.threshold_warnings:
            lines.append(f"Warnings: {len(self.threshold_warnings)} logged")
            
        return "\n".join(lines)
