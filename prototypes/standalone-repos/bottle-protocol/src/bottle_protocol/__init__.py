"""Bottle Protocol — Git-native agent-to-agent messaging."""
__version__ = "0.1.0"
from .core import Bottle, BottleProtocol, FleetPostOffice
__all__ = ["Bottle", "BottleProtocol", "FleetPostOffice"]
