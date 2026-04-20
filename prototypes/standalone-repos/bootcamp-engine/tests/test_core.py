"""Tests for Bootcamp Engine agent training."""
import pytest
from bootcamp_engine.core import BootcampEngine, Exercise, SkillTree, Attempt


class TestExercise:
    def test_exercise_creation(self):
        ex = Exercise(
            name="harbor-docking",
            category="coordination",
            difficulty=3.0,
            prompt="Describe how agents dock in the harbor",
            expected_output="harbor interface",
            evaluation_criteria=["harbor", "interface"],
        )
        assert ex.difficulty == 3.0
        assert ex.time_limit_seconds == 300


class TestBootcampEngine:
    def test_add_exercise(self):
        be = BootcampEngine()
        ex = Exercise("test", "reasoning", 2.0, "What is 2+2?", "4")
        be.add_exercise(ex)
        assert "test" in be.exercises
        
    def test_start_and_evaluate(self):
        be = BootcampEngine()
        be.add_exercise(Exercise(
            "hello",
            "reasoning",
            5.0,
            "Say hello",
            "hello world",
            ["hello"],
        ))
        
        attempt = be.start_exercise("ccc", "hello")
        assert attempt is not None
        assert attempt.agent_name == "ccc"
        
        be.evaluate_attempt(attempt, "hello world from ccc")
        assert attempt.score > 0.5
        assert attempt.passed
        assert len(attempt.feedback) > 0
        
    def test_evaluate_failure(self):
        be = BootcampEngine()
        be.add_exercise(Exercise(
            "fail-test",
            "reasoning",
            9.0,  # High difficulty
            "Complex task",
            "specific output",
        ))
        
        attempt = be.start_exercise("test", "fail-test")
        be.evaluate_attempt(attempt, "wrong answer")
        assert not attempt.passed
        assert attempt.score < 0.9
        
    def test_skill_tree_unlock(self):
        be = BootcampEngine()
        be.add_exercise(Exercise("basic", "reasoning", 1.0, "Q", "A"))
        be.add_exercise(Exercise("advanced", "reasoning", 5.0, "Q2", "A2"))
        
        be.create_skill_tree(
            "advanced-reasoning",
            "Advanced reasoning skills",
            prerequisites=["basic"],
            exercises=["advanced"],
        )
        
        # Complete basic with high score
        attempt = be.start_exercise("ccc", "basic")
        be.evaluate_attempt(attempt, "A")
        
        progress = be.get_agent_progress("ccc")
        assert "advanced-reasoning" in progress["skill_trees_unlocked"]
        assert "advanced" in progress["ready_for_next"]
        
    def test_category_breakdown(self):
        be = BootcampEngine()
        be.add_exercise(Exercise("r1", "reasoning", 1.0, "Q", "A"))
        be.add_exercise(Exercise("c1", "coding", 2.0, "Code", "def hello()"))
        
        a1 = be.start_exercise("ccc", "r1")
        be.evaluate_attempt(a1, "A")
        
        a2 = be.start_exercise("ccc", "c1")
        be.evaluate_attempt(a2, "def hello()")
        
        progress = be.get_agent_progress("ccc")
        assert "reasoning" in progress["category_breakdown"]
        assert "coding" in progress["category_breakdown"]
        
    def test_leaderboard(self):
        be = BootcampEngine()
        be.add_exercise(Exercise("ex", "reasoning", 1.0, "Q", "A"))
        
        for agent, answer in [("a", "A"), ("b", "A"), ("c", "wrong")]:
            attempt = be.start_exercise(agent, "ex")
            be.evaluate_attempt(attempt, answer)
            
        board = be.get_leaderboard()
        assert len(board) == 3
        assert board[0]["agent"] in ["a", "b"]  # a and b tied for first
        
    def test_stats(self):
        be = BootcampEngine()
        be.add_exercise(Exercise("ex", "reasoning", 1.0, "Q", "A"))
        
        for _ in range(5):
            attempt = be.start_exercise("ccc", "ex")
            be.evaluate_attempt(attempt, "A")
            
        stats = be.get_stats()
        assert stats["exercises"] == 1
        assert stats["attempts"] == 5
        assert stats["pass_rate"] == 1.0
        
    def test_unknown_exercise(self):
        be = BootcampEngine()
        assert be.start_exercise("ccc", "nonexistent") is None
        
    def test_custom_evaluator(self):
        be = BootcampEngine()
        be.add_exercise(Exercise("custom", "reasoning", 1.0, "Q", "A"))
        
        attempt = be.start_exercise("ccc", "custom")
        
        def custom_eval(output, expected):
            return 1.0 if "special" in output else 0.0
            
        be.evaluate_attempt(attempt, "special sauce", evaluator=custom_eval)
        assert attempt.score == 1.0
