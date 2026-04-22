"""
Tests for PLATO Combat Engine — using unittest (stdlib, no pytest needed).

Run: python3 plato/test_combat_engine.py
"""

import unittest
from combat_engine import (
    Combatant, Spell, Equipment, CombatRound, CombatEncounter,
    CombatState, ActionType, DamageType, SPELL_CATALOG, EQUIPMENT_CATALOG,
    _heal_tree, _fireball_tree, _finish_tree,
)


class TestSpellDecisionTrees(unittest.TestCase):
    def test_heal_tree_low_hp(self):
        p1 = Combatant(name="A", hp=20, max_hp=100, mp=50, max_mp=50)
        p2 = Combatant(name="B", hp=100, max_hp=100)
        state = CombatState(me=p1, opponent=p2, round_number=2)
        score = _heal_tree(state)
        self.assertGreater(score, 0.5)

    def test_heal_tree_full_hp(self):
        p1 = Combatant(name="A", hp=100, max_hp=100, mp=50, max_mp=50)
        p2 = Combatant(name="B", hp=100, max_hp=100)
        state = CombatState(me=p1, opponent=p2, round_number=2)
        score = _heal_tree(state)
        self.assertEqual(score, 0.0)

    def test_heal_tree_no_mp(self):
        p1 = Combatant(name="A", hp=10, max_hp=100, mp=5, max_mp=50)
        p2 = Combatant(name="B", hp=100, max_hp=100)
        state = CombatState(me=p1, opponent=p2, round_number=2)
        score = _heal_tree(state)
        self.assertEqual(score, 0.0)

    def test_fireball_tree_weak_opponent(self):
        p1 = Combatant(name="A", hp=100, max_hp=100, mp=50, max_mp=50)
        p2 = Combatant(name="B", hp=10, max_hp=100)
        state = CombatState(me=p1, opponent=p2, round_number=2)
        score = _fireball_tree(state)
        self.assertGreater(score, 0.7)

    def test_finish_tree_triggers_at_low_hp(self):
        p1 = Combatant(name="A", hp=100, max_hp=100, mp=20, max_mp=50)
        p2 = Combatant(name="B", hp=5, max_hp=100)
        state = CombatState(me=p1, opponent=p2, round_number=5)
        score = _finish_tree(state)
        self.assertEqual(score, 1.0)

    def test_finish_tree_no_trigger(self):
        p1 = Combatant(name="A", hp=100, max_hp=100, mp=20, max_mp=50)
        p2 = Combatant(name="B", hp=50, max_hp=100)
        state = CombatState(me=p1, opponent=p2, round_number=5)
        score = _finish_tree(state)
        self.assertEqual(score, 0.0)


class TestEquipment(unittest.TestCase):
    def test_claw_modifiers(self):
        eq = EQUIPMENT_CATALOG["claw_of_lyapunov"]
        base = {"strength": 10, "dexterity": 10}
        result = eq.apply(base)
        self.assertEqual(result["strength"], 15)
        self.assertEqual(result["dexterity"], 12)

    def test_shell_resistance(self):
        eq = EQUIPMENT_CATALOG["shell_of_convergence"]
        self.assertEqual(eq.resistance_bonus[DamageType.FIRE], 0.15)
        self.assertEqual(eq.resistance_bonus[DamageType.ICE], 0.25)

    def test_combatant_effective_stats(self):
        c = Combatant(
            name="Test",
            base_stats={"strength": 10, "intelligence": 10},
            equipment={"weapon": EQUIPMENT_CATALOG["claw_of_lyapunov"]},
        )
        stats = c.effective_stats
        self.assertEqual(stats["strength"], 15)
        self.assertEqual(stats["intelligence"], 10)


class TestCombatant(unittest.TestCase):
    def test_hp_ratio(self):
        c = Combatant(name="T", hp=50, max_hp=100)
        self.assertEqual(c.hp_ratio, 0.5)

    def test_can_cast_with_mp(self):
        c = Combatant(name="T", mp=20, max_mp=50)
        spell = SPELL_CATALOG["fireball"]
        self.assertTrue(c.can_cast(spell))

    def test_cannot_cast_without_mp(self):
        c = Combatant(name="T", mp=5, max_mp=50)
        spell = SPELL_CATALOG["fireball"]
        self.assertFalse(c.can_cast(spell))

    def test_cannot_cast_on_cooldown(self):
        c = Combatant(name="T", mp=50, max_mp=50)
        spell = SPELL_CATALOG["fireball"]
        c.cooldowns["fireball"] = 2
        self.assertFalse(c.can_cast(spell))

    def test_tick_cooldowns(self):
        c = Combatant(name="T")
        c.cooldowns["fireball"] = 3
        c.tick_cooldowns()
        self.assertEqual(c.cooldowns["fireball"], 2)


