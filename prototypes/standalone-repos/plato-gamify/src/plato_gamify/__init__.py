"""Plato Gamify — Gamification layer for PLATO MUD."""

from .spells import Spell, SpellBook, StochasticBoost
from .items import Item, Inventory, Tile
from .armor import Armor, ToleranceConstraint, LyapunovShell
from .combat import Combat, DecisionTree, CombatOutcome
from .dice import DicePool, ReasoningRoll, DiceEntropy
from .constraints import PythagoreanConstraint, ToleranceBound
from .agent import GamifiedAgent, AgentState
from .mud_bridge import MUDBridge

__version__ = "0.1.0"
__all__ = [
    "Spell", "SpellBook", "StochasticBoost",
    "Item", "Inventory", "Tile",
    "Armor", "ToleranceConstraint", "LyapunovShell",
    "Combat", "DecisionTree", "CombatOutcome",
    "DicePool", "ReasoningRoll", "DiceEntropy",
    "PythagoreanConstraint", "ToleranceBound",
    "GamifiedAgent", "AgentState",
    "MUDBridge",
]
