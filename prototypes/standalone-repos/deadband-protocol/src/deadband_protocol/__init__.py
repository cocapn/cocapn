"""Deadband Protocol — Adaptive thresholds for when to act vs. when to wait."""
__version__ = "0.1.0"
from .core import AdaptiveDeadband, MultiChannelObserver, Signal, DeadbandState

__all__ = ["AdaptiveDeadband", "MultiChannelObserver", "Signal", "DeadbandState"]
