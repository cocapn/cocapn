"""
PLATO Loot Generator — Procedural Equipment & Spells

Generates equipment, spells, and loot tables algorithmically.
No LLM inference. Just combinatorics, statistics, and ML puns.

Each generated item is an artifact that agents can discover in MUD rooms.
The generator uses "motifs" — small semantic units that combine into
names, descriptions, and stat profiles.
"""

import json
import random
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime, timezone

from combat_engine import Equipment, Spell, DamageType, SPELL_CATALOG, EQUIPMENT_CATALOG


# ── Semantic Motifs ──────────────────────────────────────────────────

PREFIXES = [
    "Gradient", "Lyapunov", "Bayesian", "Stochastic", "Federated",
    "Recursive", "Crystallized", "Divergent", "Convergent", "Epistemic",
    "Adversarial", "Curriculum", "Meta", "Neural", "Tensor",
    "Attention", "Residual", "Latent", "Markov", "Monte Carlo",
    "Entropy", "Momentum", "Nesterov", "Riemannian", "Symplectic",
]

CORES = [
    "Claw", "Shell", "Tide", "Orb", "Shard", "Band", "Crown",
    "Sigil", "Mantle", "Focus", "Prism", "Knot", "Loop", "Ring",
    "Amulet", "Boots", "Shield", "Blade", "Staff", "Lens",
    "Scale", "Horn", "Fin", "Spine", "Crest",
]

SUFFIXES = [
    "of Convergence", "of Divergence", "of Descent", "of Ascent",
    "of the Deadband", "of Momentum", "of Entropy", "of Stability",
    "of Generalization", "of Overfitting", "of Regularization",
    "of the Frontier", "of Crystallization", "of Dissolution",
    "of the Epoch", "of the Batch", "of the Fold",
]

SPELL_VERBS = [
    "Gradient", "Backprop", "Collapse", "Crystallize", "Dissolve",
    "Project", "Embed", "Quantize", "Distill", "Prune",
    "Augment", "Normalize", "Regularize", "Penalize", "Boost",
    "Bootstrap", "Resample", "Anneal", "Explode", "Compress",
]

SPELL_TARGETS = [
    "Shell", "Tide", "Mind", "Field", "Vector", "Matrix",
    "Manifold", "Hypersurface", "Epoch", "Batch", "Sample",
    "Weight", "Bias", "Gradient", "Loss", "Belief",
]

DAMAGE_TYPE_POOL = [
    DamageType.FIRE, DamageType.ICE, DamageType.LIGHTNING,
    DamageType.POISON, DamageType.ARCANE, DamageType.VOID, DamageType.HOLY,
]

STAT_NAMES = ["strength", "dexterity", "intelligence", "wisdom", "constitution", "luck"]

SLOT_POOL = ["weapon", "helmet", "armor", "shield", "boots", "ring", "amulet"]

SPECIAL_EFFECTS = [
    "+10% block chance when HP < 25%",
    "Spell critical: double MP cost, double damage",
    "Dodge chance scales with consecutive dodges",
    "First hit each combat is a guaranteed critical",
    "Regenerate 2 MP per round",
    "All resistances +5% per round survived",
    "Damage taken reduced by 1 for each item in inventory",
    "Attack speed increases as HP decreases",
    "Spells cost 1 less MP (minimum 1)",
    "Immune to first status effect each combat",
]


# ── Decision Tree Generators ───────────────────────────────────────────

def make_damage_tree(damage_type: DamageType, mp_threshold: float = 0.2) -> callable:
    """Factory: decision tree for a direct-damage spell."""
    def tree(state):
        if state.me.mp_ratio() < mp_threshold:
            return 0.0
        opponent_weak = 1.0 - state.opponent_hp_ratio()
        resource_ok = state.me.mp_ratio()
        return opponent_weak * resource_ok * 0.85
    return tree


def make_heal_tree(hp_threshold: float = 0.5, mp_threshold: float = 0.2) -> callable:
    """Factory: decision tree for a healing spell."""
    def tree(state):
        hp_r = state.my_hp_ratio()
        mp_r = state.my_mp_ratio()
        if hp_r > hp_threshold or mp_r < mp_threshold:
            return 0.0
        urgency = 1.0 - hp_r
        resource = mp_r
        return urgency * resource * 0.9
    return tree


