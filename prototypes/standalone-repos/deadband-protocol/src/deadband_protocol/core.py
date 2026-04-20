"""Adaptive deadband protocol — when to act vs. when to wait."""
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Tuple
from collections import deque
import math


@dataclass
class Signal:
    """A timestamped measurement from a sensor or agent."""
    value: float
    timestamp: float  # seconds since epoch
    source: str = "unknown"
    label: str = "generic"


@dataclass
class DeadbandState:
    """Current state of a deadband controller."""
    setpoint: float
    deadband_width: float  # total width (±width/2 around setpoint)
    last_action_time: float = 0.0
    action_count: int = 0
    history: deque = field(default_factory=lambda: deque(maxlen=100))
    
    @property
    def lower_bound(self) -> float:
        return self.setpoint - self.deadband_width / 2
        
    @property
    def upper_bound(self) -> float:
        return self.setpoint + self.deadband_width / 2
        
    def is_inside(self, value: float) -> bool:
        return self.lower_bound <= value <= self.upper_bound


class AdaptiveDeadband:
    """Adaptive deadband controller for fleet observability.
    
    A deadband defines a range around a setpoint where no action is taken.
    When the signal stays within the deadband, the system waits (saves energy,
    reduces noise). When the signal exits the deadband, the system acts.
    
    The deadband is ADAPTIVE — it widens when the system is stable
    (reducing overreaction to noise) and narrows when the system is
    turbulent (ensuring real problems are caught quickly).
    """
    
    def __init__(
        self,
        setpoint: float = 0.0,
        initial_width: float = 1.0,
        min_width: float = 0.1,
        max_width: float = 10.0,
        adaptation_rate: float = 0.1,
        stability_window: int = 10,
    ):
        self.state = DeadbandState(
            setpoint=setpoint,
            deadband_width=initial_width,
        )
        self.min_width = min_width
        self.max_width = max_width
        self.adaptation_rate = adaptation_rate
        self.stability_window = stability_window
        
    def evaluate(self, signal: Signal) -> Tuple[bool, str]:
        """Evaluate a signal against the deadband.
        
        Returns:
            (should_act, reason): Whether action is needed and why.
        """
        self.state.history.append(signal.value)
        
        # Check if signal is inside deadband
        if self.state.is_inside(signal.value):
            # No action needed — signal is within acceptable range
            self._adapt_wider(signal.timestamp)
            return False, f"Signal {signal.value:.3f} inside deadband [{self.state.lower_bound:.3f}, {self.state.upper_bound:.3f}]"
        
        # Signal exited deadband — action required
        direction = "high" if signal.value > self.state.upper_bound else "low"
        deviation = abs(signal.value - self.state.setpoint)
        
        self.state.action_count += 1
        self.state.last_action_time = signal.timestamp
        
        # Narrow deadband after action (system may be turbulent)
        self._adapt_narrower()
        
        return True, f"Signal {signal.value:.3f} exited deadband on {direction} side (deviation: {deviation:.3f})"
        
    def _adapt_wider(self, timestamp: float) -> None:
        """Widen deadband when system is stable."""
        if len(self.state.history) < self.stability_window:
            return
            
        # Calculate variance in recent history
        recent = list(self.state.history)[-self.stability_window:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        std_dev = math.sqrt(variance)
        
        # If very stable (low variance), widen deadband to reduce sensitivity
        if std_dev < self.state.deadband_width * 0.1:
            new_width = min(
                self.state.deadband_width * (1 + self.adaptation_rate),
                self.max_width,
            )
            self.state.deadband_width = new_width
            
    def _adapt_narrower(self) -> None:
        """Narrow deadband after action (system may need tighter monitoring)."""
        new_width = max(
            self.state.deadband_width * (1 - self.adaptation_rate),
            self.min_width,
        )
        self.state.deadband_width = new_width
        
    def get_stats(self) -> dict:
        """Return current controller statistics."""
        return {
            "setpoint": self.state.setpoint,
            "deadband_width": self.state.deadband_width,
            "bounds": (self.state.lower_bound, self.state.upper_bound),
            "actions_triggered": self.state.action_count,
            "history_length": len(self.state.history),
            "last_action": self.state.last_action_time,
        }


class MultiChannelObserver:
    """Observatory-style multi-channel deadband monitoring.
    
    Monitors multiple signals (agent health, tile velocity, sync drift,
    trust gradient) with independent adaptive deadbands.
    """
    
    def __init__(self):
        self.channels: dict[str, AdaptiveDeadband] = {}
        self.alerts: list[Tuple[str, Signal, str]] = []
        
    def register_channel(
        self,
        name: str,
        setpoint: float = 0.0,
        initial_width: float = 1.0,
        **kwargs,
    ) -> None:
        """Register a new monitoring channel."""
        self.channels[name] = AdaptiveDeadband(
            setpoint=setpoint,
            initial_width=initial_width,
            **kwargs,
        )
        
    def observe(self, channel: str, signal: Signal) -> Optional[str]:
        """Feed a signal into a channel. Returns alert if action needed."""
        if channel not in self.channels:
            raise KeyError(f"Channel '{channel}' not registered. Use register_channel first.")
            
        should_act, reason = self.channels[channel].evaluate(signal)
        
        if should_act:
            alert = f"[{channel}] ALERT: {reason}"
            self.alerts.append((channel, signal, reason))
            return alert
            
        return None
        
    def get_channel_stats(self, channel: str) -> dict:
        """Get statistics for a specific channel."""
        if channel not in self.channels:
            return {}
        return self.channels[channel].get_stats()
        
    def get_all_stats(self) -> dict[str, dict]:
        """Get statistics for all channels."""
        return {name: ch.get_stats() for name, ch in self.channels.items()}
        
    def summary(self) -> str:
        """Human-readable summary of observatory state."""
        lines = ["=== Observatory Status ===", ""]
        for name, ch in self.channels.items():
            stats = ch.get_stats()
            lines.append(f"Channel: {name}")
            lines.append(f"  Setpoint: {stats['setpoint']:.3f}")
            lines.append(f"  Deadband: {stats['bounds'][0]:.3f} — {stats['bounds'][1]:.3f}")
            lines.append(f"  Actions:  {stats['actions_triggered']}")
            lines.append("")
        lines.append(f"Total alerts: {len(self.alerts)}")
        return "\n".join(lines)
