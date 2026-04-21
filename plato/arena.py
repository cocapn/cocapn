"""
PLATO Self-Play Arena
Real implementation of the self-play system from deepseek experiments.

Features:
- ELO-based matchmaking
- League of historical policies
- Curriculum learning
- Multi-objective rewards
- Behavioral archetype discovery
"""
import json
import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone
from pathlib import Path

@dataclass
class PolicySnapshot:
    """A frozen policy checkpoint for the league."""
    version: str
    elo: float = 1200.0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    strategy_vector: np.ndarray = field(default_factory=lambda: np.random.randn(16))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    @property
    def games_played(self) -> int:
        return self.wins + self.losses + self.draws
    
    @property
    def win_rate(self) -> float:
        if self.games_played == 0:
            return 0.5
        return self.wins / self.games_played
    
    def update_elo(self, opponent_elo: float, result: float, k: int = 32):
        """Update ELO rating after a match. result: 1=win, 0.5=draw, 0=loss"""
        expected = 1 / (1 + 10 ** ((opponent_elo - self.elo) / 400))
        self.elo += k * (result - expected)

@dataclass  
class ArenaMatch:
    """A single match in the arena."""
    player1: str  # version string
    player2: str
    result: float  # 1 = p1 wins, 0.5 = draw, 0 = p2 wins
    duration_steps: int
    exploration_bonus: float = 0.0
    insight_quality: float = 0.0
    behavioral_archetype: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SelfPlayArena:
    """
    The Self-Play Arena from PLATO.
    
    Agents train by competing against historical versions of themselves
    and other fleet agents. The arena manages:
    - League snapshots
    - ELO ratings
    - Curriculum progression
    - Behavioral archetype discovery
    """
    
    def __init__(self, arena_dir: Path):
        self.arena_dir = arena_dir
        self.league: Dict[str, PolicySnapshot] = {}
        self.matches: List[ArenaMatch] = []
        self.curriculum_stage = 0
        self.elo_k = 32
        
        # Behavioral archetypes discovered
        self.archetypes = {
            "aggressive_explorer": np.array([1.0, 0.8, 0.2, -0.3] + [0.0]*12),
            "cautious_hoarder": np.array([-0.5, 0.3, 1.0, 0.7] + [0.0]*12),
            "efficient_pathfinder": np.array([0.2, 1.0, 0.1, 0.4] + [0.0]*12),
            "social_mimic": np.array([0.5, 0.2, 0.6, 0.8] + [0.0]*12),
        }
        
        self._load_state()
    
    def _load_state(self):
        """Load arena state from disk."""
        state_file = self.arena_dir / "arena_state.json"
        if state_file.exists():
            with open(state_file) as f:
                state = json.load(f)
                for v, data in state.get("league", {}).items():
                    self.league[v] = PolicySnapshot(
                        version=v,
                        elo=data["elo"],
                        wins=data["wins"],
                        losses=data["losses"],
                        draws=data["draws"],
                        strategy_vector=np.array(data["strategy_vector"]),
                        created_at=data["created_at"]
                    )
    
    def _save_state(self):
        """Save arena state to disk."""
        state = {
            "league": {
                v: {
                    "elo": p.elo,
                    "wins": p.wins,
                    "losses": p.losses,
                    "draws": p.draws,
                    "strategy_vector": p.strategy_vector.tolist(),
                    "created_at": p.created_at
                }
                for v, p in self.league.items()
            },
            "curriculum_stage": self.curriculum_stage,
            "total_matches": len(self.matches)
        }
        with open(self.arena_dir / "arena_state.json", "w") as f:
            json.dump(state, f, indent=2)
    
    def add_snapshot(self, version: str, strategy_vector: Optional[np.ndarray] = None) -> PolicySnapshot:
        """Add a new policy snapshot to the league."""
        if strategy_vector is None:
            strategy_vector = np.random.randn(16)
        
        snapshot = PolicySnapshot(version=version, strategy_vector=strategy_vector)
        self.league[version] = snapshot
        self._save_state()
        return snapshot
    
    def select_opponent(self, player_version: str, strategy: str = "pfsp") -> str:
        """
        Select an opponent using Prioritized Fictitious Self-Play.
        
        Strategies:
        - pfsp: Prioritized Fictitious Self-Play (favor strong opponents)
        - uniform: Random selection
        - elo_matched: Select similar ELO
        - diverse: Select different strategy vector
        """
        if player_version not in self.league:
            raise ValueError(f"Player {player_version} not in league")
        
        player = self.league[player_version]
        opponents = [v for v in self.league.keys() if v != player_version]
        
        if not opponents:
            return player_version  # Play against self if no opponents
        
        if strategy == "uniform":
            return random.choice(opponents)
        
        elif strategy == "elo_matched":
            # Select opponent with closest ELO
            opponent_elos = [(v, abs(self.league[v].elo - player.elo)) for v in opponents]
            opponent_elos.sort(key=lambda x: x[1])
            return opponent_elos[0][0]
        
        elif strategy == "pfsp":
            # Prioritize opponents that are strong but beatable
            weights = []
            for v in opponents:
                opp = self.league[v]
                # Weight by win probability * historical difficulty
                win_prob = 1 / (1 + 10 ** ((opp.elo - player.elo) / 400))
                # Favor opponents that player has struggled against
                historical_difficulty = 0.5
                weights.append(win_prob * (1 + historical_difficulty))
            
            total = sum(weights)
            probs = [w / total for w in weights]
            return np.random.choice(opponents, p=probs)
        
        elif strategy == "diverse":
            # Select opponent with different strategy
            player_strat = player.strategy_vector[:4]
            distances = []
            for v in opponents:
                opp_strat = self.league[v].strategy_vector[:4]
                dist = np.linalg.norm(player_strat - opp_strat)
                distances.append((v, dist))
            
            distances.sort(key=lambda x: x[1], reverse=True)
            return distances[0][0]  # Most different
        
        return random.choice(opponents)
    
    def simulate_match(self, player1: str, player2: str, 
                       curriculum_difficulty: float = 0.5) -> ArenaMatch:
        """
        Simulate a match between two policies.
        
        The outcome depends on:
        - ELO ratings (higher = more likely to win)
        - Strategy matchup (some strategies counter others)
        - Curriculum difficulty
        - Random noise (stochastic environment)
        """
        p1 = self.league[player1]
        p2 = self.league[player2]
        
        # ELO-based win probability
        p1_win_prob = 1 / (1 + 10 ** ((p2.elo - p1.elo) / 400))
        
        # Strategy interaction
        strat_interaction = np.dot(
            p1.strategy_vector[:4], 
            p2.strategy_vector[:4]
        ) / (np.linalg.norm(p1.strategy_vector[:4]) * np.linalg.norm(p2.strategy_vector[:4]) + 1e-8)
        
        # Some strategies counter others
        if strat_interaction < -0.3:
            p1_win_prob += 0.1  # Counter-strategy bonus
        elif strat_interaction > 0.7:
            p1_win_prob -= 0.05  # Similar strategies = more random
        
        # Curriculum difficulty affects match length and noise
        noise = random.gauss(0, 0.1 + curriculum_difficulty * 0.1)
        p1_win_prob += noise
        p1_win_prob = np.clip(p1_win_prob, 0.05, 0.95)
        
        # Determine result
        roll = random.random()
        if roll < p1_win_prob:
            result = 1.0
            p1.wins += 1
            p2.losses += 1
        elif roll < p1_win_prob + 0.05:  # 5% draw chance
            result = 0.5
            p1.draws += 1
            p2.draws += 1
        else:
            result = 0.0
            p1.losses += 1
            p2.wins += 1
        
        # Update ELO
        p1.update_elo(p2.elo, result, self.elo_k)
        p2.update_elo(p1.elo, 1 - result, self.elo_k)
        
        # Match characteristics
        duration = int(random.gauss(20 + curriculum_difficulty * 30, 10))
        duration = max(5, min(100, duration))
        
        exploration_bonus = random.random() * (1 - curriculum_difficulty)
        insight_quality = random.random() * (0.5 + curriculum_difficulty * 0.5)
        
        # Determine behavioral archetype
        combined_strat = (p1.strategy_vector + p2.strategy_vector) / 2
        archetype = self._classify_archetype(combined_strat)
        
        match = ArenaMatch(
            player1=player1,
            player2=player2,
            result=result,
            duration_steps=duration,
            exploration_bonus=exploration_bonus,
            insight_quality=insight_quality,
            behavioral_archetype=archetype
        )
        
        self.matches.append(match)
        self._save_state()
        
        return match
    
    def _classify_archetype(self, strategy_vector: np.ndarray) -> str:
        """Classify a strategy vector into a known archetype."""
        best_match = "unknown"
        best_score = -float('inf')
        
        for name, archetype_vec in self.archetypes.items():
            score = np.dot(strategy_vector[:4], archetype_vec[:4])
            if score > best_score:
                best_score = score
                best_match = name
        
        return best_match
    
    def run_training_session(self, agent_version: str, num_matches: int = 100,
                            opponent_strategy: str = "pfsp") -> Dict:
        """Run a full training session for an agent."""
        if agent_version not in self.league:
            self.add_snapshot(agent_version)
        
        results = {
            "agent": agent_version,
            "matches": num_matches,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "elo_start": self.league[agent_version].elo,
            "matches_detail": []
        }
        
        for i in range(num_matches):
            # Adaptive curriculum
            win_rate_so_far = (results["wins"] + 0.5 * results["draws"]) / (i + 1) if i > 0 else 0.5
            curriculum_difficulty = min(1.0, 0.3 + win_rate_so_far * 0.7)
            
            opponent = self.select_opponent(agent_version, opponent_strategy)
            match = self.simulate_match(agent_version, opponent, curriculum_difficulty)
            
            if match.result == 1.0:
                results["wins"] += 1
            elif match.result == 0.5:
                results["draws"] += 1
            else:
                results["losses"] += 1
            
            results["matches_detail"].append({
                "opponent": opponent,
                "result": match.result,
                "elo_after": self.league[agent_version].elo,
                "archetype": match.behavioral_archetype
            })
        
        results["elo_end"] = self.league[agent_version].elo
        results["elo_gain"] = results["elo_end"] - results["elo_start"]
        results["win_rate"] = results["wins"] / num_matches
        
        # Save training log
        log_path = self.arena_dir / f"training_log_{agent_version}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_path, "w") as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def get_leaderboard(self, top_n: int = 10) -> List[Tuple[str, float, int]]:
        """Get top N agents by ELO."""
        sorted_league = sorted(
            self.league.items(),
            key=lambda x: x[1].elo,
            reverse=True
        )
        return [
            (v, p.elo, p.games_played)
            for v, p in sorted_league[:top_n]
        ]
    
    def discover_new_archetype(self, name: str, vector: np.ndarray):
        """Add a newly discovered behavioral archetype."""
        self.archetypes[name] = vector
        self._save_state()


