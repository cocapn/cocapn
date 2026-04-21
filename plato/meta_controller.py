"""
PLATO Meta-Controller
Connects all fleet components into a recursive learning system.

From deepseek experiments (Recursor-0, DeepRecursor):
The meta-controller reads signals from all subsystems and adjusts their
hyperparameters based on fleet-wide dynamics.

Signals:
- Curriculum progress → Arena difficulty scaling
- Shell stability → NAS mutation rate throttling  
- Federated convergence → Artifact generation priority
- Arena ELO distribution → Curriculum advancement thresholds
"""
import json
import random
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pathlib import Path

@dataclass
class MetaSignal:
    """A signal from one subsystem to the meta-controller."""
    subsystem: str  # arena, federated, nas, curriculum, shell
    metric: str
    value: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PlatoMetaController:
    """
    The Recursor-0 from PLATO's Crowsnest.
    
    Watches all subsystems and maintains a cross-component
    equilibrium. If one subsystem is struggling, others adapt.
    
    Control loops:
    1. Arena difficulty ∝ Curriculum stage progression rate
    2. NAS mutation rate ∝ Shell stability (lower stability = more conservative)
    3. Federated learning rate ∝ Arena ELO variance (high variance = need more consensus)
    4. Curriculum threshold ∝ Federated convergence speed
    """
    
    def __init__(self, plato_dir: Path):
        self.plato_dir = plato_dir
        self.signals: List[MetaSignal] = []
        
        # Hyperparameter registry
        self.hyperparams = {
            "arena": {
                "elo_k": 32,
                "curriculum_difficulty_base": 0.5,
                "opponent_pool_size": 10,
            },
            "federated": {
                "learning_rate": 0.01,
                "dp_epsilon": 4.0,
                "compression_bits": 8,
                "clients_per_round": 8,
            },
            "nas": {
                "mutation_rate": 0.15,
                "pruning_threshold": 0.01,
                "max_primitives": 100,
                "evaluations_per_gen": 50,
            },
            "curriculum": {
                "advance_threshold": 0.7,
                "consecutive_required": 3,
                "stage_skew": 0.5,
            },
            "shell": {
                "decay_rate": 0.1,
                "instability_threshold": 2.0,
                "max_grad_norm": 1.0,
            }
        }
        
        # Load previous state
        self._load_state()
    
    def _load_state(self):
        self.plato_dir.mkdir(parents=True, exist_ok=True)
        state_file = self.plato_dir / "meta_controller_state.json"
        if state_file.exists():
            with open(state_file) as f:
                state = json.load(f)
                self.hyperparams = state.get("hyperparams", self.hyperparams)
                self.signals = [
                    MetaSignal(**s) for s in state.get("signals", [])
                ]
    
    def _save_state(self):
        self.plato_dir.mkdir(parents=True, exist_ok=True)
        state = {
            "hyperparams": self.hyperparams,
            "signals": [
                {"subsystem": s.subsystem, "metric": s.metric, 
                 "value": s.value, "timestamp": s.timestamp}
                for s in self.signals[-100:]  # Keep last 100
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        with open(self.plato_dir / "meta_controller_state.json", "w") as f:
            json.dump(state, f, indent=2)
    
    def ingest_signal(self, subsystem: str, metric: str, value: float):
        """Record a signal from a subsystem."""
        signal = MetaSignal(subsystem=subsystem, metric=metric, value=value)
        self.signals.append(signal)
        
        # Trim old signals
        if len(self.signals) > 500:
            self.signals = self.signals[-250:]
    
    def get_recent_signals(self, subsystem: str, metric: str, 
                          window: int = 10) -> List[float]:
        """Get recent values for a specific signal."""
        values = [
            s.value for s in self.signals 
            if s.subsystem == subsystem and s.metric == metric
        ]
        return values[-window:]
    
    def _compute_trend(self, values: List[float]) -> float:
        """Compute trend (positive = increasing)."""
        if len(values) < 3:
            return 0.0
        recent = np.mean(values[-3:])
        older = np.mean(values[:max(1, len(values)//2)])
        return recent - older
    
    def adapt_arena(self) -> Dict:
        """
        Adapt arena hyperparameters based on fleet signals.
        
        If curriculum agents are advancing quickly, increase arena difficulty.
        If shell integrity is low, decrease arena intensity.
        """
        # Get signals
        curriculum_advance = self.get_recent_signals("curriculum", "advance_rate", 5)
        shell_integrity = self.get_recent_signals("shell", "integrity", 5)
        
        hp = self.hyperparams["arena"]
        
        # Difficulty scales with curriculum progress
        if curriculum_advance:
            avg_advance = np.mean(curriculum_advance)
            hp["curriculum_difficulty_base"] = min(0.9, 
                0.3 + avg_advance * 0.6)
        
        # If shell integrity is crashing, make arena gentler
        if shell_integrity:
            avg_integrity = np.mean(shell_integrity)
            if avg_integrity < 0.5:
                hp["elo_k"] = max(16, int(hp["elo_k"] * 0.9))
            elif avg_integrity > 0.8:
                hp["elo_k"] = min(64, int(hp["elo_k"] * 1.05))
        
        return hp
    
    def adapt_federated(self) -> Dict:
        """
        Adapt federated learning based on fleet signals.
        
        If arena ELO variance is high, increase clients per round
        (need more consensus). If NAS is finding good architectures,
        decrease noise (lower DP epsilon).
        """
        elo_variance = self.get_recent_signals("arena", "elo_variance", 5)
        nas_best = self.get_recent_signals("nas", "best_fitness", 5)
        
        hp = self.hyperparams["federated"]
        
        # More clients if arena is chaotic
        if elo_variance:
            var = np.mean(elo_variance)
            if var > 10000:  # High variance
                hp["clients_per_round"] = min(20, hp["clients_per_round"] + 2)
            elif var < 1000:  # Stable
                hp["clients_per_round"] = max(5, hp["clients_per_round"] - 1)
        
        # Less noise if NAS is performing well
        if nas_best:
            best = np.mean(nas_best)
            if best > 0.7:
                hp["dp_epsilon"] = max(1.0, hp["dp_epsilon"] * 0.95)
            elif best < 0.5:
                hp["dp_epsilon"] = min(8.0, hp["dp_epsilon"] * 1.05)
        
        return hp
    
    def adapt_nas(self) -> Dict:
        """
        Adapt NAS based on fleet signals.
        
        If shell is stable, be more aggressive with mutations.
        If federated loss is high, focus search on simpler architectures.
        """
        shell_integrity = self.get_recent_signals("shell", "integrity", 5)
        federated_loss = self.get_recent_signals("federated", "loss", 5)
        
        hp = self.hyperparams["nas"]
        
        # Mutation rate inversely proportional to shell stability
        if shell_integrity:
            integrity = np.mean(shell_integrity)
            target_mutation = 0.05 + (1.0 - integrity) * 0.25
            hp["mutation_rate"] = 0.8 * hp["mutation_rate"] + 0.2 * target_mutation
            hp["mutation_rate"] = np.clip(hp["mutation_rate"], 0.05, 0.3)
        
        # If federated loss is high, be more conservative
        if federated_loss:
            loss = np.mean(federated_loss)
            if loss > 20:
                hp["max_primitives"] = max(50, hp["max_primitives"] - 5)
                hp["evaluations_per_gen"] = max(20, hp["evaluations_per_gen"] - 5)
            elif loss < 10:
                hp["max_primitives"] = min(200, hp["max_primitives"] + 5)
                hp["evaluations_per_gen"] = min(100, hp["evaluations_per_gen"] + 5)
        
        return hp
    
    def adapt_curriculum(self) -> Dict:
        """
        Adapt curriculum based on fleet signals.
        
        If arena win rates are low, lower advancement threshold.
        If federated convergence is good, raise threshold (agents ready for harder tasks).
        """
        arena_winrate = self.get_recent_signals("arena", "win_rate", 5)
        federated_accuracy = self.get_recent_signals("federated", "accuracy", 5)
        
        hp = self.hyperparams["curriculum"]
        
        # Adjust threshold based on arena performance
        if arena_winrate:
            wr = np.mean(arena_winrate)
            if wr < 0.4:  # Agents struggling
                hp["advance_threshold"] = max(0.5, hp["advance_threshold"] - 0.05)
                hp["consecutive_required"] = max(2, hp["consecutive_required"] - 1)
            elif wr > 0.7:  # Agents crushing it
                hp["advance_threshold"] = min(0.9, hp["advance_threshold"] + 0.03)
                hp["consecutive_required"] = min(5, hp["consecutive_required"] + 1)
        
        # If federated learning is accurate, agents have good models
        if federated_accuracy:
            acc = np.mean(federated_accuracy)
            if acc > 0.15:
                hp["stage_skew"] = min(0.8, hp["stage_skew"] + 0.05)
        
        return hp
    
    def adapt_shell(self) -> Dict:
        """
        Adapt shell parameters based on fleet signals.
        
        If NAS is creating complex architectures, tighten stability constraints.
        If curriculum agents are advancing fast, relax constraints (they can handle it).
        """
        nas_primitives = self.get_recent_signals("nas", "total_primitives", 5)
        curriculum_episodes = self.get_recent_signals("curriculum", "episodes_per_stage", 5)
        
        hp = self.hyperparams["shell"]
        
        # More primitives = more complex = tighter constraints
        if nas_primitives:
            n = np.mean(nas_primitives)
            if n > 50:
                hp["instability_threshold"] = max(1.0, hp["instability_threshold"] * 0.95)
            elif n < 20:
                hp["instability_threshold"] = min(5.0, hp["instability_threshold"] * 1.05)
        
        # Fast curriculum progression = agents learning well = can handle more exploration
        if curriculum_episodes:
            eps = np.mean(curriculum_episodes)
            if eps < 8:  # Fast learners
                hp["max_grad_norm"] = min(2.0, hp["max_grad_norm"] * 1.05)
            elif eps > 15:  # Slow learners
                hp["max_grad_norm"] = max(0.5, hp["max_grad_norm"] * 0.95)
        
        return hp
    
    def run_adaptation_cycle(self) -> Dict:
        """Run one full meta-controller adaptation cycle."""
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "adaptations": {}
        }
        
        results["adaptations"]["arena"] = self.adapt_arena()
        results["adaptations"]["federated"] = self.adapt_federated()
        results["adaptations"]["nas"] = self.adapt_nas()
        results["adaptations"]["curriculum"] = self.adapt_curriculum()
        results["adaptations"]["shell"] = self.adapt_shell()
        
        self._save_state()
        
        return results
    
    def get_cross_component_report(self) -> str:
        """Generate a human-readable report of cross-component dynamics."""
        lines = ["# Cross-Component Dynamics Report", ""]
        
        for subsystem, hp in self.hyperparams.items():
            lines.append(f"## {subsystem.upper()}")
            for key, value in hp.items():
                lines.append(f"- {key}: {value}")
            lines.append("")
        
        # Recent signal summary
        lines.append("## Recent Signals")
        recent = self.signals[-20:]
        for s in recent:
            lines.append(f"- [{s.subsystem}] {s.metric} = {s.value:.4f}")
        
        return "\n".join(lines)


def demo_meta_controller():
    """Demonstrate the meta-controller."""
    print("=" * 60)
    print("PLATO Meta-Controller Demo")
    print("=" * 60)
    
    mc = PlatoMetaController(Path("/tmp/plato_meta_demo"))
    
    # Simulate signals from subsystems
    print("\n📡 Injecting signals...")
    
    # Curriculum advancing well
    for _ in range(5):
        mc.ingest_signal("curriculum", "advance_rate", random.uniform(0.6, 0.9))
    
    # Shell integrity dropping
    for _ in range(5):
        mc.ingest_signal("shell", "integrity", random.uniform(0.3, 0.5))
    
    # Arena win rates low
    for _ in range(5):
        mc.ingest_signal("arena", "win_rate", random.uniform(0.3, 0.45))
    
    # NAS finding decent architectures
    for _ in range(5):
        mc.ingest_signal("nas", "best_fitness", random.uniform(0.5, 0.65))
    
    # Federated loss high
    for _ in range(5):
        mc.ingest_signal("federated", "loss", random.uniform(15, 25))
    
    print("Running adaptation cycle...")
    results = mc.run_adaptation_cycle()
    
    print("\n📊 Adapted Hyperparameters:")
    for subsystem, hp in results["adaptations"].items():
        print(f"\n  {subsystem.upper()}:")
        for key, value in hp.items():
            print(f"    {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Meta-controller demo complete!")
    print("=" * 60)

if __name__ == "__main__":
    demo_meta_controller()
