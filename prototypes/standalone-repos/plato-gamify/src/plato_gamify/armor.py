"""Armor system — robustness constraints as protective gear."""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np


@dataclass
class ToleranceConstraint:
    """A tolerance-based constraint on agent state."""
    metric: str           # What to constrain (gradient_norm, loss, etc.)
    threshold: float      # Maximum allowed value
    decay: float = 1.0    # Decay factor (<1 = shrinking bound)
    
    def check(self, value: float) -> bool:
        """Check if value is within tolerance."""
        return abs(value) <= self.threshold
    
    def project(self, value: float) -> float:
        """Project value onto constraint boundary if violated."""
        if self.check(value):
            return value
        # Project onto hypersphere boundary
        return np.sign(value) * self.threshold
    
    def step(self):
        """Apply decay to threshold."""
        self.threshold *= self.decay


@dataclass
class ArmorPiece:
    """A piece of armor providing one or more constraints."""
    name: str
    slot: str  # head, body, hands, feet
    constraints: List[ToleranceConstraint] = field(default_factory=list)
    weight: float = 1.0  # How much it affects agent speed
    
    def check_state(self, state: dict) -> List[str]:
        """Check which constraints are violated."""
        violations = []
        for c in self.constraints:
            value = state.get(c.metric, 0)
            if not c.check(value):
                violations.append(c.metric)
        return violations
    
    def protect(self, state: dict) -> dict:
        """Apply protection — project violated values onto boundaries."""
        protected = state.copy()
        for c in self.constraints:
            value = protected.get(c.metric, 0)
            protected[c.metric] = c.project(value)
        return protected


class LyapunovShell(ArmorPiece):
    """Specialized armor using Lyapunov stability principles."""
    
    def __init__(self, stability_margin: float = 0.1):
        super().__init__(
            name="lyapunov_shell",
            slot="body",
            constraints=[
                ToleranceConstraint(
                    metric="gradient_norm",
                    threshold=1.0,
                    decay=0.95,
                ),
                ToleranceConstraint(
                    metric="loss_spike",
                    threshold=2.0,
                    decay=0.90,
                ),
                ToleranceConstraint(
                    metric="weight_change",
                    threshold=0.5,
                    decay=0.98,
                ),
            ],
            weight=2.0,
        )
        self.stability_margin = stability_margin
    
    def lyapunov_function(self, state: dict) -> float:
        """Compute Lyapunov stability function V(x)."""
        # V(x) = sum of squared constraint violations
        v = 0.0
        for c in self.constraints:
            value = state.get(c.metric, 0)
            if not c.check(value):
                v += (abs(value) - c.threshold) ** 2
        return v
    
    def is_stable(self, state: dict) -> bool:
        """Check if agent state is Lyapunov stable."""
        return self.lyapunov_function(state) < self.stability_margin


class ArmorSet:
    """Complete armor set for an agent."""
    
    def __init__(self):
        self.pieces: dict = {}  # slot -> ArmorPiece
    
    def equip(self, piece: ArmorPiece):
        """Equip an armor piece."""
        self.pieces[piece.slot] = piece
    
    def unequip(self, slot: str):
        """Remove armor from a slot."""
        if slot in self.pieces:
            del self.pieces[slot]
    
    def get_all_constraints(self) -> List[ToleranceConstraint]:
        """Get all constraints from all equipped pieces."""
        constraints = []
        for piece in self.pieces.values():
            constraints.extend(piece.constraints)
        return constraints
    
    def total_weight(self) -> float:
        """Compute total armor weight."""
        return sum(p.weight for p in self.pieces.values())
    
    def check_state(self, state: dict) -> dict:
        """Check state against all armor constraints."""
        violations = {}
        for piece in self.pieces.values():
            piece_violations = piece.check_state(state)
            if piece_violations:
                violations[piece.name] = piece_violations
        return violations
    
    def protect(self, state: dict) -> dict:
        """Apply all armor protection to state."""
        protected = state.copy()
        for piece in self.pieces.values():
            protected = piece.protect(protected)
        return protected
