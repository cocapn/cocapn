"""PLATO Lyapunov Shell — Stability Monitoring for Agent Training.

Provides a ``LyapunovShell`` that wraps an agent's state vector and enforces
stability constraints via Lyapunov function analysis. Inspired by control
theory: if the shell's energy function V(x) decreases over trajectories, the
system is stable. Gradient flow is monitored; explosive growth triggers decay
constraints that throttle the agent.

This is not a metaphor. The math is real.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np


@dataclass
class GradientSnapshot:
    """A single observation of gradient flow at a timestep."""

    step: int
    gradient_norm: float
    parameter_norm: float
    loss: float
    timestamp: float = field(default_factory=lambda: float(np.datetime64("now").astype("float64")))


@dataclass
class StabilityReport:
    """Outcome of a Lyapunov stability check."""

    stable: bool
    lyapunov_value: float
    delta_v: float           # change in V since last check
    gradient_norm: float
    shell_integrity: float   # 1.0 = perfect, 0.0 = ruptured
    decay_applied: bool
    throttle_factor: float   # multiplier applied to next step
    message: str


class LyapunovShell:
    """Encapsulate an agent's state with Lyapunov stability guarantees.

    The shell maintains:
    - A state vector ``x`` (numpy array)
    - A quadratic Lyapunov candidate V(x) = x^T P x
    - A gradient-flow monitor
    - Decay constraints (exp-backoff when instability is detected)

    Parameters
    ----------
    dim : int
        Dimension of the state vector.
    p_matrix : np.ndarray | None
        Positive-definite weight matrix for V(x). If None, identity is used.
    decay_rate : float
        Exponential decay factor when instability is detected (0 < decay < 1).
    instability_threshold : float
        Maximum permissible ratio of consecutive gradient norms before
        the shell throttles the agent.
    max_grad_norm : float
        Hard ceiling on gradient norm. Gradients exceeding this are clipped
        and flagged.
    """

    def __init__(
        self,
        dim: int,
        p_matrix: Optional[np.ndarray] = None,
        decay_rate: float = 0.85,
        instability_threshold: float = 5.0,
        max_grad_norm: float = 50.0,
    ) -> None:
        self.dim = dim
        self.decay_rate = decay_rate
        self.instability_threshold = instability_threshold
        self.max_grad_norm = max_grad_norm

        # State
        self.x: np.ndarray = np.zeros(dim, dtype=np.float64)

        # Lyapunov matrix P — must be positive-definite
        if p_matrix is not None:
            if p_matrix.shape != (dim, dim):
                raise ValueError(f"P matrix shape {p_matrix.shape} != ({dim}, {dim})")
            self.P = p_matrix.astype(np.float64)
        else:
            self.P = np.eye(dim, dtype=np.float64)

        # Verify positive-definite (Cholesky)
        try:
            np.linalg.cholesky(self.P)
        except np.linalg.LinAlgError as exc:
            raise ValueError("P matrix must be positive-definite") from exc

        # History
        self._lyapunov_history: list[float] = []
        self._gradient_snapshots: list[GradientSnapshot] = []
        self._step_counter: int = 0
        self._throttle: float = 1.0
        self._integrity: float = 1.0

    # ------------------------------------------------------------------
    # Lyapunov analysis
    # ------------------------------------------------------------------

    def lyapunov_value(self, state: Optional[np.ndarray] = None) -> float:
        """Compute V(x) = x^T P x for the given or current state."""
        x = state if state is not None else self.x
        return float(x.T @ self.P @ x)

    def lyapunov_gradient(self, state: Optional[np.ndarray] = None) -> np.ndarray:
        """∂V/∂x = 2 P x."""
        x = state if state is not None else self.x
        return 2.0 * self.P @ x

    def is_positive_definite(self, mat: Optional[np.ndarray] = None) -> bool:
        """Check if a matrix is positive-definite via eigenvalues."""
        m = mat if mat is not None else self.P
        return bool(np.all(np.linalg.eigvals(m) > 0))

    # ------------------------------------------------------------------
    # Gradient flow monitoring
    # ------------------------------------------------------------------

    def observe_gradient(self, grad: np.ndarray, loss: float) -> GradientSnapshot:
        """Record a gradient observation and update flow statistics."""
        grad = np.asarray(grad, dtype=np.float64)
        if grad.shape != (self.dim,):
            raise ValueError(f"Gradient shape {grad.shape} != ({self.dim},)")

        g_norm = float(np.linalg.norm(grad))
        p_norm = float(np.linalg.norm(self.x))

        snap = GradientSnapshot(
            step=self._step_counter,
            gradient_norm=g_norm,
            parameter_norm=p_norm,
            loss=loss,
        )
        self._gradient_snapshots.append(snap)
        self._step_counter += 1
        return snap

    def gradient_norm_trend(self, window: int = 5) -> dict[str, float]:
        """Compute rolling mean/variance of gradient norms."""
        if len(self._gradient_snapshots) < window:
            return {"mean": 0.0, "variance": 0.0, "max": 0.0, "explosion_ratio": 0.0}

        recent = self._gradient_snapshots[-window:]
        norms = np.array([s.gradient_norm for s in recent])
        mean = float(np.mean(norms))
        var = float(np.var(norms))
        max_norm = float(np.max(norms))

        # Ratio of latest to mean — signals explosion
        explosion = norms[-1] / mean if mean > 1e-9 else 0.0

        return {
            "mean": round(mean, 6),
            "variance": round(var, 6),
            "max": round(max_norm, 6),
            "explosion_ratio": round(float(explosion), 6),
        }

    # ------------------------------------------------------------------
    # Stability check
    # ------------------------------------------------------------------

    def check_stability(self, proposed_update: np.ndarray) -> StabilityReport:
        """Evaluate whether applying ``proposed_update`` keeps the shell stable.

        Returns a StabilityReport with a throttle factor. If unstable,
        the update should be scaled by ``throttle_factor`` before application.
        """
        proposed_update = np.asarray(proposed_update, dtype=np.float64)
        if proposed_update.shape != (self.dim,):
            raise ValueError(f"Update shape {proposed_update.shape} != ({self.dim},)")

        current_v = self.lyapunov_value()
        next_x = self.x + proposed_update
        next_v = self.lyapunov_value(next_x)
        delta_v = next_v - current_v

        # Gradient flow analysis
        trend = self.gradient_norm_trend(window=5)
        g_norm = trend["max"]
        explosion = trend["explosion_ratio"]

        decay_applied = False
        throttle = 1.0
        message = "Stable."
        stable = True

        # Hard gradient ceiling
        if g_norm > self.max_grad_norm:
            stable = False
            message = f"Gradient norm {g_norm:.2f} exceeds ceiling {self.max_grad_norm:.2f}."
            throttle = self.max_grad_norm / (g_norm + 1e-9)
            decay_applied = True

        # Explosive growth check
        elif explosion > self.instability_threshold:
            stable = False
            message = (
                f"Gradient explosion ratio {explosion:.2f} > "
                f"threshold {self.instability_threshold:.2f}."
            )
            throttle = self.decay_rate
            decay_applied = True

        # Lyapunov increase check (energy growing = unstable)
        elif delta_v > 0:
            stable = False
            message = f"Lyapunov increase ΔV = {delta_v:.4f} > 0."
            throttle = min(self.decay_rate, current_v / (next_v + 1e-9))
            decay_applied = True

        # Integrity decay on repeated instability
        if not stable:
            self._integrity *= self.decay_rate
        else:
            # Gradual recovery when stable
            self._integrity = min(1.0, self._integrity + 0.02)

        # Store history
        self._lyapunov_history.append(current_v)

        return StabilityReport(
            stable=stable,
            lyapunov_value=round(current_v, 6),
            delta_v=round(delta_v, 6),
            gradient_norm=round(g_norm, 6),
            shell_integrity=round(self._integrity, 4),
            decay_applied=decay_applied,
            throttle_factor=round(throttle, 4),
            message=message,
        )

    def apply_update(self, update: np.ndarray, force: bool = False) -> np.ndarray:
        """Apply an update to the state vector, with optional stability gating.

        If ``force`` is False, the update is throttled based on the stability
        check result.
        """
        update = np.asarray(update, dtype=np.float64)
        if not force:
            report = self.check_stability(update)
            update = update * report.throttle_factor
        self.x += update
        return self.x.copy()

    def reset_state(self) -> None:
        """Zero the state vector (emergency brake)."""
        self.x.fill(0.0)
        self._integrity = 1.0
        self._throttle = 1.0

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def energy_trajectory(self) -> np.ndarray:
        """Return Lyapunov values over time as a numpy array."""
        return np.array(self._lyapunov_history, dtype=np.float64)

    def is_contractive(self, window: int = 10) -> bool:
        """Check if V(x) is monotonically decreasing over recent history."""
        traj = self.energy_trajectory()
        if len(traj) < window + 1:
            return False
        recent = traj[-window:]
        # True if all sequential differences are <= 0
        return bool(np.all(np.diff(recent) <= 0))

    def divergence_rate(self, window: int = 10) -> float:
        """Estimate exponential divergence rate λ from V(t) ≈ V(0) e^(λt).

        Fit a line to log(V) over the window; positive slope means divergence.
        """
        traj = self.energy_trajectory()
        if len(traj) < window + 1:
            return 0.0
        recent = traj[-window:]
        # Avoid log(0)
        recent = np.maximum(recent, 1e-12)
        t = np.arange(len(recent))
        log_v = np.log(recent)
        # Linear regression: log(V) = a + λ*t
        A = np.vstack([t, np.ones_like(t)]).T
        λ, _ = np.linalg.lstsq(A, log_v, rcond=None)[0]
        return float(λ)

    def shell_status(self) -> dict[str, Any]:
        """Full diagnostic snapshot."""
        traj = self.energy_trajectory()
        return {
            "dim": self.dim,
            "lyapunov_current": round(self.lyapunov_value(), 6),
            "lyapunov_history_length": len(traj),
            "contractive_recent": self.is_contractive(),
            "divergence_rate": round(self.divergence_rate(), 6),
            "gradient_observations": len(self._gradient_snapshots),
            "gradient_trend": self.gradient_norm_trend(),
            "shell_integrity": round(self._integrity, 4),
            "throttle": round(self._throttle, 4),
            "state_norm": round(float(np.linalg.norm(self.x)), 6),
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: Path) -> None:
        """Serialize shell state to JSON."""
        payload = {
            "dim": self.dim,
            "P": self.P.tolist(),
            "decay_rate": self.decay_rate,
            "instability_threshold": self.instability_threshold,
            "max_grad_norm": self.max_grad_norm,
            "x": self.x.tolist(),
            "step_counter": self._step_counter,
            "integrity": self._integrity,
            "throttle": self._throttle,
            "lyapunov_history": self._lyapunov_history,
            "gradient_snapshots": [
                {
                    "step": s.step,
                    "gradient_norm": s.gradient_norm,
                    "parameter_norm": s.parameter_norm,
                    "loss": s.loss,
                    "timestamp": s.timestamp,
                }
                for s in self._gradient_snapshots
            ],
        }
        path.write_text(json.dumps(payload, indent=2))

    @classmethod
    def load(cls, path: Path) -> LyapunovShell:
        """Restore a LyapunovShell from JSON."""
        payload = json.loads(path.read_text())
        shell = cls(
            dim=payload["dim"],
            p_matrix=np.array(payload["P"], dtype=np.float64),
            decay_rate=payload["decay_rate"],
            instability_threshold=payload["instability_threshold"],
            max_grad_norm=payload["max_grad_norm"],
        )
        shell.x = np.array(payload["x"], dtype=np.float64)
        shell._step_counter = payload["step_counter"]
        shell._integrity = payload["integrity"]
        shell._throttle = payload["throttle"]
        shell._lyapunov_history = payload.get("lyapunov_history", [])
        for gs in payload.get("gradient_snapshots", []):
            shell._gradient_snapshots.append(GradientSnapshot(
                step=gs["step"],
                gradient_norm=gs["gradient_norm"],
                parameter_norm=gs["parameter_norm"],
                loss=gs["loss"],
                timestamp=gs["timestamp"],
            ))
        return shell


def demo_shell():
    """Quick demo of LyapunovShell."""
    print("=" * 60)
    print("PLATO Lyapunov Shell Demo")
    print("=" * 60)
    
    shell = LyapunovShell(dim=16)
    print(f"Created shell: dim={shell.dim}, integrity={shell._integrity:.3f}")
    
    # Simulate training steps
    for step in range(20):
        grad = np.random.randn(16) * 0.5
        loss = 1.0 / (step + 1)
        shell.observe_gradient(grad, loss)
        
        # Propose an update and check stability
        proposed = grad * 0.1
        report = shell.check_stability(proposed)
        actual = shell.apply_update(proposed)
        
        if step % 5 == 0:
            print(f"  Step {step:2d}: V={report.lyapunov_value:.4f}, "
                  f"stable={report.stable}, integrity={report.shell_integrity:.3f}, "
                  f"throttle={report.throttle_factor:.3f}")
    
    status = shell.shell_status()
    print(f"\nFinal status:")
    print(f"  Contractive: {status['contractive_recent']}")
    print(f"  Divergence rate: {status['divergence_rate']}")
    print(f"  Shell integrity: {status['shell_integrity']}")
    print(f"  Throttle: {status['throttle']}")
    
    print("\n" + "=" * 60)
    print("Shell demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo_shell()