class TestCombatRound(unittest.TestCase):
    def test_aggressive_prefers_attack(self):
        p1 = Combatant(
            name="Aggro", hp=100, max_hp=100, mp=50, max_mp=50,
            spellbook=[SPELL_CATALOG["fireball"]],
            behavioral_tag="aggressive",
        )
        p2 = Combatant(name="Target", hp=100, max_hp=100)
        state = CombatState(me=p1, opponent=p2, round_number=1)
        cr = CombatRound(1)
        action = cr._decide(p1, state)
        self.assertIn(action.action_type, (ActionType.ATTACK, ActionType.CAST))

    def test_defensive_prefers_defend_when_low(self):
        p1 = Combatant(
            name="Turtle", hp=20, max_hp=100, mp=50, max_mp=50,
            behavioral_tag="defensive",
        )
        p2 = Combatant(name="Target", hp=100, max_hp=100)
        state = CombatState(me=p1, opponent=p2, round_number=3)
        cr = CombatRound(3)
        action = cr._decide(p1, state)
        self.assertTrue(action.action_type == ActionType.DEFEND or action.score > 0.4)

    def test_combat_resolves(self):
        p1 = Combatant(
            name="A", hp=100, max_hp=100, mp=50, max_mp=50,
            spellbook=[SPELL_CATALOG["fireball"]],
            behavioral_tag="balanced",
        )
        p2 = Combatant(
            name="B", hp=100, max_hp=100, mp=50, max_mp=50,
            spellbook=[SPELL_CATALOG["mend_shell"]],
            behavioral_tag="balanced",
        )
        cr = CombatRound(1)
        p1, p2, log = cr.resolve(p1, p2)
        self.assertGreaterEqual(len(log), 2)
        self.assertTrue(p1.hp != 100 or p2.hp != 100)


class TestCombatEncounter(unittest.TestCase):
    def test_combat_has_winner(self):
        p1 = Combatant(
            name="Winner", hp=200, max_hp=200, mp=50, max_mp=50,
            spellbook=[SPELL_CATALOG["fireball"]],
            base_stats={"strength": 20, "intelligence": 20},
            behavioral_tag="aggressive",
        )
        p2 = Combatant(
            name="Loser", hp=50, max_hp=50, mp=10, max_mp=10,
            behavioral_tag="balanced",
        )
        enc = CombatEncounter(p1, p2, max_rounds=20)
        winner, log, rounds = enc.run()
        self.assertIsNotNone(winner)
        self.assertLessEqual(rounds, 20)
        self.assertGreater(len(log), 0)

    def test_damage_calculated(self):
        p1 = Combatant(
            name="S", hp=100, max_hp=100, mp=50, max_mp=50,
            base_stats={"strength": 15},
        )
        p2 = Combatant(name="T", hp=100, max_hp=100)
        cr = CombatRound(1)
        dmg = cr._calculate_attack_damage(p1, p2)
        self.assertGreater(dmg, 0)
        self.assertIsInstance(dmg, int)

    def test_combat_state_dict(self):
        p1 = Combatant(name="A", hp=100, max_hp=100)
        p2 = Combatant(name="B", hp=80, max_hp=100)
        enc = CombatEncounter(p1, p2, max_rounds=5)
        winner, _, _ = enc.run()
        d = enc.to_dict()
        self.assertEqual(d["p1"], "A")
        self.assertEqual(d["p2"], "B")
        self.assertIn("winner", d)
        self.assertIn("rounds", d)


class TestSpellDamage(unittest.TestCase):
    def test_fireball_damage(self):
        spell = SPELL_CATALOG["fireball"]
        stats = {"intelligence": 20, "wisdom": 10}
        resists = {DamageType.FIRE: 0.0}
        dmg = spell.calculate_damage(stats, resists)
        self.assertGreater(dmg, 35)

    def test_resistance_reduces_damage(self):
        spell = SPELL_CATALOG["fireball"]
        stats = {"intelligence": 10, "wisdom": 10}
        resists = {DamageType.FIRE: 0.50}
        dmg = spell.calculate_damage(stats, resists)
        self.assertLess(dmg, 35)

    def test_lightning_variance(self):
        spell = SPELL_CATALOG["lightning_strike"]
        stats = {"intelligence": 10, "wisdom": 10}
        resists = {}
        dmg = spell.calculate_damage(stats, resists)
        self.assertGreaterEqual(dmg, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
