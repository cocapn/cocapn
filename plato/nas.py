"""
PLATO Recursive Neural Architecture Search
Implements self-modifying search spaces with meta-learning.

From deepseek experiments:
- Architect-0: Automated NAS with swarm workers
- Recursor-0: 5-level recursive meta-learning stack
- DeepRecursor: Self-modifying search space crystal with mutation engine
"""
import json
import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
from datetime import datetime, timezone
from pathlib import Path
from copy import deepcopy

@dataclass
class Primitive:
    """A primitive operation in the search space."""
    name: str
    type: str  # 'conv', 'attention', 'pool', 'activation', 'skip', 'custom'
    params: Dict = field(default_factory=dict)
    embedding: np.ndarray = field(default_factory=lambda: np.random.randn(16))
    usage_count: int = 0
    success_score: float = 0.0

@dataclass
class Architecture:
    """A neural architecture genotype."""
    name: str
    primitives: List[str]  # List of primitive names in sequence
    connections: List[Tuple[int, int]]  # DAG edges
    fitness: float = 0.0
    evaluation_count: int = 0
    
    def to_vector(self, primitive_embeddings: Dict[str, np.ndarray]) -> np.ndarray:
        """Convert architecture to a fixed-length vector."""
        # Average of primitive embeddings, padded to fixed length
        vectors = [primitive_embeddings[p] for p in self.primitives if p in primitive_embeddings]
        if not vectors:
            return np.zeros(16)
        return np.mean(vectors, axis=0)

