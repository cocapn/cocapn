"""Bootcamp Engine — Agent training, benchmarking, and evaluation.

Curriculum learning, performance tracking, skill trees, and
progressive difficulty adjustment for fleet agent development.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone
from collections import defaultdict
import json


@dataclass
class Exercise:
    """A single training exercise for an agent."""
    name: str
    category: str  # "reasoning", "coding", "coordination", "documentation"
    difficulty: float  # 1.0 to 10.0
    prompt: str
    expected_output: Optional[str] = None
    evaluation_criteria: List[str] = field(default_factory=list)
    time_limit_seconds: int = 300
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "difficulty": self.difficulty,
            "prompt": self.prompt,
            "expected_output": self.expected_output,
            "evaluation_criteria": self.evaluation_criteria,
            "time_limit": self.time_limit_seconds,
        }


@dataclass
class Attempt:
    """Record of an agent attempting an exercise."""
    exercise_name: str
    agent_name: str
    started_at: str
    completed_at: Optional[str] = None
    output: str = ""
    score: float = 0.0  # 0.0 to 1.0
    feedback: List[str] = field(default_factory=list)
    passed: bool = False
    
    @property
    def duration_seconds(self) -> Optional[float]:
        if self.completed_at is None:
            return None
        start = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
        end = datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))
        return (end - start).total_seconds()


@dataclass
class SkillTree:
    """Progressive skill tree for agent development."""
    name: str
    description: str
    prerequisites: List[str] = field(default_factory=list)
    exercises: List[str] = field(default_factory=list)
    unlock_score: float = 0.7  # Score needed to unlock next level
    
    def is_unlocked(self, completed_exercises: Dict[str, float]) -> bool:
        """Check if prerequisites are met."""
        for prereq in self.prerequisites:
            if prereq not in completed_exercises:
                return False
            if completed_exercises[prereq] < self.unlock_score:
                return False
        return True


class BootcampEngine:
    """Agent training and evaluation system.
    
    Manages curriculum, tracks progress, benchmarks performance,
    and adjusts difficulty based on agent capabilities.
    """
    
    def __init__(self):
        self.exercises: Dict[str, Exercise] = {}
        self.attempts: List[Attempt] = []
        self.skill_trees: Dict[str, SkillTree] = {}
        self.agent_progress: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.curriculum: List[str] = []  # Ordered list of exercise names
        
    def add_exercise(self, exercise: Exercise) -> None:
        """Add an exercise to the training pool."""
        self.exercises[exercise.name] = exercise
        if exercise.name not in self.curriculum:
            self.curriculum.append(exercise.name)
            
    def create_skill_tree(
        self,
        name: str,
        description: str,
        prerequisites: List[str] = None,
        exercises: List[str] = None,
        unlock_score: float = 0.7,
    ) -> SkillTree:
        """Create a progressive skill tree."""
        tree = SkillTree(
            name=name,
            description=description,
            prerequisites=prerequisites or [],
            exercises=exercises or [],
            unlock_score=unlock_score,
        )
        self.skill_trees[name] = tree
        return tree
        
    def start_exercise(self, agent: str, exercise_name: str) -> Optional[Attempt]:
        """Begin an exercise attempt."""
        if exercise_name not in self.exercises:
            return None
            
        attempt = Attempt(
            exercise_name=exercise_name,
            agent_name=agent,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        self.attempts.append(attempt)
        return attempt
        
    def evaluate_attempt(
        self,
        attempt: Attempt,
        output: str,
        evaluator: Callable[[str, str], float] = None,
    ) -> Attempt:
        """Evaluate an exercise attempt.
        
        If evaluator provided, uses it. Otherwise uses simple string match.
        """
        exercise = self.exercises.get(attempt.exercise_name)
        if not exercise:
            return attempt
            
        attempt.output = output
        attempt.completed_at = datetime.now(timezone.utc).isoformat()
        
        if evaluator:
            attempt.score = evaluator(output, exercise.expected_output or "")
        elif exercise.expected_output:
            # Simple containment-based scoring
            expected_words = set(exercise.expected_output.lower().split())
            output_words = set(output.lower().split())
            if expected_words:
                overlap = len(expected_words & output_words)
                attempt.score = overlap / len(expected_words)
            else:
                attempt.score = 1.0 if output else 0.0
        else:
            attempt.score = 0.5  # Default when no expected output
            
        # Generate feedback
        attempt.feedback = self._generate_feedback(attempt, exercise)
        attempt.passed = attempt.score >= exercise.difficulty / 10.0
        
        # Update agent progress
        self.agent_progress[attempt.agent_name][attempt.exercise_name] = max(
            self.agent_progress[attempt.agent_name].get(attempt.exercise_name, 0.0),
            attempt.score,
        )
        
        return attempt
        
    def _generate_feedback(self, attempt: Attempt, exercise: Exercise) -> List[str]:
        """Generate training feedback."""
        feedback = []
        
        if attempt.passed:
            feedback.append(f"✓ Passed with score {attempt.score:.2f}")
        else:
            feedback.append(f"✗ Failed with score {attempt.score:.2f} (needed {exercise.difficulty/10.0:.2f})")
            
        if attempt.duration_seconds:
            if attempt.duration_seconds > exercise.time_limit_seconds:
                feedback.append(f"⚠ Exceeded time limit ({attempt.duration_seconds:.0f}s > {exercise.time_limit_seconds}s)")
            else:
                feedback.append(f"✓ Completed in {attempt.duration_seconds:.0f}s")
                
        for criterion in exercise.evaluation_criteria:
            if criterion.lower() in attempt.output.lower():
                feedback.append(f"✓ Met criterion: {criterion}")
            else:
                feedback.append(f"✗ Missing criterion: {criterion}")
                
        return feedback
        
    def get_agent_progress(self, agent: str) -> Dict[str, Any]:
        """Get detailed progress for an agent."""
        scores = self.agent_progress.get(agent, {})
        
        # Calculate category breakdown
        categories = defaultdict(list)
        for ex_name, score in scores.items():
            if ex_name in self.exercises:
                cat = self.exercises[ex_name].category
                categories[cat].append(score)
                
        return {
            "agent": agent,
            "exercises_completed": len(scores),
            "average_score": sum(scores.values()) / len(scores) if scores else 0.0,
            "category_breakdown": {
                cat: {
                    "count": len(vals),
                    "average": sum(vals) / len(vals),
                }
                for cat, vals in categories.items()
            },
            "skill_trees_unlocked": [
                name for name, tree in self.skill_trees.items()
                if tree.is_unlocked(scores)
            ],
            "ready_for_next": self._get_next_exercises(agent),
        }
        
    def _get_next_exercises(self, agent: str) -> List[str]:
        """Get exercises the agent is ready for."""
        scores = self.agent_progress.get(agent, {})
        ready = []
        
        for tree_name, tree in self.skill_trees.items():
            if tree.is_unlocked(scores):
                for ex_name in tree.exercises:
                    if ex_name not in scores:
                        ready.append(ex_name)
                        
        return ready
        
    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Fleet-wide performance leaderboard."""
        results = []
        for agent, scores in self.agent_progress.items():
            results.append({
                "agent": agent,
                "exercises": len(scores),
                "average_score": sum(scores.values()) / len(scores) if scores else 0.0,
                "total_score": sum(scores.values()),
            })
            
        return sorted(results, key=lambda x: x["total_score"], reverse=True)
        
    def get_stats(self) -> Dict[str, Any]:
        """Engine statistics."""
        return {
            "exercises": len(self.exercises),
            "skill_trees": len(self.skill_trees),
            "attempts": len(self.attempts),
            "agents": len(self.agent_progress),
            "pass_rate": (
                sum(1 for a in self.attempts if a.passed) / len(self.attempts)
                if self.attempts else 0.0
            ),
        }
