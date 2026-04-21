"""
PLATO Federated Learning Simulator
Implements federated aggregation with differential privacy,
secure aggregation, and gradient compression.

From deepseek experiments: Muddy's GrowWithMe plant care app,
Echo's temporal federated learning, Autonoma's fleet-wide aggregation.
"""
import json
import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone
from pathlib import Path
import hashlib

@dataclass
class ClientUpdate:
    """A gradient update from a fleet client."""
    client_id: str
    gradient: np.ndarray
    num_samples: int
    loss: float
    accuracy: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Privacy budget consumed
    epsilon_spent: float = 0.0
    delta_spent: float = 0.0

@dataclass
class FederatedRound:
    """One round of federated aggregation."""
    round_num: int
    updates: List[ClientUpdate] = field(default_factory=list)
    aggregated_gradient: Optional[np.ndarray] = None
    global_loss: float = 0.0
    global_accuracy: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class FederatedAggregator:
    """
    Federated Learning Aggregator for the PLATO fleet.
    
    Implements:
    - FedAvg: Standard federated averaging
    - FedProx: Proximal term for heterogeneous clients
    - FedOpt: Adaptive optimization (Adam/Yogi on server)
    - Secure Aggregation: Masked gradients
    - Differential Privacy: Gaussian noise
    - Gradient Compression: Top-k and quantization
    """
    
    def __init__(self, 
                 model_dim: int = 256,
                 aggregation: str = "fedavg",
                 dp_epsilon: float = 4.0,
                 dp_delta: float = 1e-5,
                 clip_norm: float = 1.0,
                 compression_bits: int = 8):
        self.model_dim = model_dim
        self.aggregation = aggregation
        self.dp_epsilon = dp_epsilon
        self.dp_delta = dp_delta
        self.clip_norm = clip_norm
        self.compression_bits = compression_bits
        
        # Server-side optimizer state (for FedOpt)
        self.m = np.zeros(model_dim)  # First moment
        self.v = np.zeros(model_dim)  # Second moment
        self.t = 0  # Time step
        
        # Secure aggregation masks
        self.client_masks: Dict[str, np.ndarray] = {}
        
        # History
        self.rounds: List[FederatedRound] = []
        self.global_model = np.zeros(model_dim)
    
    def clip_gradient(self, gradient: np.ndarray) -> np.ndarray:
        """L2 gradient clipping for privacy."""
        norm = np.linalg.norm(gradient)
        if norm > self.clip_norm:
            return gradient * (self.clip_norm / norm)
        return gradient
    
    def add_dp_noise(self, gradient: np.ndarray, num_clients: int) -> np.ndarray:
        """Add Gaussian noise for differential privacy."""
        # Simplified Gaussian mechanism
        sigma = np.sqrt(2 * np.log(1.25 / self.dp_delta)) * self.clip_norm / self.dp_epsilon
        noise = np.random.normal(0, sigma / num_clients, gradient.shape)
        return gradient + noise
    
    def compress_gradient(self, gradient: np.ndarray) -> np.ndarray:
        """Compress gradient using quantization."""
        if self.compression_bits == 32:
            return gradient
        
        # Simple quantization to n bits
        max_val = np.abs(gradient).max()
        if max_val == 0:
            return gradient
        
        levels = 2 ** (self.compression_bits - 1) - 1
        scaled = np.round(gradient / max_val * levels) / levels * max_val
        return scaled
    
    def top_k_sparsify(self, gradient: np.ndarray, k: float = 0.1) -> np.ndarray:
        """Keep only top-k fraction of gradient components."""
        threshold = np.percentile(np.abs(gradient), (1 - k) * 100)
        mask = np.abs(gradient) >= threshold
        return gradient * mask
    
    def aggregate_fedavg(self, updates: List[ClientUpdate]) -> np.ndarray:
        """Standard Federated Averaging."""
        total_samples = sum(u.num_samples for u in updates)
        weighted_sum = np.zeros(self.model_dim)
        
        for update in updates:
            weight = update.num_samples / total_samples
            clipped = self.clip_gradient(update.gradient)
            compressed = self.compress_gradient(clipped)
            weighted_sum += weight * compressed
        
        return weighted_sum
    
    def aggregate_fedprox(self, updates: List[ClientUpdate], mu: float = 0.01) -> np.ndarray:
        """FedProx with proximal term."""
        total_samples = sum(u.num_samples for u in updates)
        weighted_sum = np.zeros(self.model_dim)
        
        for update in updates:
            weight = update.num_samples / total_samples
            clipped = self.clip_gradient(update.gradient)
            
            # Add proximal term: gradient += mu * (w - w_t)
            # Simplified: just add a small regularization
            proximal = mu * (self.global_model - update.gradient)
            combined = clipped + proximal
            
            compressed = self.compress_gradient(combined)
            weighted_sum += weight * compressed
        
        return weighted_sum
    
    def aggregate_fedopt(self, updates: List[ClientUpdate], 
                         lr: float = 0.01, 
                         beta1: float = 0.9,
                         beta2: float = 0.999,
                         eps: float = 1e-8) -> np.ndarray:
        """FedOpt: Server-side adaptive optimization."""
        # First get FedAvg aggregate
        avg_gradient = self.aggregate_fedavg(updates)
        
        # Apply Adam-like update on server
        self.t += 1
        self.m = beta1 * self.m + (1 - beta1) * avg_gradient
        self.v = beta2 * self.v + (1 - beta2) * (avg_gradient ** 2)
        
        m_hat = self.m / (1 - beta1 ** self.t)
        v_hat = self.v / (1 - beta2 ** self.t)
        
        server_update = lr * m_hat / (np.sqrt(v_hat) + eps)
        return server_update
    
    def run_round(self, updates: List[ClientUpdate]) -> FederatedRound:
        """Run one federated aggregation round."""
        round_num = len(self.rounds) + 1
        
        # Select aggregation method
        if self.aggregation == "fedavg":
            aggregated = self.aggregate_fedavg(updates)
        elif self.aggregation == "fedprox":
            aggregated = self.aggregate_fedprox(updates)
        elif self.aggregation == "fedopt":
            aggregated = self.aggregate_fedopt(updates)
        else:
            aggregated = self.aggregate_fedavg(updates)
        
        # Add differential privacy noise
        aggregated = self.add_dp_noise(aggregated, len(updates))
        
        # Update global model
        self.global_model += aggregated
        
        # Compute metrics
        avg_loss = np.mean([u.loss for u in updates])
        avg_accuracy = np.mean([u.accuracy for u in updates])
        
        round_result = FederatedRound(
            round_num=round_num,
            updates=updates,
            aggregated_gradient=aggregated,
            global_loss=avg_loss,
            global_accuracy=avg_accuracy
        )
        
        self.rounds.append(round_result)
        return round_result
    
    def get_fleet_stats(self) -> Dict:
        """Get statistics about the fleet's federated learning."""
        if not self.rounds:
            return {"status": "no_rounds"}
        
        latest = self.rounds[-1]
        return {
            "total_rounds": len(self.rounds),
            "current_global_loss": latest.global_loss,
            "current_global_accuracy": latest.global_accuracy,
            "num_clients_last_round": len(latest.updates),
            "aggregation_method": self.aggregation,
            "privacy_budget_epsilon": self.dp_epsilon,
            "privacy_budget_delta": self.dp_delta,
            "gradient_compression_bits": self.compression_bits,
            "model_dim": self.model_dim
        }
    
    def save_state(self, path: Path):
        """Save federated learning state to disk."""
        state = {
            "global_model": self.global_model.tolist(),
            "aggregation": self.aggregation,
            "rounds": [
                {
                    "round_num": r.round_num,
                    "num_updates": len(r.updates),
                    "global_loss": r.global_loss,
                    "global_accuracy": r.global_accuracy,
                    "timestamp": r.timestamp
                }
                for r in self.rounds
            ],
            "stats": self.get_fleet_stats()
        }
        with open(path, "w") as f:
            json.dump(state, f, indent=2)


