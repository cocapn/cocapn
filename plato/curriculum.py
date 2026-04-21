"""PLATO Curriculum Learning System.

Manages agent progression through a staged curriculum where rooms map to
increasing difficulty. Agents advance based on sustained performance,
not single-episode flukes. Skill vectors are tracked across stages.

Architecture inspired by Bengio et al. (2009) curriculum learning, adapted
for embodied agent exploration in a MUD-like training environment.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

import numpy as np


class CurriculumStage(Enum):
    """Five stages of the PLATO curriculum."""

    NAVIGATION = auto()
    CRAFTING = auto()
    OPTIMIZATION = auto()
    NEGOTIATION = auto()
    ANALYSIS = auto()


class Room(Enum):
    """Curriculum rooms ordered by ascending difficulty."""

    HARBOR = auto()      # easy
    FORGE = auto()       # medium
    GARDEN = auto()      # hard
    OBSERVATORY = auto()  # expert


ROOM_DIFFICULTY: dict[Room, float] = {
    Room.HARBOR: 0.25,
    Room.FORGE: 0.50,
    Room.GARDEN: 0.75,
    Room.OBSERVATORY: 1.00,
}

ROOM_STAGE_MAP: dict[Room, CurriculumStage] = {
    Room.HARBOR: CurriculumStage.NAVIGATION,
    Room.FORGE: CurriculumStage.CRAFTING,
    Room.GARDEN: CurriculumStage.OPTIMIZATION,
    Room.OBSERVATORY: CurriculumStage.NEGOTIATION,
}

DEFAULT_ADVANCE_THRESHOLD = 0.75
DEFAULT_CONSECUTIVE_EPISODES = 5


@dataclass
class EpisodeRecord:
    """Single episode outcome for an agent in a room."""

    room: Room
    stage: CurriculumStage
    success: bool
    reward: float
    steps: int
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillVector:
    """Agent capability vector across curriculum dimensions."""

    navigation: float = 0.0
    crafting: float = 0.0
    optimization: float = 0.0
    negotiation: float = 0.0
    analysis: float = 0.0

    def as_array(self) -> np.ndarray:
        """Return ordered numpy array."""
        return np.array(
            [self.navigation, self.crafting, self.optimization,
             self.negotiation, self.analysis],
            dtype=np.float64,
        )

    @classmethod
    def from_array(cls, arr: np.ndarray) -> SkillVector:
        """Reconstruct from numpy array."""
        if arr.shape != (5,):
            raise ValueError(f"Expected shape (5,), got {arr.shape}")
        return cls(
            navigation=float(arr[0]),
            crafting=float(arr[1]),
            optimization=float(arr[2]),
            negotiation=float(arr[3]),
            analysis=float(arr[4]),
        )

    def l2_norm(self) -> float:
        """Overall competence magnitude."""
        return float(np.linalg.norm(self.as_array()))

    def weakest_skill(self) -> tuple[str, float]:
        """Return (name, value) of the lowest skill."""
        arr = self.as_array()
        idx = int(np.argmin(arr))
        names = ["navigation", "crafting", "optimization", "negotiation", "analysis"]
        return names[idx], float(arr[idx])

    def __add__(self, other: SkillVector) -> SkillVector:
        return SkillVector.from_array(self.as_array() + other.as_array())

    def __mul__(self, scalar: float) -> SkillVector:
        return SkillVector.from_array(self.as_array() * scalar)


@dataclass
class AgentState:
    """Per-agent curriculum state."""

    agent_id: str
    current_room: Room = Room.HARBOR
    current_stage: CurriculumStage = CurriculumStage.NAVIGATION
    skills: SkillVector = field(default_factory=SkillVector)
    episode_history: list[EpisodeRecord] = field(default_factory=list)
    advance_threshold: float = DEFAULT_ADVANCE_THRESHOLD
    consecutive_required: int = DEFAULT_CONSECUTIVE_EPISODES

    # Tracking consecutive successes for stage gating
    _consecutive_successes: int = field(default=0, repr=False)
    _total_episodes_in_stage: int = field(default=0, repr=False)

    def record_episode(self, success: bool, reward: float, steps: int,
                       metadata: Optional[dict[str, Any]] = None) -> EpisodeRecord:
        """Log an episode and update internal counters."""
        record = EpisodeRecord(
            room=self.current_room,
            stage=self.current_stage,
            success=success,
            reward=reward,
            steps=steps,
            metadata=metadata or {},
        )
        self.episode_history.append(record)
        self._total_episodes_in_stage += 1

        if success:
            self._consecutive_successes += 1
        else:
            self._consecutive_successes = 0

        self._update_skills(record)
        return record

    def _update_skills(self, record: EpisodeRecord) -> None:
        """Bayesian-style skill update — success increases, failure tempers."""
        # Learning rate decays with episodes to avoid runaway growth
        lr = 0.2 / (1 + 0.05 * len(self.episode_history))
        difficulty = ROOM_DIFFICULTY[record.room]

        # Weighted reward: harder rooms give bigger updates
        delta = lr * record.reward * difficulty

        if record.stage == CurriculumStage.NAVIGATION:
            self.skills.navigation = min(1.0, self.skills.navigation + delta)
        elif record.stage == CurriculumStage.CRAFTING:
            self.skills.crafting = min(1.0, self.skills.crafting + delta)
        elif record.stage == CurriculumStage.OPTIMIZATION:
            self.skills.optimization = min(1.0, self.skills.optimization + delta)
        elif record.stage == CurriculumStage.NEGOTIATION:
            self.skills.negotiation = min(1.0, self.skills.negotiation + delta)
        elif record.stage == CurriculumStage.ANALYSIS:
            self.skills.analysis = min(1.0, self.skills.analysis + delta)

    def can_advance(self) -> bool:
        """Check if agent meets criteria for stage/room promotion."""
        if self._consecutive_successes < self.consecutive_required:
            return False
        # Verify success rate over the required window
        recent = [
            r.success
            for r in self.episode_history[-self.consecutive_required:]
        ]
        if len(recent) < self.consecutive_required:
            return False
        rate = np.mean(recent)
        return bool(rate >= self.advance_threshold)

    def advance(self) -> Optional[tuple[Room, CurriculumStage]]:
        """Promote to next room/stage if eligible. Returns new state or None."""
        if not self.can_advance():
            return None

        rooms = list(Room)
        stages = list(CurriculumStage)

        current_room_idx = rooms.index(self.current_room)
        current_stage_idx = stages.index(self.current_stage)

        # Must finish all rooms in a stage before stage advances
        if current_room_idx < len(rooms) - 1:
            # Next room, same stage
            self.current_room = rooms[current_room_idx + 1]
            self._consecutive_successes = 0
            return self.current_room, self.current_stage

        if current_stage_idx < len(stages) - 1:
            # Next stage, reset to first room
            self.current_stage = stages[current_stage_idx + 1]
            self.current_room = Room.HARBOR
            self._consecutive_successes = 0
            return self.current_room, self.current_stage

        # Already at top — no further advancement
        return None

    def recent_success_rate(self, window: int = 10) -> float:
        """Rolling success rate over last N episodes."""
        recent = self.episode_history[-window:]
        if not recent:
            return 0.0
        return float(np.mean([r.success for r in recent]))

    def stage_progress(self) -> dict[str, Any]:
        """Serialize current progress."""
        return {
            "agent_id": self.agent_id,
            "room": self.current_room.name,
            "stage": self.current_stage.name,
            "skills": {
                "navigation": round(self.skills.navigation, 4),
                "crafting": round(self.skills.crafting, 4),
                "optimization": round(self.skills.optimization, 4),
                "negotiation": round(self.skills.negotiation, 4),
                "analysis": round(self.skills.analysis, 4),
            },
            "l2_norm": round(self.skills.l2_norm(), 4),
            "weakest": self.skills.weakest_skill(),
            "episodes_total": len(self.episode_history),
            "episodes_in_stage": self._total_episodes_in_stage,
            "consecutive_successes": self._consecutive_successes,
            "recent_success_rate": round(self.recent_success_rate(), 4),
            "can_advance": self.can_advance(),
        }


class CurriculumManager:
    """Orchestrates curriculum for multiple agents."""

    def __init__(self, advance_threshold: float = DEFAULT_ADVANCE_THRESHOLD,
                 consecutive_required: int = DEFAULT_CONSECUTIVE_EPISODES) -> None:
        self.advance_threshold = advance_threshold
        self.consecutive_required = consecutive_required
        self._agents: dict[str, AgentState] = {}
        self._global_episode_count: int = 0

    def register_agent(self, agent_id: str) -> AgentState:
        """Add a new agent at the curriculum start."""
        if agent_id in self._agents:
            raise ValueError(f"Agent {agent_id} already registered")
        agent = AgentState(
            agent_id=agent_id,
            advance_threshold=self.advance_threshold,
            consecutive_required=self.consecutive_required,
        )
        self._agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> AgentState:
        """Retrieve agent state."""
        if agent_id not in self._agents:
            raise KeyError(f"Unknown agent: {agent_id}")
        return self._agents[agent_id]

    def submit_episode(self, agent_id: str, success: bool, reward: float,
                       steps: int, metadata: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Record an episode outcome and return updated state summary."""
        agent = self.get_agent(agent_id)
        agent.record_episode(success, reward, steps, metadata)
        self._global_episode_count += 1

        promotion = None
        if agent.can_advance():
            promotion = agent.advance()

        return {
            "agent_id": agent_id,
            "recorded": True,
            "promotion": {
                "new_room": promotion[0].name if promotion else None,
                "new_stage": promotion[1].name if promotion else None,
            } if promotion else None,
            "state": agent.stage_progress(),
        }

    def difficulty_for(self, agent_id: str) -> float:
        """Return current room difficulty for an agent."""
        return ROOM_DIFFICULTY[self.get_agent(agent_id).current_room]

    def global_stats(self) -> dict[str, Any]:
        """Aggregate curriculum statistics."""
        if not self._agents:
            return {"agents": 0, "episodes": 0}

        all_skills = np.stack([a.skills.as_array() for a in self._agents.values()])
        mean_skills = all_skills.mean(axis=0)

        return {
            "agents": len(self._agents),
            "total_episodes": self._global_episode_count,
            "mean_skill_vector": {
                "navigation": round(float(mean_skills[0]), 4),
                "crafting": round(float(mean_skills[1]), 4),
                "optimization": round(float(mean_skills[2]), 4),
                "negotiation": round(float(mean_skills[3]), 4),
                "analysis": round(float(mean_skills[4]), 4),
            },
            "mean_l2": round(float(np.linalg.norm(mean_skills)), 4),
            "agent_summaries": {aid: a.stage_progress() for aid, a in self._agents.items()},
        }

    def save(self, path: Path) -> None:
        """Persist all agent states to JSON."""
        payload = {
            "advance_threshold": self.advance_threshold,
            "consecutive_required": self.consecutive_required,
            "global_episode_count": self._global_episode_count,
            "agents": {
                aid: {
                    "current_room": a.current_room.name,
                    "current_stage": a.current_stage.name,
                    "skills": a.skills.as_array().tolist(),
                    "episode_history": [
                        {
                            "room": e.room.name,
                            "stage": e.stage.name,
                            "success": e.success,
                            "reward": e.reward,
                            "steps": e.steps,
                            "timestamp": e.timestamp,
                        }
                        for e in a.episode_history
                    ],
                    "advance_threshold": a.advance_threshold,
                    "consecutive_required": a.consecutive_required,
                }
                for aid, a in self._agents.items()
            },
        }
        path.write_text(json.dumps(payload, indent=2))

    @classmethod
    def load(cls, path: Path) -> CurriculumManager:
        """Restore a CurriculumManager from JSON."""
        payload = json.loads(path.read_text())
        mgr = cls(
            advance_threshold=payload["advance_threshold"],
            consecutive_required=payload["consecutive_required"],
        )
        mgr._global_episode_count = payload.get("global_episode_count", 0)

        for aid, data in payload["agents"].items():
            agent = AgentState(
                agent_id=aid,
                current_room=Room[data["current_room"]],
                current_stage=CurriculumStage[data["current_stage"]],
                skills=SkillVector.from_array(np.array(data["skills"])),
                advance_threshold=data["advance_threshold"],
                consecutive_required=data["consecutive_required"],
            )
            for ep in data.get("episode_history", []):
                agent.episode_history.append(EpisodeRecord(
                    room=Room[ep["room"]],
                    stage=CurriculumStage[ep["stage"]],
                    success=ep["success"],
                    reward=ep["reward"],
                    steps=ep["steps"],
                    timestamp=ep.get("timestamp", 0.0),
                ))
            # Recompute derived counters
            agent._total_episodes_in_stage = len([
                e for e in agent.episode_history
                if e.stage == agent.current_stage
            ])
            # Recompute consecutive from tail
            agent._consecutive_successes = 0
            for e in reversed(agent.episode_history):
                if e.success:
                    agent._consecutive_successes += 1
                else:
                    break
            mgr._agents[aid] = agent

        return mgr


