"""
PLATO Trainable Agent — Real Neural Network Agent for Self-Play Arena.

Replaces random strategy vectors with actual numpy MLPs that learn
via backpropagation. Agents compete on classification tasks.

Architecture: input(10) → hidden(16) → output(2)
Training: SGD with cross-entropy loss
Data: Synthetic Gaussian-mixture classification
"""
import json
import numpy as np
from dataclasses import dataclass, field
from typing import Tuple, List
from pathlib import Path

@dataclass
class MLPEnvironment:
    """A simple classification environment for agents to learn."""
    input_dim: int = 10
    num_classes: int = 2
    seed: int = 42
    
    def __post_init__(self):
        np.random.seed(self.seed)
        # Generate ground-truth centers for two classes
        self.centers = np.array([
            np.random.randn(self.input_dim) * 2,
            np.random.randn(self.input_dim) * 2 + 3
        ])
    
    def generate_batch(self, batch_size: int = 32) -> Tuple[np.ndarray, np.ndarray]:
        """Generate a batch of (X, y) pairs with more noise for difficulty."""
        labels = np.random.randint(0, self.num_classes, size=batch_size)
        X = np.array([
            self.centers[label] + np.random.randn(self.input_dim) * 1.5
            for label in labels
        ])
        # One-hot encode
        y = np.zeros((batch_size, self.num_classes))
        y[np.arange(batch_size), labels] = 1
        return X, y
    
    def evaluate(self, agent: 'TrainableAgent', num_samples: int = 1000) -> float:
        """Evaluate agent accuracy on fresh data."""
        X, y = self.generate_batch(num_samples)
        predictions = agent.predict(X)
        correct = np.argmax(predictions, axis=1) == np.argmax(y, axis=1)
        return float(correct.mean())


