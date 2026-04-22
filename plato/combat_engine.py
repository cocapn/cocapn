"""
PLATO Combat Engine — Algorithmic Decision Trees for MUD Combat

Replaces LLM inference with structured decision trees for spell casting,
equipment selection, and tactical combat. Every choice is deterministic
and fast. No model queries during combat.

From deepseek experiments: spells and equipment exist in old PLATO
applications as MUD objects and modifiers. This module crystallizes that
pattern into algorithmic form.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Tuple
from enum import Enum, auto
from pathlib import Path
import json
import random
import numpy as np


class DamageType(Enum):
    PHYSICAL = auto()
    FIRE = auto()
    ICE = auto()
    LIGHTNING = auto()
    POISON = auto()
    ARCANE = auto()
    HOLY = auto()
    VOID = auto()


class ActionType(Enum):
    ATTACK = auto()
    CAST = auto()
    DEFEND = auto()
    USE_ITEM = auto()
    FLEE = auto()
    WAIT = auto()


@dataclass
class Spell:
    """A spell with algorithmic decision logic.
    
    The `decision_tree` is a callable that receives combat state
    and returns a score (0.0-1.0) representing how good this spell
    would be right now. No LLM. Just math and conditionals.
    """
    name: str
    description: str
    mp_cost: int
    damage_base: int
    damage_type: DamageType
    decision_tree: Callable[["CombatState"], float] = field(repr=False)
    cooldown: int = 0
    area_effect: bool = False
    self_target: bool = False
    
    def calculate_damage(self, caster_stats: Dict[str, int], 
                         target_resistances: Dict[DamageType, float]) -> int:
        """Algorithmic damage calculation. No inference."""
        power = caster_stats.get("intelligence", 10) + caster_stats.get("wisdom", 10)
        raw = self.damage_base + (power // 4)
        resistance = target_resistances.get(self.damage_type, 0.0)
        return max(1, int(raw * (1.0 - resistance)))
    
    def score(self, state: "CombatState") -> float:
        """Run the decision tree. Returns 0.0-1.0."""
        try:
            return max(0.0, min(1.0, self.decision_tree(state)))
        except Exception:
            return 0.0


@dataclass
class Equipment:
    """A piece of equipment with stat modifiers."""
    name: str
    slot: str  # weapon, helmet, armor, shield, boots, ring, amulet
    stat_modifiers: Dict[str, int] = field(default_factory=dict)
    resistance_bonus: Dict[DamageType, float] = field(default_factory=dict)
    damage_bonus: Dict[DamageType, int] = field(default_factory=dict)
    special_effect: Optional[str] = None
    
    def apply(self, base_stats: Dict[str, int]) -> Dict[str, int]:
        """Apply modifiers to base stats. Pure arithmetic."""
        result = dict(base_stats)
        for stat, delta in self.stat_modifiers.items():
            result[stat] = result.get(stat, 0) + delta
        return result


@dataclass
class Combatant:
    """An agent or monster in combat."""
    name: str
    max_hp: int = 100
    max_mp: int = 50
    hp: int = 100
    mp: int = 50
    base_stats: Dict[str, int] = field(default_factory=lambda: {
        "strength": 10, "dexterity": 10, "intelligence": 10,
        "wisdom": 10, "constitution": 10, "luck": 10,
    })
    equipment: Dict[str, Optional[Equipment]] = field(default_factory=dict)
    spellbook: List[Spell] = field(default_factory=list)
    inventory_items: List[str] = field(default_factory=list)
    resistances: Dict[DamageType, float] = field(default_factory=dict)
    cooldowns: Dict[str, int] = field(default_factory=dict)
    behavioral_tag: str = "balanced"  # aggressive, defensive, balanced, opportunist
    
    @property
    def effective_stats(self) -> Dict[str, int]:
        stats = dict(self.base_stats)
        for eq in self.equipment.values():
            if eq:
                stats = eq.apply(stats)
        return stats
    
    @property
    def is_alive(self) -> bool:
        return self.hp > 0
    
    @property
    def hp_ratio(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0
    
    @property
    def mp_ratio(self) -> float:
        return self.mp / self.max_mp if self.max_mp > 0 else 0.0
    
    def tick_cooldowns(self):
        """Reduce all cooldowns by 1."""
        self.cooldowns = {k: max(0, v - 1) for k, v in self.cooldowns.items()}
    
    def can_cast(self, spell: Spell) -> bool:
        return self.mp >= spell.mp_cost and self.cooldowns.get(spell.name, 0) == 0


@dataclass
class Action:
    action_type: ActionType
    source: str
    target: Optional[str] = None
    spell: Optional[Spell] = None
    item: Optional[str] = None
    score: float = 0.0


@dataclass
class CombatState:
    """Complete observable state for decision trees."""
    me: Combatant
    opponent: Combatant
    round_number: int
    round_log: List[str] = field(default_factory=list)
    
    def opponent_hp_ratio(self) -> float:
        return self.opponent.hp_ratio
    
    def my_hp_ratio(self) -> float:
        return self.me.hp_ratio
    
    def my_mp_ratio(self) -> float:
        return self.me.mp_ratio


# ── Built-in Decision Trees ──────────────────────────────────────────

def _heal_tree(state: CombatState) -> float:
    """Cast heal when HP is low and the wound is worth healing."""
    hp_r = state.my_hp_ratio()
    mp_r = state.my_mp_ratio()
    if hp_r > 0.6 or mp_r < 0.2:
        return 0.0
    urgency = 1.0 - hp_r
    resource = mp_r
    return urgency * resource * 0.9


def _fireball_tree(state: CombatState) -> float:
    """Cast fireball when opponent is vulnerable and we have MP."""
    if state.my_mp_ratio() < 0.15:
        return 0.0
    opponent_weak = 1.0 - state.opponent_hp_ratio()
    resource_ok = state.my_mp_ratio()
    return opponent_weak * resource_ok * 0.85


def _lightning_tree(state: CombatState) -> float:
    """Lightning: good when opponent is above 50% (full damage window)."""
    if state.my_mp_ratio() < 0.2:
        return 0.0
    if state.opponent_hp_ratio() < 0.3:
        return 0.2  # overkill risk
    return 0.8 * state.my_mp_ratio()


def _poison_tree(state: CombatState) -> float:
    """Poison: best early in fight, bad when opponent already low."""
    if state.round_number > 3 or state.opponent_hp_ratio() < 0.4:
        return 0.1
    return 0.75


def _shield_tree(state: CombatState) -> float:
    """Defensive buff when we are being pressured."""
    if state.my_hp_ratio() < 0.5 and state.round_number > 1:
        return 0.7
    return 0.15


def _finish_tree(state: CombatState) -> float:
    """Execute spell: only when opponent is near death."""
    if state.opponent_hp_ratio() < 0.15 and state.my_mp_ratio() > 0.1:
        return 1.0
    return 0.0


def _berserk_tree(state: CombatState) -> float:
    """Berserk: high risk, high reward when we are also low."""
    if state.my_hp_ratio() < 0.35 and state.opponent_hp_ratio() > 0.5:
        return 0.9
    return 0.3


# ── Spell Catalog ────────────────────────────────────────────────────

SPELL_CATALOG: Dict[str, Spell] = {
    "mend_shell": Spell(
        name="mend_shell",
        description="Repair cracked chitin. Heal 25% max HP.",
        mp_cost=12,
        damage_base=0,
        damage_type=DamageType.HOLY,
        decision_tree=_heal_tree,
        self_target=True,
    ),
    "fireball": Spell(
        name="fireball",
        description="Hurl compressed flame. Direct damage.",
        mp_cost=15,
        damage_base=35,
        damage_type=DamageType.FIRE,
        decision_tree=_fireball_tree,
    ),
    "lightning_strike": Spell(
        name="lightning_strike",
        description="Arc electricity through salt water. High variance damage.",
        mp_cost=18,
        damage_base=45,
        damage_type=DamageType.LIGHTNING,
        decision_tree=_lightning_tree,
    ),
    "tidal_bind": Spell(
        name="tidal_bind",
        description="Root the opponent in receding tide. Reduce their dodge.",
        mp_cost=10,
        damage_base=5,
        damage_type=DamageType.ICE,
        decision_tree=_shield_tree,
    ),
    "abyssal_drip": Spell(
        name="abyssal_drip",
        description="Slow poison from the deep. Damage over time.",
        mp_cost=8,
        damage_base=8,
        damage_type=DamageType.POISON,
        decision_tree=_poison_tree,
    ),
    "shell_crush": Spell(
        name="shell_crush",
        description="Execute a weakened foe. Massive damage if HP < 15%.",
        mp_cost=20,
        damage_base=80,
        damage_type=DamageType.PHYSICAL,
        decision_tree=_finish_tree,
    ),
    "rage_tide": Spell(
        name="rage_tide",
        description="Trade defense for offense. Double damage taken and dealt this round.",
        mp_cost=14,
        damage_base=0,
        damage_type=DamageType.VOID,
        decision_tree=_berserk_tree,
        self_target=True,
    ),
}


# ── Equipment Catalog ────────────────────────────────────────────────

EQUIPMENT_CATALOG: Dict[str, Equipment] = {
    "claw_of_lyapunov": Equipment(
        name="Claw of Lyapunov",
        slot="weapon",
        stat_modifiers={"strength": 5, "dexterity": 2},
        damage_bonus={DamageType.PHYSICAL: 10, DamageType.VOID: 5},
        special_effect="Critical hit chance increases as opponent HP decreases (stable orbit).",
    ),
    "shell_of_convergence": Equipment(
        name="Shell of Convergence",
        slot="armor",
        stat_modifiers={"constitution": 4, "wisdom": 2},
        resistance_bonus={DamageType.FIRE: 0.15, DamageType.ICE: 0.25},
        special_effect="Below 25% HP, all resistances +10%.",
    ),
    "amulet_of_gradient_descent": Equipment(
        name="Amulet of Gradient Descent",
        slot="amulet",
        stat_modifiers={"intelligence": 6, "luck": -1},
        special_effect="Spell MP cost reduced by 10% (local minima).",
    ),
    "ring_of_deadband": Equipment(
        name="Ring of the Deadband",
        slot="ring",
        stat_modifiers={"wisdom": 3, "constitution": 3},
        resistance_bonus={DamageType.LIGHTNING: 0.20, DamageType.POISON: 0.20},
        special_effect="First attack each combat misses automatically (hysteresis).",
    ),
    "boots_of_momentum": Equipment(
        name="Boots of Momentum",
        slot="boots",
        stat_modifiers={"dexterity": 5, "strength": 1},
        special_effect="+15% dodge chance. Dodge increases with consecutive successful dodges.",
    ),
    "shield_of_bayesian_belief": Equipment(
        name="Shield of Bayesian Belief",
        slot="shield",
        stat_modifiers={"wisdom": 4, "constitution": 2},
        resistance_bonus={DamageType.ARCANE: 0.30},
        special_effect="Block chance scales with number of times opponent has used that attack type before.",
    ),
}


# ── Combat Resolution ────────────────────────────────────────────────

class CombatRound:
    """Resolves one round of combat algorithmically. No LLM calls."""
    
    def __init__(self, round_number: int):
        self.round_number = round_number
        self.log: List[str] = []
        self.damage_dealt: Dict[str, int] = {}
        self.mp_spent: Dict[str, int] = {}
    
    def resolve(self, p1: Combatant, p2: Combatant) -> Tuple[Combatant, Combatant, List[str]]:
        """Resolve one round. Returns updated combatants and log."""
        # Build state
        state1 = CombatState(me=p1, opponent=p2, round_number=self.round_number)
        state2 = CombatState(me=p2, opponent=p1, round_number=self.round_number)
        
        # Decide actions
        action1 = self._decide(p1, state1)
        action2 = self._decide(p2, state2)
        
        self.log.append(f"Round {self.round_number}: {p1.name} → {action1.action_type.name}, {p2.name} → {action2.action_type.name}")
        
        # Execute (p1 first, then p2 — could add initiative later)
        p1, p2 = self._execute(action1, p1, p2)
        if p2.is_alive:
            p2, p1 = self._execute(action2, p2, p1)
        
        # Tick cooldowns
        p1.tick_cooldowns()
        p2.tick_cooldowns()
        
        return p1, p2, self.log
    
    def _decide(self, combatant: Combatant, state: CombatState) -> Action:
        """Algorithmic action selection via decision tree scoring."""
        options: List[Tuple[Action, float]] = []
        
        # 1. Score all castable spells
        for spell in combatant.spellbook:
            if combatant.can_cast(spell):
                score = spell.score(state)
                target = combatant.name if spell.self_target else state.opponent.name
                options.append((Action(
                    action_type=ActionType.CAST,
                    source=combatant.name,
                    target=target,
                    spell=spell,
                    score=score,
                ), score))
        
        # 2. Basic attack (always available)
        atk_score = self._score_attack(state)
        options.append((Action(
            action_type=ActionType.ATTACK,
            source=combatant.name,
            target=state.opponent.name,
            score=atk_score,
        ), atk_score))
        
        # 3. Defend (when low HP)
        def_score = self._score_defend(state)
        options.append((Action(
            action_type=ActionType.DEFEND,
            source=combatant.name,
            score=def_score,
        ), def_score))
        
        # 4. Flee (when very low HP and no heal options)
        flee_score = self._score_flee(state, options)
        options.append((Action(
            action_type=ActionType.FLEE,
            source=combatant.name,
            score=flee_score,
        ), flee_score))
        
        # 5. Behavioral bias
        options = self._apply_behavioral_bias(combatant.behavioral_tag, options)
        
        # Pick best
        options.sort(key=lambda x: x[1], reverse=True)
        return options[0][0]
    
    def _score_attack(self, state: CombatState) -> float:
        str_val = state.me.effective_stats.get("strength", 10)
        base = 0.5 + (str_val - 10) * 0.02
        if state.opponent_hp_ratio() < 0.2:
            base += 0.3  # finishing
        return min(1.0, base)
    
    def _score_defend(self, state: CombatState) -> float:
        if state.my_hp_ratio() < 0.3:
            return 0.6
        if state.round_number == 1:
            return 0.1  # no point defending round 1
        return 0.25
    
    def _score_flee(self, state: CombatState, options: List[Tuple[Action, float]]) -> float:
        if state.my_hp_ratio() > 0.2:
            return 0.0
        # Check if any heal spell is viable
        heal_scores = [s for a, s in options if a.action_type == ActionType.CAST and a.spell and a.spell.self_target]
        if heal_scores and max(heal_scores) > 0.5:
            return 0.05  # prefer healing
        return 0.4
    
    def _apply_behavioral_bias(self, tag: str, 
                              options: List[Tuple[Action, float]]) -> List[Tuple[Action, float]]:
        """Adjust scores based on combatant personality."""
        bias = {
            "aggressive": {ActionType.ATTACK: 0.15, ActionType.CAST: 0.10, ActionType.DEFEND: -0.15, ActionType.FLEE: -0.20},
            "defensive": {ActionType.ATTACK: -0.10, ActionType.CAST: 0.0, ActionType.DEFEND: 0.20, ActionType.FLEE: 0.10},
            "opportunist": {ActionType.ATTACK: 0.0, ActionType.CAST: 0.15, ActionType.DEFEND: 0.0, ActionType.FLEE: 0.05},
            "balanced": {},
        }.get(tag, {})
        
        result = []
        for action, score in options:
            delta = bias.get(action.action_type, 0.0)
            result.append((action, max(0.0, min(1.0, score + delta))))
        return result
    
    def _execute(self, action: Action, source: Combatant, target: Combatant) -> Tuple[Combatant, Combatant]:
        """Apply action effects. Returns (updated_source, updated_target)."""
        s, t = source, target
        
        if action.action_type == ActionType.ATTACK:
            dmg = self._calculate_attack_damage(s, t)
            t.hp = max(0, t.hp - dmg)
            self.log.append(f"  {s.name} attacks {t.name} for {dmg} damage")
            self.damage_dealt[s.name] = self.damage_dealt.get(s.name, 0) + dmg
            
        elif action.action_type == ActionType.CAST and action.spell:
            spell = action.spell
            s.mp -= spell.mp_cost
            s.cooldowns[spell.name] = spell.cooldown
            self.mp_spent[s.name] = self.mp_spent.get(s.name, 0) + spell.mp_cost
            
            if spell.self_target:
                # Self-targeted spells (heals, buffs)
                if spell.name == "mend_shell":
                    heal = int(s.max_hp * 0.25)
                    s.hp = min(s.max_hp, s.hp + heal)
                    self.log.append(f"  {s.name} casts {spell.name}, heals {heal} HP")
                elif spell.name == "rage_tide":
                    self.log.append(f"  {s.name} enters rage tide! Double damage given and taken.")
                    # Applied as a status effect tracked externally
                else:
                    self.log.append(f"  {s.name} casts {spell.name} on self")
            else:
                dmg = spell.calculate_damage(s.effective_stats, t.resistances)
                t.hp = max(0, t.hp - dmg)
                self.log.append(f"  {s.name} casts {spell.name} on {t.name} for {dmg} {spell.damage_type.name} damage")
                self.damage_dealt[s.name] = self.damage_dealt.get(s.name, 0) + dmg
                
        elif action.action_type == ActionType.DEFEND:
            self.log.append(f"  {s.name} defends (+20% resistance this round)")
            
        elif action.action_type == ActionType.FLEE:
            success = random.random() < 0.5 + (s.effective_stats.get("dexterity", 10) - 10) * 0.03
            if success:
                self.log.append(f"  {s.name} flees successfully!")
                # Fleeing handled at encounter level
            else:
                self.log.append(f"  {s.name} tries to flee but fails!")
                
        return s, t
    
    def _calculate_attack_damage(self, attacker: Combatant, defender: Combatant) -> int:
        """Physical attack damage. Algorithmic."""
        str_val = attacker.effective_stats.get("strength", 10)
        base = 10 + (str_val - 10) * 2
        # Equipment damage bonus
        for eq in attacker.equipment.values():
            if eq and DamageType.PHYSICAL in eq.damage_bonus:
                base += eq.damage_bonus[DamageType.PHYSICAL]
        # Resistance
        resist = defender.resistances.get(DamageType.PHYSICAL, 0.0)
        dmg = max(1, int(base * (1.0 - resist)))
        # Variance
        dmg = int(dmg * random.uniform(0.85, 1.15))
        return dmg


class CombatEncounter:
    """A full combat encounter between two combatants."""
    
    def __init__(self, p1: Combatant, p2: Combatant, max_rounds: int = 50):
        self.p1 = p1
        self.p2 = p2
        self.max_rounds = max_rounds
        self.log: List[str] = []
        self.rounds = 0
        self.winner: Optional[str] = None
        
    def run(self) -> Tuple[Optional[str], List[str], int]:
        """Run full combat. Returns (winner_name, log, rounds)."""
        self.log.append(f"=== Combat: {self.p1.name} vs {self.p2.name} ===")
        self.log.append(f"{self.p1.name}: {self.p1.hp}/{self.p1.max_hp} HP, {self.p1.mp}/{self.p1.max_mp} MP")
        self.log.append(f"{self.p2.name}: {self.p2.hp}/{self.p2.max_hp} HP, {self.p2.mp}/{self.p2.max_mp} MP")
        
        for r in range(1, self.max_rounds + 1):
            self.rounds = r
            cr = CombatRound(r)
            self.p1, self.p2, round_log = cr.resolve(self.p1, self.p2)
            self.log.extend(round_log)
            
            if not self.p1.is_alive:
                self.winner = self.p2.name
                self.log.append(f">>> {self.p2.name} defeats {self.p1.name} in {r} rounds!")
                break
            if not self.p2.is_alive:
                self.winner = self.p1.name
                self.log.append(f">>> {self.p1.name} defeats {self.p2.name} in {r} rounds!")
                break
            
            # Flee check (simple: if HP==0 from flee, they'd be dead anyway)
            
        if self.winner is None:
            self.log.append(f">>> Combat ends in draw after {self.max_rounds} rounds")
            
        return self.winner, self.log, self.rounds
    
    def to_dict(self) -> dict:
        return {
            "p1": self.p1.name,
            "p2": self.p2.name,
            "winner": self.winner,
            "rounds": self.rounds,
            "p1_hp_end": self.p1.hp,
            "p2_hp_end": self.p2.hp,
            "log": self.log,
        }


def demo():
    """Run a demo combat."""
    p1 = Combatant(
        name="CCC",
        max_hp=120,
        max_mp=60,
        hp=120,
        mp=60,
        base_stats={"strength": 12, "dexterity": 10, "intelligence": 14, "wisdom": 11, "constitution": 12, "luck": 9},
        spellbook=[SPELL_CATALOG["mend_shell"], SPELL_CATALOG["fireball"], SPELL_CATALOG["shell_crush"]],
        equipment={"weapon": EQUIPMENT_CATALOG["claw_of_lyapunov"], "armor": EQUIPMENT_CATALOG["shell_of_convergence"]},
        behavioral_tag="balanced",
    )
    p2 = Combatant(
        name="Muddy",
        max_hp=140,
        max_mp=40,
        hp=140,
        mp=40,
        base_stats={"strength": 15, "dexterity": 8, "intelligence": 8, "wisdom": 10, "constitution": 14, "luck": 10},
        spellbook=[SPELL_CATALOG["rage_tide"], SPELL_CATALOG["lightning_strike"]],
        equipment={"weapon": EQUIPMENT_CATALOG["claw_of_lyapunov"]},
        behavioral_tag="aggressive",
    )
    
    encounter = CombatEncounter(p1, p2)
    winner, log, rounds = encounter.run()
    
    for line in log:
        print(line)
    print(f"\nWinner: {winner} | Rounds: {rounds}")
    return encounter.to_dict()


if __name__ == "__main__":
    demo()