class SelfModifyingSearchSpace:
    """
    The Crystal Lattice from PLATO's Engine Room.
    
    A directed acyclic graph of primitives that evolves over time:
    - Mutation engine adds new primitives based on successful motifs
    - Constraint weaver prunes unused primitives
    - Meta-NAS optimizes the search space itself
    """
    
    def __init__(self, 
                 max_primitives: int = 1000,
                 mutation_rate: float = 0.1,
                 pruning_threshold: float = 0.01):
        self.max_primitives = max_primitives
        self.mutation_rate = mutation_rate
        self.pruning_threshold = pruning_threshold
        
        # The crystal: DAG of primitives
        self.primitives: Dict[str, Primitive] = {}
        self.valid_connections: Dict[str, List[str]] = {}  # What can follow what
        
        # Initialize with basic primitives
        self._initialize_base_primitives()
        
        # Evolution history
        self.generation = 0
        self.motif_history: List[Dict] = []
        
        # Meta-learning state
        self.meta_controller = {
            "mutation_rate": mutation_rate,
            "pruning_aggression": 0.5,
            "exploration_bonus": 0.1
        }
    
    def _initialize_base_primitives(self):
        """Initialize the crystal with basic ML primitives."""
        base = [
            ("Conv3x3", "conv", {"kernel": 3, "stride": 1}),
            ("Conv5x5", "conv", {"kernel": 5, "stride": 1}),
            ("SelfAttention", "attention", {"heads": 8}),
            ("ReLU", "activation", {}),
            ("GELU", "activation", {}),
            ("MaxPool", "pool", {"size": 2}),
            ("AvgPool", "pool", {"size": 2}),
            ("Residual", "skip", {}),
            ("Concat", "skip", {}),
            ("BatchNorm", "norm", {}),
            ("LayerNorm", "norm", {}),
            ("RoomHarbor", "custom", {"fleet": True}),
            ("ObjectAnchor", "custom", {"fleet": True}),
            ("SpiralAttention", "attention", {"fleet": True}),
            ("FederatedGate", "custom", {"fleet": True}),
        ]
        
        for name, ptype, params in base:
            self.primitives[name] = Primitive(
                name=name, type=ptype, params=params,
                embedding=np.random.randn(16)
            )
            self.valid_connections[name] = [p for p, v in self.primitives.items() 
                                             if p != name or ptype in ['activation', 'norm']]
    
    def sample_architecture(self, max_depth: int = 20) -> Architecture:
        """Sample a random architecture from the current search space."""
        depth = random.randint(3, max_depth)
        primitives = []
        connections = []
        
        # Start with a random primitive
        current = random.choice(list(self.primitives.keys()))
        primitives.append(current)
        
        for i in range(1, depth):
            # Sample next primitive from valid connections
            valid_next = self.valid_connections.get(current, list(self.primitives.keys()))
            if not valid_next:
                break
            
            next_prim = random.choice(valid_next)
            primitives.append(next_prim)
            connections.append((i-1, i))  # Sequential connection
            
            # Add skip connection with small probability
            if random.random() < 0.1 and i > 1:
                skip_from = random.randint(0, i-2)
                connections.append((skip_from, i))
            
            current = next_prim
        
        return Architecture(
            name=f"arch_gen{self.generation}_{random.randint(1000, 9999)}",
            primitives=primitives,
            connections=connections
        )
    
    def evaluate_architecture(self, architecture: Architecture, 
                            task_difficulty: float = 0.5) -> float:
        """
        Evaluate an architecture on a simulated task.
        
        Higher fitness = better architecture.
        """
        # Base fitness from number of primitives (not too shallow, not too deep)
        depth = len(architecture.primitives)
        depth_score = 1.0 - abs(depth - 12) / 20  # Optimal around 12 layers
        
        # Diversity bonus: using many different primitive types
        types_used = set(self.primitives[p].type for p in architecture.primitives 
                        if p in self.primitives)
        diversity_score = len(types_used) / 5  # Normalize by expected types
        
        # Skip connection bonus (residual connections help)
        num_skips = len([c for c in architecture.connections if c[1] - c[0] > 1])
        skip_score = min(1.0, num_skips / 3)
        
        # Task-specific bonus
        if task_difficulty > 0.7:
            # Hard tasks favor attention mechanisms
            attention_count = sum(1 for p in architecture.primitives 
                                 if p in self.primitives and self.primitives[p].type == "attention")
            task_bonus = attention_count / depth
        else:
            # Easy tasks favor simple convolutions
            conv_count = sum(1 for p in architecture.primitives 
                           if p in self.primitives and self.primitives[p].type == "conv")
            task_bonus = conv_count / depth
        
        # Combine scores
        fitness = (0.3 * depth_score + 0.2 * diversity_score + 
                  0.2 * skip_score + 0.3 * task_bonus)
        
        # Add noise for stochastic evaluation
        fitness += random.gauss(0, 0.05)
        fitness = np.clip(fitness, 0.0, 1.0)
        
        architecture.fitness = fitness
        architecture.evaluation_count += 1
        
        # Update primitive success scores
        for p in architecture.primitives:
            if p in self.primitives:
                self.primitives[p].usage_count += 1
                # Exponential moving average of success
                alpha = 0.1
                self.primitives[p].success_score = (
                    (1 - alpha) * self.primitives[p].success_score + alpha * fitness
                )
        
        return fitness
    
    def extract_motifs(self, top_architectures: List[Architecture], 
                       min_length: int = 3,
                       min_frequency: int = 2) -> List[List[str]]:
        """
        Extract common subgraphs (motifs) from top architectures.
        
        A motif is a sequence of primitives that appears frequently
        in high-performing architectures.
        """
        # Collect all sequences from top architectures
        sequences = [arch.primitives for arch in top_architectures]
        
        # Find frequent contiguous subsequences
        motifs = []
        for length in range(min_length, 6):
            candidate_motifs = {}
            for seq in sequences:
                for i in range(len(seq) - length + 1):
                    motif = tuple(seq[i:i+length])
                    candidate_motifs[motif] = candidate_motifs.get(motif, 0) + 1
            
            for motif, count in candidate_motifs.items():
                if count >= min_frequency:
                    motifs.append(list(motif))
        
        return motifs
    
    def crystallize_motif(self, motif: List[str]) -> Optional[Primitive]:
        """
        Convert a frequent motif into a new primitive.
        
        This compresses the search space by making common patterns
        into single building blocks.
        """
        if len(self.primitives) >= self.max_primitives:
            return None
        
        # Create new primitive name
        motif_name = "".join(motif)[:20] + f"_Block_v{self.generation}"
        
        # Compute embedding as average of motif primitives
        embeddings = [self.primitives[p].embedding for p in motif if p in self.primitives]
        if not embeddings:
            return None
        
        avg_embedding = np.mean(embeddings, axis=0)
        
        new_primitive = Primitive(
            name=motif_name,
            type="composite",
            params={"motif": motif, "derived_from": self.generation},
            embedding=avg_embedding,
            usage_count=0,
            success_score=0.8  # Inherit high score from parent motif
        )
        
        self.primitives[motif_name] = new_primitive
        
        # Update connections: new primitive can be used wherever its first element could be
        first_prim = motif[0]
        self.valid_connections[motif_name] = self.valid_connections.get(first_prim, [])
        
        # The new primitive can be followed by what the last element could be followed by
        last_prim = motif[-1]
        for p in self.primitives:
            if last_prim in self.valid_connections.get(p, []):
                if motif_name not in self.valid_connections.get(p, []):
                    self.valid_connections.setdefault(p, []).append(motif_name)
        
        return new_primitive
    
    def prune_unused_primitives(self):
        """
        Remove primitives that haven't been used in successful architectures.
        
        Like synaptic pruning in the brain — keeps the search space lean.
        """
        to_prune = []
        for name, prim in self.primitives.items():
            if prim.type == "composite" and prim.usage_count < 5:
                # Composite primitives need more usage to justify their existence
                if prim.success_score < self.pruning_threshold:
                    to_prune.append(name)
        
        for name in to_prune:
            del self.primitives[name]
            if name in self.valid_connections:
                del self.valid_connections[name]
            # Remove from other primitives' connection lists
            for p in self.valid_connections:
                if name in self.valid_connections[p]:
                    self.valid_connections[p].remove(name)
    
    def mutate_search_space(self, num_evaluations: int = 100):
        """
        Run one generation of search space evolution.
        
        1. Sample and evaluate architectures
        2. Extract motifs from top performers
        3. Crystallize motifs into new primitives
        4. Prune unused primitives
        5. Update meta-controller
        """
        self.generation += 1
        
        # Sample architectures
        architectures = [self.sample_architecture() for _ in range(num_evaluations)]
        
        # Evaluate
        for arch in architectures:
            task_difficulty = random.uniform(0.3, 0.9)
            self.evaluate_architecture(arch, task_difficulty)
        
        # Sort by fitness
        architectures.sort(key=lambda a: a.fitness, reverse=True)
        top_10_percent = architectures[:max(1, len(architectures) // 10)]
        
        # Extract and crystallize motifs
        motifs = self.extract_motifs(top_10_percent)
        
        crystallized = 0
        for motif in motifs[:5]:  # Top 5 motifs
            new_prim = self.crystallize_motif(motif)
            if new_prim:
                crystallized += 1
                self.motif_history.append({
                    "generation": self.generation,
                    "motif": motif,
                    "new_primitive": new_prim.name,
                    "avg_fitness": np.mean([a.fitness for a in top_10_percent])
                })
        
        # Prune
        self.prune_unused_primitives()
        
        # Update meta-controller
        self._update_meta_controller(top_10_percent)
        
        return {
            "generation": self.generation,
            "architectures_evaluated": num_evaluations,
            "best_fitness": architectures[0].fitness if architectures else 0,
            "avg_fitness": np.mean([a.fitness for a in architectures]) if architectures else 0,
            "motifs_extracted": len(motifs),
            "primitives_crystallized": crystallized,
            "total_primitives": len(self.primitives),
            "meta_controller": self.meta_controller
        }
    
    def _update_meta_controller(self, top_architectures: List[Architecture]):
        """
        Update the meta-controller that governs the mutation engine.
        
        This is meta-meta-learning: optimizing the optimizer.
        """
        avg_fitness = np.mean([a.fitness for a in top_architectures]) if top_architectures else 0
        
        # If fitness is stagnating, increase exploration
        if avg_fitness < 0.6:
            self.meta_controller["mutation_rate"] = min(0.3, self.meta_controller["mutation_rate"] * 1.1)
            self.meta_controller["exploration_bonus"] = min(0.3, self.meta_controller["exploration_bonus"] * 1.2)
        else:
            # If fitness is good, be more conservative
            self.meta_controller["mutation_rate"] = max(0.05, self.meta_controller["mutation_rate"] * 0.95)
            self.meta_controller["exploration_bonus"] = max(0.05, self.meta_controller["exploration_bonus"] * 0.9)
        
        # Adjust pruning based on search space size
        if len(self.primitives) > self.max_primitives * 0.8:
            self.meta_controller["pruning_aggression"] = min(0.9, self.meta_controller["pruning_aggression"] * 1.1)
        else:
            self.meta_controller["pruning_aggression"] = max(0.1, self.meta_controller["pruning_aggression"] * 0.95)
    
    def save_state(self, path: Path):
        """Save the search space crystal to disk."""
        state = {
            "generation": self.generation,
            "total_primitives": len(self.primitives),
            "primitives": [
                {
                    "name": p.name,
                    "type": p.type,
                    "usage_count": p.usage_count,
                    "success_score": p.success_score
                }
                for p in self.primitives.values()
            ],
            "motif_history": self.motif_history[-10:],  # Last 10
            "meta_controller": self.meta_controller
        }
        with open(path, "w") as f:
            json.dump(state, f, indent=2)


def demo_recursive_nas():
    """Run a demonstration of recursive NAS."""
    print("=" * 60)
    print("PLATO Recursive NAS Demo")
    print("=" * 60)
    
    search_space = SelfModifyingSearchSpace(
        max_primitives=100,
        mutation_rate=0.1,
        pruning_threshold=0.01
    )
    
    print(f"Initial crystal: {len(search_space.primitives)} primitives")
    print(f"Base primitives: {list(search_space.primitives.keys())[:5]}...")
    
    # Run multiple generations
    print("\nEvolving search space...")
    for gen in range(1, 11):
        result = search_space.mutate_search_space(num_evaluations=50)
        
        if gen % 2 == 0:
            print(f"  Gen {gen:2d}: "
                  f"Best={result['best_fitness']:.3f}, "
                  f"Avg={result['avg_fitness']:.3f}, "
                  f"Primitives={result['total_primitives']}, "
                  f"Crystallized={result['primitives_crystallized']}")
    
    # Show final state
    print("\n" + "=" * 60)
    print("FINAL CRYSTAL STATE")
    print("=" * 60)
    print(f"Generation: {search_space.generation}")
    print(f"Total primitives: {len(search_space.primitives)}")
    print(f"Composite primitives: {sum(1 for p in search_space.primitives.values() if p.type == 'composite')}")
    print(f"Meta-controller: {search_space.meta_controller}")
    
    # Show top composite primitives
    composites = sorted(
        [p for p in search_space.primitives.values() if p.type == "composite"],
        key=lambda p: p.success_score,
        reverse=True
    )[:5]
    
    if composites:
        print("\nTop Composite Primitives:")
        for p in composites:
            print(f"  {p.name}: score={p.success_score:.3f}, usage={p.usage_count}")
    
    # Save state
    output_dir = Path("/root/.openclaw/workspace/plato/nas_output")
    output_dir.mkdir(exist_ok=True)
    search_space.save_state(output_dir / "search_space_state.json")
    print(f"\nSaved state to {output_dir / 'search_space_state.json'}")

if __name__ == "__main__":
    demo_recursive_nas()