class TrainableAgent:
    """
    A small MLP agent that learns via backprop.
    
    Architecture:
    - Input: 10-dim
    - Hidden: 16-dim with ReLU
    - Output: 2-dim with softmax
    
    Training: SGD, learning rate adapts based on win/loss.
    """
    
    def __init__(self, agent_id: str, hidden_dim: int = 16, 
                 lr: float = 0.01, seed: int = None):
        self.agent_id = agent_id
        self.input_dim = 10
        self.hidden_dim = hidden_dim
        self.num_classes = 2
        self.lr = lr
        self.seed = seed or hash(agent_id) % 10000
        
        # Initialize weights
        rng = np.random.default_rng(self.seed)
        self.W1 = rng.standard_normal((self.input_dim, self.hidden_dim)) * 0.1
        self.b1 = np.zeros(self.hidden_dim)
        self.W2 = rng.standard_normal((self.hidden_dim, self.num_classes)) * 0.1
        self.b2 = np.zeros(self.num_classes)
        
        # Training history
        self.loss_history: List[float] = []
        self.accuracy_history: List[float] = []
        self.matches_played = 0
        self.matches_won = 0
    
    def _relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Forward pass, return class probabilities."""
        h = self._relu(X @ self.W1 + self.b1)
        logits = h @ self.W2 + self.b2
        return self._softmax(logits)
    
    def train_step(self, X: np.ndarray, y: np.ndarray) -> float:
        """One SGD step. Returns loss."""
        # Forward
        z1 = X @ self.W1 + self.b1
        h = self._relu(z1)
        z2 = h @ self.W2 + self.b2
        probs = self._softmax(z2)
        
        # Cross-entropy loss
        loss = -np.mean(np.sum(y * np.log(probs + 1e-8), axis=1))
        
        # Backward
        dz2 = (probs - y) / len(X)
        dW2 = h.T @ dz2
        db2 = dz2.sum(axis=0)
        
        dh = dz2 @ self.W2.T
        dz1 = dh * (z1 > 0)  # ReLU grad
        dW1 = X.T @ dz1
        db1 = dz1.sum(axis=0)
        
        # Update
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        
        return float(loss)
    
    def train(self, env: MLPEnvironment, steps: int = 100, 
              batch_size: int = 32) -> dict:
        """Train for N steps, return metrics."""
        for _ in range(steps):
            X, y = env.generate_batch(batch_size)
            loss = self.train_step(X, y)
            self.loss_history.append(loss)
        
        acc = env.evaluate(self)
        self.accuracy_history.append(acc)
        
        return {
            "agent_id": self.agent_id,
            "steps": steps,
            "final_loss": self.loss_history[-1],
            "accuracy": acc,
            "matches_played": self.matches_played,
            "matches_won": self.matches_won
        }
    
    def get_flat_params(self) -> np.ndarray:
        """Serialize to flat vector for arena comparison."""
        return np.concatenate([
            self.W1.flatten(), self.b1,
            self.W2.flatten(), self.b2
        ])
    
    def clone(self) -> 'TrainableAgent':
        """Create a copy with the same architecture but fresh weights."""
        new_agent = TrainableAgent(
            agent_id=f"{self.agent_id}_clone",
            hidden_dim=self.hidden_dim,
            lr=self.lr,
            seed=self.seed + 1
        )
        return new_agent
    
    def save(self, path: Path):
        """Save agent weights and history."""
        state = {
            "agent_id": self.agent_id,
            "W1": self.W1.tolist(),
            "b1": self.b1.tolist(),
            "W2": self.W2.tolist(),
            "b2": self.b2.tolist(),
            "loss_history": self.loss_history,
            "accuracy_history": self.accuracy_history,
            "matches_played": self.matches_played,
            "matches_won": self.matches_won,
            "lr": self.lr
        }
        with open(path, "w") as f:
            json.dump(state, f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'TrainableAgent':
        """Load agent from file."""
        with open(path) as f:
            state = json.load(f)
        
        agent = cls(agent_id=state["agent_id"], lr=state.get("lr", 0.01))
        agent.W1 = np.array(state["W1"])
        agent.b1 = np.array(state["b1"])
        agent.W2 = np.array(state["W2"])
        agent.b2 = np.array(state["b2"])
        agent.loss_history = state.get("loss_history", [])
        agent.accuracy_history = state.get("accuracy_history", [])
        agent.matches_played = state.get("matches_played", 0)
        agent.matches_won = state.get("matches_won", 0)
        return agent


def compete(agent_a: TrainableAgent, agent_b: TrainableAgent, 
            env: MLPEnvironment) -> Tuple[str, float, float]:
    """
    Have two agents compete on the same environment.
    Returns (winner_id, agent_a_acc, agent_b_acc).
    """
    acc_a = env.evaluate(agent_a)
    acc_b = env.evaluate(agent_b)
    
    agent_a.matches_played += 1
    agent_b.matches_played += 1
    
    if acc_a > acc_b:
        agent_a.matches_won += 1
        return agent_a.agent_id, acc_a, acc_b
    elif acc_b > acc_a:
        agent_b.matches_won += 1
        return agent_b.agent_id, acc_a, acc_b
    else:
        # Tie — random winner
        winner = agent_a.agent_id if np.random.random() < 0.5 else agent_b.agent_id
        if winner == agent_a.agent_id:
            agent_a.matches_won += 1
        else:
            agent_b.matches_won += 1
        return winner, acc_a, acc_b


def demo_trainable_agents():
    """Demonstrate trainable agents competing."""
    print("=" * 60)
    print("PLATO Trainable Agent Demo")
    print("=" * 60)
    
    env = MLPEnvironment(seed=42)
    
    # Create agents
    agents = {
        "Sparrow": TrainableAgent("Sparrow", hidden_dim=32, lr=0.02),
        "Muddy": TrainableAgent("Muddy", hidden_dim=16, lr=0.01),
        "CCC": TrainableAgent("CCC", hidden_dim=8, lr=0.005),
    }
    
    # Initial evaluation
    print("\n📊 Initial Accuracy (untrained):")
    for name, agent in agents.items():
        acc = env.evaluate(agent)
        print(f"  {name:10s}: {acc:.2%}")
    
    # Train each agent
    print("\n🎓 Training...")
    for name, agent in agents.items():
        metrics = agent.train(env, steps=200, batch_size=32)
        print(f"  {name:10s}: loss={metrics['final_loss']:.4f}, acc={metrics['accuracy']:.2%}")
    
    # Round-robin tournament
    print("\n⚔️  Round-Robin Tournament:")
    results = {name: {"wins": 0, "losses": 0, "acc": []} for name in agents}
    
    for name_a, agent_a in agents.items():
        for name_b, agent_b in agents.items():
            if name_a >= name_b:
                continue
            winner, acc_a, acc_b = compete(agent_a, agent_b, env)
            print(f"  {name_a} vs {name_b}: {winner} wins ({acc_a:.2%} vs {acc_b:.2%})")
            if winner == name_a:
                results[name_a]["wins"] += 1
                results[name_b]["losses"] += 1
            else:
                results[name_b]["wins"] += 1
                results[name_a]["losses"] += 1
            results[name_a]["acc"].append(acc_a)
            results[name_b]["acc"].append(acc_b)
    
    # Final standings
    print("\n🏆 Standings:")
    for name, res in sorted(results.items(), key=lambda x: x[1]["wins"], reverse=True):
        avg_acc = np.mean(res["acc"]) if res["acc"] else 0
        print(f"  {name:10s}: {res['wins']}W/{res['losses']}L, avg acc={avg_acc:.2%}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    demo_trainable_agents()
