"""Constraint system — Pythagorean and tolerance-based bounds."""

import math
from typing import List, Dict
import numpy as np


class PythagoreanConstraint:
    """Actions constrained to a hypersphere (Pythagorean theorem in N dimensions)."""
    
    def __init__(self, dimensions: List[str], radius: float = 1.0):
        self.dimensions = dimensions
        self.radius = radius
        self.center = {d: 0.0 for d in dimensions}
    
    def distance(self, point: Dict[str, float]) -> float:
        """Compute Euclidean distance from center."""
        return math.sqrt(sum(
            (point.get(d, 0) - self.center[d]) ** 2
            for d in self.dimensions
        ))
    
    def fits(self, point: Dict[str, float]) -> bool:
        """Check if point is within hypersphere."""
        return self.distance(point) <= self.radius
    
    def snap_to_surface(self, point: Dict[str, float]) -> Dict[str, float]:
        """Project point onto hypersphere boundary."""
        dist = self.distance(point)
        if dist == 0:
            # Random point on surface
            direction = {d: np.random.random() - 0.5 for d in self.dimensions}
            return self.snap_to_surface(direction)
        
        scale = self.radius / dist
        return {
            d: self.center[d] + (point.get(d, 0) - self.center[d]) * scale
            for d in self.dimensions
        }
    
    def random_point_on_surface(self) -> Dict[str, float]:
        """Generate random point on hypersphere surface."""
        # Sample from normal distribution, then normalize
        raw = {d: np.random.normal() for d in self.dimensions}
        dist = math.sqrt(sum(v ** 2 for v in raw.values()))
        
        return {
            d: self.center[d] + (v / dist) * self.radius
            for d, v in raw.items()
        }


class ToleranceBound:
    """Axis-aligned bounding box constraints."""
    
    def __init__(self, bounds: Dict[str, tuple]):
        """Initialize with dimension bounds.
        
        Example:
            ToleranceBound({
                "confidence": (0.0, 1.0),
                "speed": (0.0, 10.0),
                "cost": (0.0, 100.0),
            })
        """
        self.bounds = bounds
    
    def check(self, point: Dict[str, float]) -> bool:
        """Check if point is within all bounds."""
        for dim, (low, high) in self.bounds.items():
            value = point.get(dim, 0)
            if value < low or value > high:
                return False
        return True
    
    def clamp(self, point: Dict[str, float]) -> Dict[str, float]:
        """Clamp point to within bounds."""
        clamped = point.copy()
        for dim, (low, high) in self.bounds.items():
            value = point.get(dim, 0)
            clamped[dim] = max(low, min(high, value))
        return clamped
    
    def volume(self) -> float:
        """Compute volume of bounding box."""
        volume = 1.0
        for low, high in self.bounds.values():
            volume *= (high - low)
        return volume
    
    def is_point_inside(self, point: Dict[str, float]) -> bool:
        """Check if point is strictly inside (not on boundary)."""
        for dim, (low, high) in self.bounds.items():
            value = point.get(dim, 0)
            if value <= low or value >= high:
                return False
        return True


class ConstraintSet:
    """Multiple constraints combined."""
    
    def __init__(self):
        self.pythagorean: List[PythagoreanConstraint] = []
        self.tolerance: List[ToleranceBound] = []
    
    def add_pythagorean(self, dimensions: List[str], radius: float = 1.0):
        """Add Pythagorean constraint."""
        self.pythagorean.append(PythagoreanConstraint(dimensions, radius))
    
    def add_tolerance(self, bounds: Dict[str, tuple]):
        """Add tolerance bound."""
        self.tolerance.append(ToleranceBound(bounds))
    
    def check(self, point: Dict[str, float]) -> bool:
        """Check if point satisfies all constraints."""
        for p in self.pythagorean:
            if not p.fits(point):
                return False
        for t in self.tolerance:
            if not t.check(point):
                return False
        return True
    
    def project(self, point: Dict[str, float]) -> Dict[str, float]:
        """Project point to satisfy all constraints."""
        projected = point.copy()
        
        # Apply tolerance bounds first (cheap)
        for t in self.tolerance:
            projected = t.clamp(projected)
        
        # Apply Pythagorean constraints (more expensive)
        for p in self.pythagorean:
            if not p.fits(projected):
                projected = p.snap_to_surface(projected)
        
        return projected
