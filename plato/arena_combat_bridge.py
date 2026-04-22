"""
Arena-Combat Bridge

Integrates the algorithmic combat engine (combat_engine.py) with the
self-play arena (arena.py). Converts policy strategy vectors into
combatants with spells, equipment, and behavioral tags.

This replaces the probabilistic ELO+noise match simulation with
deterministic, interpretable combat rounds. Every decision is visible
in the combat log. No black-box inference.
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
import json

from combat_engine import (
    Combatant, Spell, Equipment, CombatEncounter,
    CombatState, SPELL_CATALOG, EQUIPMENT_CATALOG, DamageType,
)
from arena import SelfPlayArena, PolicySnapshot, ArenaMatch


class StrategyToCombatant:
    """Maps a 16-dim strategy vector to a combatant build.
    
    The strategy vector dimensions (from deepseek experiments):
    0-3:   Aggression, Defense, Mobility, Control  (combat style)
    4-7:   Exploration, Exploitation, Risk, Safety  (meta)
    8-11:  Adaptation, Specialization, Hybrid, Niche  (flexibility)
    12-15: Consistency, Variance, Burst, Sustain  (temporal)
    """
    
    @staticmethod
    def build(name: str, snapshot: PolicySnapshot) -> Combatant:
        vec = snapshot.strategy_vector
        
        # Derive core stats from combat-style dimensions (0-3)
        aggression = np.clip((vec[0] + 2) / 4, 0.1, 1.0)
        defense = np.clip((vec[1] + 2) / 4, 0.1, 1.0)
        mobility = np.clip((vec[2] + 2) / 4, 0.1, 1.0)
        control = np.clip((vec[3] + 2) / 4, 0.1, 1.0)
        
        # Derive secondary stats from meta dimensions (4-7)
        risk = np.clip((vec[6] + 2) / 4, 0.1, 1.0)
        
        # Base stats (10-20 range)
        stats = {
            "strength": int(10 + aggression * 10),
            "dexterity": int(10 + mobility * 10),
            "intelligence": int(10 + control * 10),
            "wisdom": int(10 + defense * 8),
            "constitution": int(10 + defense * 8 + risk * 2),
            "luck": int(10 + risk * 5),
        }
        
        # HP/MP from constitution and intelligence
        max_hp = 80 + stats["constitution"] * 4
        max_mp = 30 + stats["intelligence"] * 3
        
        # Behavioral tag from dominant combat style
        styles = [("aggressive", aggression), ("defensive", defense),
                  ("opportunist", mobility), ("balanced", control)]
        behavioral_tag = max(styles, key=lambda x: x[1])[0]
        
        # Spell selection based on stats + strategy
        spellbook = StrategyToCombatant._select_spells(vec, stats)
        
        # Equipment based on dominant stats
        equipment = StrategyToCombatant._select_equipment(vec, stats, behavioral_tag)
        
        # Resistances from defense dimension
        resistances = {
            DamageType.FIRE: defense * 0.1 + control * 0.05,
            DamageType.ICE: defense * 0.15,
            DamageType.LIGHTNING: mobility * 0.1,
            DamageType.POISON: defense * 0.1 + risk * 0.05,
            DamageType.ARCANE: control * 0.15,
            DamageType.PHYSICAL: defense * 0.1,
        }
        
        return Combatant(
            name=name,
            max_hp=max_hp,
            max_mp=max_mp,
            hp=max_hp,
            mp=max_mp,
            base_stats=stats,
            spellbook=spellbook,
            equipment=equipment,
            resistances=resistances,
            behavioral_tag=behavioral_tag,
        )
    
    @staticmethod
    def _select_spells(vec: np.ndarray, stats: Dict[str, int]) -> List[Spell]:
        """Pick spells that match the strategy vector. Algorithmic."""
        spells = []
        aggression = (vec[0] + 2) / 4
        defense = (vec[1] + 2) / 4
        control = (vec[3] + 2) / 4
        risk = (vec[6] + 2) / 4
        sustain = (vec[15] + 2) / 4
        
        # Every combatant gets a basic heal
        spells.append(SPELL_CATALOG["mend_shell"])
        
        # Aggressive → fireball, shell_crush
        if aggression > 0.5:
            spells.append(SPELL_CATALOG["fireball"])
        if aggression > 0.7 and stats["strength"] > 15:
            spells.append(SPELL_CATALOG["shell_crush"])
        
        # Control → lightning, poison
        if control > 0.5:
            spells.append(SPELL_CATALOG["lightning_strike"])
        if control > 0.6:
            spells.append(SPELL_CATALOG["abyssal_drip"])
        
        # Risk-seeking → rage_tide
        if risk > 0.6:
            spells.append(SPELL_CATALOG["rage_tide"])
        
        # Sustain focus → tidal_bind for endurance
        if sustain > 0.6:
            spells.append(SPELL_CATALOG["tidal_bind"])
        
        return spells
    
    @staticmethod
    def _select_equipment(vec: np.ndarray, stats: Dict[str, int], tag: str) -> Dict[str, Optional[Equipment]]:
        """Pick equipment matching the build."""
        eq: Dict[str, Optional[Equipment]] = {}
        aggression = (vec[0] + 2) / 4
        defense = (vec[1] + 2) / 4
        mobility = (vec[2] + 2) / 4
        control = (vec[3] + 2) / 4
        
        # Weapon: always claws for now (lyapunov = aggressive, bayesian = control)
        if aggression > control:
            eq["weapon"] = EQUIPMENT_CATALOG["claw_of_lyapunov"]
        else:
            eq["weapon"] = EQUIPMENT_CATALOG["shield_of_bayesian_belief"]
        
        # Armor: shell if defensive, nothing if pure offense
        if defense > 0.4:
            eq["armor"] = EQUIPMENT_CATALOG["shell_of_convergence"]
        
        # Boots if mobile
        if mobility > 0.6:
            eq["boots"] = EQUIPMENT_CATALOG["boots_of_momentum"]
        
        # Ring for risk-takers
        if (vec[6] + 2) / 4 > 0.5:
            eq["ring"] = EQUIPMENT_CATALOG["ring_of_deadband"]
        
        # Amulet for intelligence builds
        if stats["intelligence"] > 15:
            eq["amulet"] = EQUIPMENT_CATALOG["amulet_of_gradient_descent"]
        
        return eq


class CombatArenaBridge:
    """Wraps SelfPlayArena to add algorithmic combat matches."""
    
    def __init__(self, arena: SelfPlayArena):
        self.arena = arena
        self.combat_history: List[dict] = []
    
    def simulate_combat_match(self, player1: str, player2: str,
                               max_rounds: int = 50) -> ArenaMatch:
        """Run a match using the combat engine instead of probability."""
        p1_snap = self.arena.league[player1]
        p2_snap = self.arena.league[player2]
        
        # Build combatants from strategy vectors
        c1 = StrategyToCombatant.build(player1, p1_snap)
        c2 = StrategyToCombatant.build(player2, p2_snap)
        
        # Run algorithmic combat
        encounter = CombatEncounter(c1, c2, max_rounds=max_rounds)
        winner_name, log, rounds = encounter.run()
        
        # Map back to arena result
        if winner_name == player1:
            result = 1.0
            p1_snap.wins += 1
            p2_snap.losses += 1
        elif winner_name == player2:
            result = 0.0
            p1_snap.losses += 1
            p2_snap.wins += 1
        else:
            result = 0.5
            p1_snap.draws += 1
            p2_snap.draws += 1
        
        # Update ELO
        p1_snap.update_elo(p2_snap.elo, result, self.arena.elo_k)
        p2_snap.update_elo(p1_snap.elo, 1 - result, self.arena.elo_k)
        
        # Determine archetype from combined strategy (same as original)
        combined_strat = (p1_snap.strategy_vector + p2_snap.strategy_vector) / 2
        archetype = self.arena._classify_archetype(combined_strat)
        
        match = ArenaMatch(
            player1=player1,
            player2=player2,
            result=result,
            duration_steps=rounds,
            exploration_bonus=rounds / 50.0,
            insight_quality=len(log) / 100.0,
            behavioral_archetype=archetype,
        )
        
        self.arena.matches.append(match)
        self.arena._save_state()
        
        # Save combat log
        combat_record = {
            "match_id": len(self.arena.matches),
            "player1": player1,
            "player2": player2,
            "winner": winner_name,
            "rounds": rounds,
            "p1_build": {
                "stats": c1.base_stats,
                "equipment": {k: v.name if v else None for k, v in c1.equipment.items()},
                "spells": [s.name for s in c1.spellbook],
                "tag": c1.behavioral_tag,
            },
            "p2_build": {
                "stats": c2.base_stats,
                "equipment": {k: v.name if v else None for k, v in c2.equipment.items()},
                "spells": [s.name for s in c2.spellbook],
                "tag": c2.behavioral_tag,
            },
            "log": log,
        }
        self.combat_history.append(combat_record)
        
        # Persist combat history
        combat_dir = Path(self.arena.arena_dir) / "combat_logs"
        combat_dir.mkdir(exist_ok=True)
        (combat_dir / f"combat_{len(self.arena.matches)}.json").write_text(
            json.dumps(combat_record, indent=2)
        )
        
        return match
    
    def run_combat_training_session(self, agent_version: str, num_matches: int = 10,
                                     opponent_strategy: str = "pfsp") -> Tuple[dict, List[ArenaMatch]]:
        """Run training using algorithmic combat."""
        matches = []
        wins = 0
        
        for i in range(num_matches):
            opponent = self.arena.select_opponent(agent_version, opponent_strategy)
            match = self.simulate_combat_match(agent_version, opponent)
            matches.append(match)
            
            if match.result == 1.0:
                wins += 1
            elif match.result == 0.5:
                wins += 0.5
        
        summary = {
            "agent": agent_version,
            "matches": num_matches,
            "wins": wins,
            "win_rate": wins / num_matches,
            "avg_duration": sum(m.duration_steps for m in matches) / len(matches) if matches else 0,
            "archetypes": [m.behavioral_archetype for m in matches],
        }
        
        return summary, matches


def demo():
    """Demo: run a combat match between two arena policies."""
    from arena import SelfPlayArena
    
    arena = SelfPlayArena(Path("arena_state"))
    bridge = CombatArenaBridge(arena)
    
    # Ensure we have at least 2 snapshots
    if len(arena.league) < 2:
        arena.add_snapshot("TestA", np.random.randn(16) * 0.5)
        arena.add_snapshot("TestB", np.random.randn(16) * 0.5)
    
    versions = list(arena.league.keys())[:2]
    match = bridge.simulate_combat_match(versions[0], versions[1])
    
    print(f"Combat match: {versions[0]} vs {versions[1]}")
    print(f"Result: {match.result} (1.0 = p1 wins)")
    print(f"Rounds: {match.duration_steps}")
    print(f"Archetype: {match.behavioral_archetype}")
    
    # Print latest combat log
    if bridge.combat_history:
        latest = bridge.combat_history[-1]
        print(f"\n--- Combat Log (last {min(10, len(latest['log']))} lines) ---")
        for line in latest["log"][-10:]:
            print(line)
    
    return match


if __name__ == "__main__":
    demo()