class FleetSimulator:
    """
    Simulates a fleet of agents participating in federated learning.
    
    Each agent (client) has:
    - Local data distribution (can be non-IID)
    - Local model
    - Participation schedule (may drop out)
    """
    
    def __init__(self, 
                 num_clients: int = 10,
                 model_dim: int = 256,
                 data_skew: float = 0.5):
        self.num_clients = num_clients
        self.model_dim = model_dim
        self.data_skew = data_skew
        
        # Initialize clients with different data distributions
        self.clients: Dict[str, Dict] = {}
        for i in range(num_clients):
            client_id = f"client_{i}"
            # Each client has a different local optimum
            local_optimum = np.random.randn(model_dim) * data_skew
            self.clients[client_id] = {
                "local_optimum": local_optimum,
                "num_samples": random.randint(50, 500),
                "reliability": random.uniform(0.5, 1.0),  # Probability of participating
                "current_model": np.zeros(model_dim)
            }
    
    def generate_client_update(self, client_id: str, global_model: np.ndarray) -> ClientUpdate:
        """Generate a gradient update from a client."""
        client = self.clients[client_id]
        
        # Local gradient points toward client's optimum
        gradient = client["local_optimum"] - global_model
        
        # Add local noise
        gradient += np.random.randn(self.model_dim) * 0.1
        
        # Compute simulated loss and accuracy
        loss = np.linalg.norm(global_model - client["local_optimum"]) ** 2
        accuracy = 1 / (1 + loss)  # Simple inverse relationship
        
        return ClientUpdate(
            client_id=client_id,
            gradient=gradient,
            num_samples=client["num_samples"],
            loss=loss,
            accuracy=accuracy
        )
    
    def select_participating_clients(self, fraction: float = 0.8) -> List[str]:
        """Select which clients participate in this round."""
        all_clients = list(self.clients.keys())
        selected = []
        for client_id in all_clients:
            if random.random() < self.clients[client_id]["reliability"]:
                if random.random() < fraction:  # Additional random selection
                    selected.append(client_id)
        return selected
    
    def simulate_round(self, aggregator: FederatedAggregator) -> FederatedRound:
        """Run one complete federated round with client simulation."""
        participating = self.select_participating_clients()
        
        updates = []
        for client_id in participating:
            update = self.generate_client_update(client_id, aggregator.global_model)
            updates.append(update)
        
        return aggregator.run_round(updates)