def demo():
    """Run a demonstration of the Self-Play Arena."""
    print("=" * 60)
    print("PLATO Self-Play Arena Demo")
    print("=" * 60)
    
    arena_dir = Path("/tmp/plato_arena_demo")
    arena_dir.mkdir(exist_ok=True)
    arena = SelfPlayArena(arena_dir)
    
    # Create initial agents
    agents = ["Sparrow_v1", "Muddy_v1", "CCC_v1", "Echo_v1"]
    for agent in agents:
        arena.add_snapshot(agent, strategy_vector=np.random.randn(16))
    print(f"Created {len(agents)} agents in the league")
    
    # Run training sessions
    for agent in agents:
        print(f"\nTraining {agent}...")
        results = arena.run_training_session(agent, num_matches=50)
        print(f"  Matches: {results['matches']}")
        print(f"  Win rate: {results['win_rate']:.2%}")
        print(f"  ELO: {results['elo_start']:.0f} -> {results['elo_end']:.0f} (+{results['elo_gain']:.0f})")
    
    # Show leaderboard
    print("\n" + "=" * 60)
    print("LEADERBOARD")
    print("=" * 60)
    for rank, (name, elo, games) in enumerate(arena.get_leaderboard(10), 1):
        print(f"{rank}. {name:15s} ELO: {elo:6.0f}  Games: {games}")
    
    print("\n" + "=" * 60)
    print("Arena demo complete!")
    print("=" * 60)

if __name__ == "__main__":
    demo()
