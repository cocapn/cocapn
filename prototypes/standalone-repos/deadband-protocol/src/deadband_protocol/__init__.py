"""Deadband Protocol — Safety validation for AI outputs."""
__version__ = "0.1.0"
from .core import Deadband, Priority, SafetyGate
__all__ = ["Deadband", "Priority", "SafetyGate"]