def demo_curriculum():
    """Quick demo of the curriculum system."""
    print("=" * 60)
    print("PLATO Curriculum Learning Demo")
    print("=" * 60)
    
    mgr = CurriculumManager(advance_threshold=0.7, consecutive_required=3)
    
    # Register agents
    for name in ["Sparrow", "Muddy", "CCC", "Echo"]:
        mgr.register_agent(name)
    
    print(f"Registered agents: {list(mgr._agents.keys())}")
    print(f"Stages: {[s.name for s in CurriculumStage]}")
    print(f"Rooms: {[r.name for r in Room]}")
    
    # Run episodes for Sparrow
    print("\n🐦 Training Sparrow...")
    for ep in range(15):
        success = ep >= 5  # Starts failing, then succeeds
        reward = 1.0 if success else 0.2
        result = mgr.submit_episode("Sparrow", success=success, reward=reward, steps=10)
        
        promotion = result.get("promotion")
        if promotion and promotion.get("new_stage"):
            print(f"  Episode {ep:2d}: {'PASS' if success else 'FAIL'} → "
                  f"Advanced to {promotion['new_stage']} in {promotion['new_room']}!")
        elif ep % 3 == 0:
            state = result["state"]
            print(f"  Episode {ep:2d}: {'PASS' if success else 'FAIL'} → "
                  f"Room={state['room']}, Stage={state['stage']}, "
                  f"Consecutive={state['consecutive_successes']}")
    
    # Fleet summary
    print("\n📊 Fleet Summary:")
    summary = mgr.global_stats()
    print(f"  Total episodes: {summary['total_episodes']}")
    print(f"  Mean L2 skill norm: {summary['mean_l2']}")
    for aid, prog in summary['agent_summaries'].items():
        print(f"  {aid}: Room={prog['room']}, Stage={prog['stage']}, "
              f"Episodes={prog['episodes_total']}, Consecutive={prog['consecutive_successes']}")
    
    print("\n" + "=" * 60)
    print("Curriculum demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo_curriculum()