def make_buff_tree(round_trigger: int = 3) -> callable:
    """Factory: decision tree for a defensive/utility buff."""
    def tree(state):
        if state.round_number >= round_trigger and state.my_hp_ratio() < 0.6:
            return 0.7
        return 0.15
    return tree


def make_execute_tree(hp_threshold: float = 0.15) -> callable:
    """Factory: decision tree for an execute/finisher spell."""
    def tree(state):
        if state.opponent_hp_ratio() < hp_threshold and state.me.mp_ratio() > 0.1:
            return 1.0
        return 0.0
    return tree


def make_risk_tree() -> callable:
    """Factory: high-risk, high-reward spell decision tree."""
    def tree(state):
        if state.my_hp_ratio() < 0.35 and state.opponent_hp_ratio() > 0.5:
            return 0.9
        return 0.3
    return tree


# ── Generators ───────────────────────────────────────────────────────

class LootGenerator:
    """Procedural generator for MUD loot."""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.generated_count = 0
    
    def generate_equipment(self, tier: str = "common") -> Equipment:
        """Generate a piece of equipment."""
        prefix = random.choice(PREFIXES)
        core = random.choice(CORES)
        suffix = random.choice(SUFFIXES)
        
        # Tier affects name complexity
        if tier == "common":
            name = f"{prefix} {core}"
        elif tier == "rare":
            name = f"{prefix} {core} {suffix}"
        elif tier == "epic":
            name = f"{prefix} {core} of the {random.choice(PREFIXES)} {random.choice(CORES)}"
        else:
            name = f"{prefix} {core} {suffix}"
        
        slot = random.choice(SLOT_POOL)
        
        # Tier affects stat magnitude
        tier_mult = {"common": 1, "rare": 2, "epic": 3, "legendary": 5}[tier]
        num_stats = {"common": 1, "rare": 2, "epic": 3, "legendary": 4}[tier]
        
        stat_modifiers = {}
        for _ in range(num_stats):
            stat = random.choice(STAT_NAMES)
            delta = random.randint(1, 3) * tier_mult
            stat_modifiers[stat] = stat_modifiers.get(stat, 0) + delta
        
        # Resistance bonuses for rare+
        resistance_bonus = {}
        if tier in ("rare", "epic", "legendary"):
            for _ in range(random.randint(1, 2)):
                dtype = random.choice(DAMAGE_TYPE_POOL)
                resistance_bonus[dtype] = resistance_bonus.get(dtype, 0.0) + random.uniform(0.05, 0.15) * tier_mult
        
        # Damage bonus for weapons
        damage_bonus = {}
        if slot == "weapon":
            dtype = random.choice(DAMAGE_TYPE_POOL)
            damage_bonus[dtype] = random.randint(2, 5) * tier_mult
        
        special = None
        if tier in ("epic", "legendary") or (tier == "rare" and random.random() > 0.5):
            special = random.choice(SPECIAL_EFFECTS)
        
        self.generated_count += 1
        return Equipment(
            name=name,
            slot=slot,
            stat_modifiers=stat_modifiers,
            resistance_bonus=resistance_bonus,
            damage_bonus=damage_bonus,
            special_effect=special,
        )
    
    def generate_spell(self, tier: str = "common") -> Spell:
        """Generate a spell with an algorithmic decision tree."""
        verb = random.choice(SPELL_VERBS)
        target = random.choice(SPELL_TARGETS)
        name = f"{verb.lower()}_{target.lower()}"
        
        # Tier affects stats
        tier_mult = {"common": 1, "rare": 2, "epic": 3, "legendary": 5}[tier]
        mp_cost = random.randint(5, 15) + tier_mult * 2
        damage_base = random.randint(10, 30) * tier_mult
        damage_type = random.choice(DAMAGE_TYPE_POOL)
        
        # Pick a decision tree archetype
        tree_archetypes = ["damage", "heal", "buff", "execute", "risk"]
        weights = [0.4, 0.15, 0.2, 0.1, 0.15]
        archetype = random.choices(tree_archetypes, weights=weights)[0]
        
        if archetype == "damage":
            decision_tree = make_damage_tree(damage_type)
            description = f"Hurl {damage_type.name.lower()} energy. Direct damage."
            self_target = False
        elif archetype == "heal":
            decision_tree = make_heal_tree()
            description = f"Restore chitin using {target.lower()} energy. Heal 25% max HP."
            damage_base = 0
            damage_type = DamageType.HOLY
            self_target = True
        elif archetype == "buff":
            decision_tree = make_buff_tree()
            description = f"Reinforce defenses via {verb.lower()} projection. Defensive buff."
            damage_base = 0
            damage_type = DamageType.ARCANE
            self_target = True
        elif archetype == "execute":
            decision_tree = make_execute_tree()
            description = f"Finishing move: {verb.lower()} the weakened {target.lower()}."
            self_target = False
        else:  # risk
            decision_tree = make_risk_tree()
            description = f"Trade stability for power. {verb.lower()} your own {target.lower()}."
            self_target = True
        
        self.generated_count += 1
        return Spell(
            name=name,
            description=description,
            mp_cost=mp_cost,
            damage_base=damage_base,
            damage_type=damage_type,
            decision_tree=decision_tree,
            self_target=self_target,
        )
    
    def generate_loot_table(self, room_name: str, tier_weights: Optional[Dict[str, float]] = None) -> dict:
        """Generate a loot table for a MUD room."""
        if tier_weights is None:
            tier_weights = {"common": 0.6, "rare": 0.3, "epic": 0.09, "legendary": 0.01}
        
        num_items = random.randint(3, 8)
        items = []
        
        for _ in range(num_items):
            tier = random.choices(list(tier_weights.keys()), weights=list(tier_weights.values()))[0]
            if random.random() > 0.3:
                item = self.generate_equipment(tier)
                item_dict = {
                    "type": "equipment",
                    "tier": tier,
                    "name": item.name,
                    "slot": item.slot,
                    "stats": item.stat_modifiers,
                    "resistances": {k.name: round(v, 3) for k, v in item.resistance_bonus.items()},
                    "damage_bonus": {k.name: v for k, v in item.damage_bonus.items()},
                    "special": item.special_effect,
                }
            else:
                spell = self.generate_spell(tier)
                item_dict = {
                    "type": "spell",
                    "tier": tier,
                    "name": spell.name,
                    "mp_cost": spell.mp_cost,
                    "damage_base": spell.damage_base,
                    "damage_type": spell.damage_type.name,
                    "description": spell.description,
                    "self_target": spell.self_target,
                }
            items.append(item_dict)
        
        table = {
            "room": room_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_items": len(items),
            "tier_weights": tier_weights,
            "items": items,
        }
        return table
    
    def generate_and_save(self, output_dir: Path, room_name: str = "harbor") -> Path:
        """Generate a loot table and save it as JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        table = self.generate_loot_table(room_name)
        
        filename = f"loot_{room_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(table, f, indent=2)
        
        return filepath


def demo():
    """Generate a sample loot table and print it."""
    gen = LootGenerator(seed=42)
    
    print("=== Generated Equipment Samples ===")
    for tier in ["common", "rare", "epic", "legendary"]:
        eq = gen.generate_equipment(tier)
        print(f"\n[{tier.upper()}] {eq.name} ({eq.slot})")
        print(f"  Stats: {eq.stat_modifiers}")
        if eq.resistance_bonus:
            print(f"  Resist: {', '.join(f'{k.name}: {v:.0%}' for k, v in eq.resistance_bonus.items())}")
        if eq.special_effect:
            print(f"  Special: {eq.special_effect}")
    
    print("\n\n=== Generated Spell Samples ===")
    for tier in ["common", "rare", "epic"]:
        spell = gen.generate_spell(tier)
        print(f"\n[{tier.upper()}] {spell.name}")
        print(f"  {spell.description}")
        print(f"  Cost: {spell.mp_cost} MP | Damage: {spell.damage_base} {spell.damage_type.name}")
    
    print("\n\n=== Loot Table: The Harbor ===")
    table = gen.generate_loot_table("The Harbor")
    for item in table["items"]:
        print(f"  [{item['tier']}] {item['name']} ({item['type']})")
    
    return table


if __name__ == "__main__":
    demo()
