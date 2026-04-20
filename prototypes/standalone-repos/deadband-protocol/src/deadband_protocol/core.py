"""Safety validation with priority-ordered constraint checking."""
from enum import Enum
from typing import Any, Callable, List, Optional
from dataclasses import dataclass


class Priority(Enum):
    P0 = "P0"  # Critical safety
    P1 = "P1"  # Operational safety
    P2 = "P2"  # Optimization


@dataclass
class ValidationResult:
    passed: bool
    priority: Priority
    reason: str
    suggestion: Optional[str] = None


class SafetyGate:
    """A single safety check."""
    def __init__(self, name: str, check: Callable[[Any], bool], priority: Priority, reason: str):
        self.name = name
        self.check = check
        self.priority = priority
        self.reason = reason


class Deadband:
    """Priority-ordered safety validator."""
    def __init__(self):
        self._gates: List[SafetyGate] = []
        
    def add_gate(self, gate: SafetyGate) -> None:
        self._gates.append(gate)
        # Sort by priority: P0 first
        self._gates.sort(key=lambda g: (g.priority.value, g.name))
        
    def validate(self, data: Any) -> List[ValidationResult]:
        results = []
        for gate in self._gates:
            passed = gate.check(data)
            results.append(ValidationResult(
                passed=passed,
                priority=gate.priority,
                reason=gate.reason if passed else f"FAILED: {gate.reason}",
                suggestion=None if passed else f"Fix {gate.name}"
            ))
            # P0 failures are fatal
            if not passed and gate.priority == Priority.P0:
                break
        return results
    
    def is_safe(self, data: Any) -> bool:
        return all(r.passed for r in self.validate(data))
