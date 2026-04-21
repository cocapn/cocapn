"""Dice system — stochastic reasoning via polyhedral dice."""

import random
import math
from dataclasses import dataclass
from typing import Dict, List
import numpy as np


@dataclass
class ReasoningRoll:
    """Result of a dice roll — represents a reasoning step."""
    outcome: int
    confidence: float  # 0.0 to 1.0
    entropy: float     # Uncertainty measure
    
    def is_critical_success(self) -> bool:
        """Check if roll was a critical success (max outcome)."""
        return self.confidence > 0.95
    
    def is_critical_failure(self) -> bool:
        """Check if roll was a critical failure (min outcome)."""
        return self.confidence < 0.05


class DicePool:
    """A pool of dice for stochastic reasoning."""
    
    def __init__(self, **kwargs):
        """Initialize dice pool.
        
        Examples:
            DicePool(d6=3)  # 3 six-sided dice
            DicePool(d20=1, modifier=+3)  # 1d20 + 3
            DicePool(d6=4, keep_highest=3)  # Roll 4d6, keep 3
        """
        self.dice: Dict[int, int] = {}  # sides -> count
        self.modifier: int = 0
        self.keep_highest: Optional[int] = None
        
        for key, value in kwargs.items():
            if key == "modifier":
                self.modifier = value
            elif key == "keep_highest":
                self.keep_highest = value
            elif key.startswith("d"):
                sides = int(key[1:])
                self.dice[sides] = value
    
    def roll(self) -> int:
        """Roll the dice pool."""
        results = []
        
        for sides, count in self.dice.items():
            for _ in range(count):
                results.append(random.randint(1, sides))
        
        # Keep highest if specified
        if self.keep_highest and len(results) > self.keep_highest:
            results = sorted(results, reverse=True)[:self.keep_highest]
        
        return sum(results) + self.modifier
    
    def max_outcome(self) -> int:
        """Compute maximum possible outcome."""
        total = sum(sides * count for sides, count in self.dice.items())
        if self.keep_highest:
            # Approximate — actual max depends on dice combination
            total = sum(sorted([sides] * count, reverse=True)[:self.keep_highest]
                       for sides, count in self.dice.items())
        return total + self.modifier
    
    def min_outcome(self) -> int:
        """Compute minimum possible outcome."""
        count = sum(self.dice.values())
        if self.keep_highest:
            count = self.keep_highest
        return count + self.modifier
    
    def entropy(self) -> float:
        """Compute Shannon entropy of the dice distribution."""
        # Simplified: entropy based on number of possible outcomes
        outcomes = self.max_outcome() - self.min_outcome() + 1
        # Approximate entropy for uniform-like dice distribution
        if outcomes <= 1:
            return 0.0
        return math.log2(outcomes)
    
    def expected_value(self) -> float:
        """Compute expected value of the dice pool."""
        expected = 0.0
        for sides, count in self.dice.items():
            expected += count * (sides + 1) / 2
        return expected + self.modifier
    
    def variance(self) -> float:
        """Compute variance of the dice pool."""
        var = 0.0
        for sides, count in self.dice.items():
            # Variance of single die: (n^2 - 1) / 12
            var += count * (sides**2 - 1) / 12
        return var
    
    def __repr__(self) -> str:
        parts = []
        for sides, count in sorted(self.dice.items()):
            parts.append(f"{count}d{sides}")
        if self.modifier > 0:
            parts.append(f"+{self.modifier}")
        elif self.modifier < 0:
            parts.append(f"{self.modifier}")
        if self.keep_highest:
            parts.append(f"keep_highest_{self.keep_highest}")
        return " ".join(parts)


class DiceEntropy:
    """Track entropy over multiple rolls to measure reasoning confidence."""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.rolls: List[ReasoningRoll] = []
    
    def add(self, roll: ReasoningRoll):
        """Add a roll to the history."""
        self.rolls.append(roll)
        if len(self.rolls) > self.window_size:
            self.rolls.pop(0)
    
    def mean_confidence(self) -> float:
        """Average confidence over recent rolls."""
        if not self.rolls:
            return 0.5
        return np.mean([r.confidence for r in self.rolls])
    
    def mean_entropy(self) -> float:
        """Average entropy over recent rolls."""
        if not self.rolls:
            return 1.0
        return np.mean([r.entropy for r in self.rolls])
    
    def trend(self) -> str:
        """Determine if confidence is improving or declining."""
        if len(self.rolls) < 3:
            return "insufficient_data"
        
        recent = [r.confidence for r in self.rolls[-3:]]
        if recent[-1] > recent[0]:
            return "improving"
        elif recent[-1] < recent[0]:
            return "declining"
        else:
            return "stable"
    
    def should_seek_context(self) -> bool:
        """Determine if agent should seek more context."""
        return self.mean_entropy() > 2.0 or self.mean_confidence() < 0.4
