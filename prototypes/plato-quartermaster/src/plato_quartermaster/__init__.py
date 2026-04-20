"""
plato-quartermaster: The Vagus Nerve of the Fleet

The Quartermaster is the gut-brain axis — the second brain that handles
metabolism, proprioception, and reflexes without bothering the cortex.

It reads everything flowing through the system, decides what to keep,
what to digest, what to evacuate, and signals hunger upstream.
"""

__version__ = "0.1.0"

from .quartermaster import Quartermaster, TranscendenceLevel, SystemVitals, DigestionTask
from .selftrain import SelfTrainingPipeline, DecisionRecord
from .reflex import ReflexArc, ReflexType, reflex_registry, register_reflex, check_all_reflexes
from .homunculus import FleetHomunculus, Vessel, VesselStatus, PainSignal

__all__ = [
    "Quartermaster",
    "TranscendenceLevel",
    "SystemVitals", 
    "DigestionTask",
    "SelfTrainingPipeline",
    "DecisionRecord",
    "ReflexArc",
    "ReflexType",
    "reflex_registry",
    "register_reflex",
    "check_all_reflexes",
    "FleetHomunculus",
    "Vessel",
    "VesselStatus",
    "PainSignal",
]
