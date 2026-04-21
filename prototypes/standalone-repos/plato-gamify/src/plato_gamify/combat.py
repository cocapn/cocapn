"""Combat system — decision tree optimization disguised as battle."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
import numpy as np

from .dice import DicePool, ReasoningRoll


@dataclass
class CombatOutcome:
    """Result of a combat encounter."""
    winner: Optional[str]
    loser: Optional[str]
    rounds: int
    final_state_a: dict
    final_state_b: dict
    decision_path: List[str] = field(default_factory=list)
    confidence_trajectory: List[float] = field(default_factory=list)


@dataclass
class DecisionNode:
    """A node in the combat decision tree."""
    feature: str
    threshold: float
    left: Optional['DecisionNode'] = None  # <= threshold
    right: Optional['DecisionNode'] = None  # > threshold
    value: Optional[float] = None  # Leaf node value
    
    def evaluate(self, state: dict) -> float:
        """Evaluate decision tree for given state."""
        if self.value is not None:
            return self.value
        
        feature_value = state.get(self.feature, 0)
        if feature_value <= self.threshold:
            return self.left.evaluate(state) if self.left else 0
        else:
            return self.right.evaluate(state) if self.right else 1


class DecisionTree:
    """Decision tree for combat resolution."""
    
    def __init__(self, features: List[str], strategy: str = "minimax", depth: int = 5):
        self.features = features
        self.strategy = strategy
        self.depth = depth
        self.tree: Optional[DecisionNode] = None
        self._build_tree()
    
    def _build_tree(self):
        """Build a simple decision tree."""
        # Build balanced tree with random thresholds
        self.tree = self._build_node(self.features, self.depth)
    
    def _build_node(self, features: List[str], depth: int) -> DecisionNode:
        """Recursively build tree node."""
        if depth == 0 or not features:
            return DecisionNode(
                feature="",
                threshold=0,
                value=np.random.random(),
            )
        
        feature = features[depth % len(features)]
        threshold = np.random.random() * 0.5 + 0.25  # 0.25 to 0.75
        
        return DecisionNode(
            feature=feature,
            threshold=threshold,
            left=self._build_node(features, depth - 1),
            right=self._build_node(features, depth - 1),
        )
    
    def predict(self, state: dict) -> float:
        """Predict combat outcome for given state."""
        if not self.tree:
            return 0.5
        return self.tree.evaluate(state)
    
    def minimax(self, state: dict, is_maximizing: bool, 
                depth: int = None) -> float:
        """Minimax strategy for combat."""
        if depth is None:
            depth = self.depth
        
        if depth == 0:
            return self.predict(state)
        
        if is_maximizing:
            value = float('-inf')
            # Try different actions
            for action in ["attack", "defend", "spell"]:
                new_state = self._apply_action(state, action)
                eval = self.minimax(new_state, False, depth - 1)
                value = max(value, eval)
            return value
        else:
            value = float('inf')
            for action in ["attack", "defend", "spell"]:
                new_state = self._apply_action(state, action)
                eval = self.minimax(new_state, True, depth - 1)
                value = min(value, eval)
            return value
    
    def _apply_action(self, state: dict, action: str) -> dict:
        """Apply action to state."""
        new_state = state.copy()
        
        if action == "attack":
            new_state["confidence"] = state.get("confidence", 0) + 0.1
        elif action == "defend":
            new_state["robustness"] = state.get("robustness", 0) + 0.15
        elif action == "spell":
            new_state["mana"] = state.get("mana", 0) - 5
            new_state["confidence"] = state.get("confidence", 0) + 0.2
        
        return new_state
    
    def get_best_action(self, state: dict) -> str:
        """Get best action using minimax."""
        actions = ["attack", "defend", "spell"]
        best_action = actions[0]
        best_value = float('-inf')
        
        for action in actions:
            new_state = self._apply_action(state, action)
            value = self.minimax(new_state, False, self.depth - 1)
            if value > best_value:
                best_value = value
                best_action = action
        
        return best_action


class Combat:
    """Combat encounter between two agents."""
    
    def __init__(self, attacker: dict, defender: dict, 
                 resolution: Optional[DecisionTree] = None):
        self.attacker = attacker
        self.defender = defender
        self.resolution = resolution or DecisionTree(
            features=["confidence", "robustness", "mana"],
            strategy="minimax",
            depth=3,
        )
        self.rounds = 0
        self.max_rounds = 20
        self.decision_path = []
        self.confidence_trajectory = []
    
    def fight(self) -> CombatOutcome:
        """Resolve combat encounter."""
        state_a = self.attacker.copy()
        state_b = self.defender.copy()
        
        while self.rounds < self.max_rounds:
            self.rounds += 1
            
            # Attacker's turn
            action_a = self.resolution.get_best_action(state_a)
            self.decision_path.append(f"A:{action_a}")
            state_a = self.resolution._apply_action(state_a, action_a)
            
            # Check if defender defeated
            if self._is_defeated(state_b, state_a):
                return self._create_outcome("attacker", state_a, state_b)
            
            # Defender's turn
            action_b = self.resolution.get_best_action(state_b)
            self.decision_path.append(f"D:{action_b}")
            state_b = self.resolution._apply_action(state_b, action_b)
            
            # Check if attacker defeated
            if self._is_defeated(state_a, state_b):
                return self._create_outcome("defender", state_a, state_b)
            
            # Track confidence
            avg_confidence = (state_a.get("confidence", 0) + 
                             state_b.get("confidence", 0)) / 2
            self.confidence_trajectory.append(avg_confidence)
        
        # Timeout — evaluate final states
        score_a = self._score_state(state_a)
        score_b = self._score_state(state_b)
        
        if score_a > score_b:
            return self._create_outcome("attacker", state_a, state_b)
        elif score_b > score_a:
            return self._create_outcome("defender", state_a, state_b)
        else:
            return self._create_outcome(None, state_a, state_b)  # Draw
    
    def _is_defeated(self, target: dict, attacker: dict) -> bool:
        """Check if target is defeated."""
        # Defeated if confidence drops below threshold or mana exhausted
        return (target.get("confidence", 1.0) < 0.1 or 
                target.get("mana", 100) < 0)
    
    def _score_state(self, state: dict) -> float:
        """Score agent state for tiebreaking."""
        return (
            state.get("confidence", 0) * 0.4 +
            state.get("robustness", 0) * 0.3 +
            state.get("mana", 0) / 100 * 0.2 +
            state.get("tiles", 0) / 100 * 0.1
        )
    
    def _create_outcome(self, winner: Optional[str], 
                        state_a: dict, state_b: dict) -> CombatOutcome:
        """Create combat outcome."""
        return CombatOutcome(
            winner="attacker" if winner == "attacker" else 
                   "defender" if winner == "defender" else None,
            loser="defender" if winner == "attacker" else 
                  "attacker" if winner == "defender" else None,
            rounds=self.rounds,
            final_state_a=state_a,
            final_state_b=state_b,
            decision_path=self.decision_path,
            confidence_trajectory=self.confidence_trajectory,
        )