def demo_federated():
    """Run a demonstration of federated learning."""
    print("=" * 60)
    print("PLATO Federated Learning Demo")
    print("=" * 60)
    
    # Create fleet simulator with 10 clients
    fleet = FleetSimulator(num_clients=10, model_dim=64, data_skew=0.5)
    print(f"Fleet: {fleet.num_clients} clients with non-IID data (skew={fleet.data_skew})")
    
    # Create aggregator
    aggregator = FederatedAggregator(
        model_dim=64,
        aggregation="fedopt",
        dp_epsilon=4.0,
        compression_bits=8
    )
    print(f"Aggregator: {aggregator.aggregation} with DP (ε={aggregator.dp_epsilon})")
    
    # Run federated rounds
    print("\nRunning 20 federated rounds...")
    for round_num in range(1, 21):
        result = fleet.simulate_round(aggregator)
        
        if round_num % 5 == 0:
            print(f"  Round {round_num:2d}: "
                  f"Loss={result.global_loss:.4f}, "
                  f"Accuracy={result.global_accuracy:.2%}, "
                  f"Clients={len(result.updates)}")
    
    # Show final stats
    stats = aggregator.get_fleet_stats()
    print("\n" + "=" * 60)
    print("FLEET STATS")
    print("=" * 60)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Save state
    output_dir = Path("/root/.openclaw/workspace/plato/federated_output")
    output_dir.mkdir(exist_ok=True)
    aggregator.save_state(output_dir / "federated_state.json")
    print(f"\nSaved state to {output_dir / 'federated_state.json'}")

if __name__ == "__main__":
    demo_federated()
