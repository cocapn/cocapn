"""Spell system — spells as stochastic reasoning operations."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
import numpy as np

from .dice import DicePool, ReasoningRoll


@dataclass
class SpellCost:
    """Resource cost for casting a spell."""
    mana: int = 0
    tokens: int = 0
    tiles: int = 0
    compute: float = 0.0  # FLOPs estimate


@dataclass
class SpellEffect:
    """Effect of a spell — modifies agent state or environment."""
    target: str  # What state to modify
    delta: float  # How much to change
    duration: int = 1  # Turns/effective duration
    decay: float = 1.0  # 1.0 = permanent, <1.0 = decaying


@dataclass
class StochasticBoost:
    """Confidence boost from stochastic reasoning (dice roll)."""
    base_confidence: float
    dice: DicePool
    tolerance: float = 0.1
    
    def roll(self) -> ReasoningRoll:
        """Roll the dice and compute confidence interval."""
        outcome = self.dice.roll()
        
        # Confidence is scaled by dice outcome
        max_outcome = self.dice.max_outcome()
        confidence = min(1.0, self.base_confidence + 
                          (outcome / max_outcome) * self.tolerance)
        
        return ReasoningRoll(
            outcome=outcome,
            confidence=confidence,
            entropy=self.dice.entropy(),
        )


@dataclass
class Spell:
    """A spell — an algorithmic operation disguised as magic."""
    name: str
    description: str = ""
    cost: SpellCost = field(default_factory=SpellCost)
    effect: Optional[SpellEffect] = None
    boost: Optional[StochasticBoost] = None
    
    # Spell categories map to ML operations
    category: str = "general"  # attention, optimization, inference, memory
    
    def cast(self, caster_state: dict, target_state: Optional[dict] = None) -> dict:
        """Cast the spell — returns modified state."""
        result = {
            "spell": self.name,
            "success": True,
            "cost_paid": False,
            "effects": [],
            "reasoning": None,
        }
        
        # Check if caster can afford
        if not self._can_afford(caster_state):
            result["success"] = False
            result["reason"] = "insufficient_resources"
            return result
        
        # Pay cost
        self._pay_cost(caster_state)
        result["cost_paid"] = True
        
        # Apply stochastic boost if present
        if self.boost:
            reasoning = self.boost.roll()
            result["reasoning"] = reasoning
            
            # Boost modifies the effect magnitude
            if self.effect:
                self.effect.delta *= reasoning.confidence
        
        # Apply effect
        if self.effect:
            modified = self._apply_effect(caster_state, target_state)
            result["effects"].append(modified)
        
        return result
    
    def _can_afford(self, state: dict) -> bool:
        """Check if caster has sufficient resources."""
        return (
            state.get("mana", 0) >= self.cost.mana and
            state.get("tokens", 0) >= self.cost.tokens and
            state.get("tiles", 0) >= self.cost.tiles
        )
    
    def _pay_cost(self, state: dict):
        """Deduct spell cost from caster."""
        state["mana"] = state.get("mana", 0) - self.cost.mana
        state["tokens"] = state.get("tokens", 0) - self.cost.tokens
        state["tiles"] = state.get("tiles", 0) - self.cost.tiles
    
    def _apply_effect(self, caster: dict, target: Optional[dict]) -> dict:
        """Apply spell effect to target state."""
        if not self.effect:
            return {}
        
        state = target if target else caster
        current = state.get(self.effect.target, 0)
        state[self.effect.target] = current + self.effect.delta
        
        return {
            "target": self.effect.target,
            "delta": self.effect.delta,
            "new_value": state[self.effect.target],
            "duration": self.effect.duration,
        }


class SpellBook:
    """Collection of spells known to an agent."""
    
    def __init__(self):
        self.spells: Dict[str, Spell] = {}
        self._register_default_spells()
    
    def _register_default_spells(self):
        """Register the default PLATO spell set."""
        # Attention spells
        self.add(Spell(
            name="attention_focus",
            description="Sharpen attention on a single target",
            cost=SpellCost(mana=5, tokens=20),
            effect=SpellEffect(target="attention_weight", delta=0.3, duration=3),
            category="attention",
            boost=StochasticBoost(
                base_confidence=0.6,
                dice=DicePool(d6=2),
                tolerance=0.15,
            ),
        ))
        
        # Optimization spells
        self.add(Spell(
            name="gradient_blast",
            description="Rapid gradient descent with high variance",
            cost=SpellCost(mana=10, tokens=50, compute=1e9),
            effect=SpellEffect(target="learning_rate", delta=0.5, duration=1),
            category="optimization",
            boost=StochasticBoost(
                base_confidence=0.5,
                dice=DicePool(d6=3, keep_highest=2),
                tolerance=0.2,
            ),
        ))
        
        # Inference spells
        self.add(Spell(
            name="confidence_surge",
            description="Boost prediction confidence temporarily",
            cost=SpellCost(mana=8, tokens=30),
            effect=SpellEffect(target="confidence", delta=0.25, duration=2),
            category="inference",
            boost=StochasticBoost(
                base_confidence=0.7,
                dice=DicePool(d8=1, d6=1),
                tolerance=0.1,
            ),
        ))
        
        # Memory spells
        self.add(Spell(
            name="tile_recall",
            description="Retrieve a tile from memory with perfect accuracy",
            cost=SpellCost(mana=3, tiles=1),
            effect=SpellEffect(target="memory_accuracy", delta=0.4, duration=1),
            category="memory",
        ))
        
        # Robustness spells
        self.add(Spell(
            name="lyapunov_shield",
            description="Stabilize against gradient explosion",
            cost=SpellCost(mana=15, tokens=40),
            effect=SpellEffect(target="gradient_norm", delta=-0.5, duration=5),
            category="robustness",
            boost=StochasticBoost(
                base_confidence=0.8,
                dice=DicePool(d4=2),
                tolerance=0.05,
            ),
        ))
    
    def add(self, spell: Spell):
        """Add a spell to the book."""
        self.spells[spell.name] = spell
    
    def get(self, name: str) -> Optional[Spell]:
        """Get a spell by name."""
        return self.spells.get(name)
    
    def list_by_category(self, category: str) -> List[Spell]:
        """List spells in a category."""
        return [s for s in self.spells.values() if s.category == category]
    
    def cast(self, name: str, caster_state: dict, 
             target_state: Optional[dict] = None) -> dict:
        """Cast a spell by name."""
        spell = self.get(name)
        if not spell:
            return {"success": False, "reason": "spell_not_found"}
        return spell.cast(caster_state, target_state)
