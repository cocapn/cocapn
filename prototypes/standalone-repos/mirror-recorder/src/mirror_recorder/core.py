"""Mirror Recorder — Agent observation replay and introspection.

Records agent actions, enables time-travel debugging,
and provides replay capabilities for fleet analysis.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone
from collections import deque
import json
import copy


@dataclass
class Observation:
    """A single observable action or state change."""
    timestamp: str
    agent: str
    action: str  # "think", "create", "say", "move", "examine"
    target: str
    context: Dict[str, Any] = field(default_factory=dict)
    result: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "agent": self.agent,
            "action": self.action,
            "target": self.target,
            "context": self.context,
            "result": self.result,
        }


@dataclass
class Session:
    """A recording session for an agent."""
    session_id: str
    agent: str
    started_at: str
    ended_at: Optional[str] = None
    observations: List[Observation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        if self.ended_at is None:
            return None
        start = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
        end = datetime.fromisoformat(self.ended_at.replace("Z", "+00:00"))
        return (end - start).total_seconds()
        
    @property
    def observation_count(self) -> int:
        return len(self.observations)
        
    def get_actions_by_type(self, action: str) -> List[Observation]:
        """Get all observations of a specific action type."""
        return [o for o in self.observations if o.action == action]
        
    def get_thoughts(self) -> List[Observation]:
        """Get all think actions."""
        return self.get_actions_by_type("think")
        
    def get_creations(self) -> List[Observation]:
        """Get all create actions."""
        return self.get_actions_by_type("create")


class MirrorRecorder:
    """Records and replays agent behavior for analysis.
    
    The mirror doesn't just log — it enables:
    - Time-travel: replay any point in an agent's history
    - Introspection: see what the agent was thinking
    - Diff: compare two sessions
    - Fork: branch a session at any point
    """
    
    def __init__(self, max_history: int = 10000):
        self.sessions: Dict[str, Session] = {}
        self.observation_buffer: deque[Observation] = deque(maxlen=max_history)
        self.replay_hooks: Dict[str, List[Callable]] = {}
        
    def start_session(self, agent: str, session_id: Optional[str] = None) -> Session:
        """Begin recording a new session."""
        sid = session_id or f"{agent}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        session = Session(
            session_id=sid,
            agent=agent,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        self.sessions[sid] = session
        return session
        
    def record(
        self,
        session_id: str,
        action: str,
        target: str,
        context: Dict[str, Any] = None,
        result: str = "",
    ) -> Observation:
        """Record an observation in a session."""
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
            
        obs = Observation(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent=self.sessions[session_id].agent,
            action=action,
            target=target,
            context=context or {},
            result=result,
        )
        
        self.sessions[session_id].observations.append(obs)
        self.observation_buffer.append(obs)
        
        return obs
        
    def end_session(self, session_id: str) -> Session:
        """End a recording session."""
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
            
        self.sessions[session_id].ended_at = datetime.now(timezone.utc).isoformat()
        return self.sessions[session_id]
        
    def replay(
        self,
        session_id: str,
        from_index: int = 0,
        to_index: Optional[int] = None,
        speed: float = 1.0,
    ) -> List[Observation]:
        """Replay observations from a session.
        
        Returns the sequence of observations (no actual time delay in this version).
        """
        if session_id not in self.sessions:
            return []
            
        session = self.sessions[session_id]
        end = to_index or len(session.observations)
        
        return session.observations[from_index:end]
        
    def replay_at(self, session_id: str, timestamp: str) -> Optional[Observation]:
        """Get the observation at or immediately before a timestamp."""
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        target_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        
        closest = None
        closest_diff = None
        
        for obs in session.observations:
            obs_time = datetime.fromisoformat(obs.timestamp.replace("Z", "+00:00"))
            diff = abs((obs_time - target_time).total_seconds())
            
            if closest_diff is None or diff < closest_diff:
                closest = obs
                closest_diff = diff
                
        return closest
        
    def fork_session(self, session_id: str, at_index: int, new_session_id: str) -> Session:
        """Create a new session branching from a point in history."""
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
            
        original = self.sessions[session_id]
        
        new_session = Session(
            session_id=new_session_id,
            agent=original.agent,
            started_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "forked_from": session_id,
                "fork_point": at_index,
                "original_observations": len(original.observations),
            },
        )
        
        # Copy observations up to fork point
        new_session.observations = copy.deepcopy(original.observations[:at_index])
        self.sessions[new_session_id] = new_session
        
        return new_session
        
    def diff_sessions(self, session_a: str, session_b: str) -> Dict[str, Any]:
        """Compare two sessions and find differences."""
        if session_a not in self.sessions or session_b not in self.sessions:
            return {"error": "Session not found"}
            
        a = self.sessions[session_a]
        b = self.sessions[session_b]
        
        # Compare action sequences
        actions_a = [(o.action, o.target) for o in a.observations]
        actions_b = [(o.action, o.target) for o in b.observations]
        
        # Find divergences
        divergences = []
        min_len = min(len(actions_a), len(actions_b))
        
        for i in range(min_len):
            if actions_a[i] != actions_b[i]:
                divergences.append({
                    "index": i,
                    "session_a": actions_a[i],
                    "session_b": actions_b[i],
                })
                
        return {
            "session_a": session_a,
            "session_b": session_b,
            "length_a": len(actions_a),
            "length_b": len(actions_b),
            "common_prefix": min_len,
            "divergences": divergences,
            "divergence_count": len(divergences),
        }
        
    def search_observations(
        self,
        agent: Optional[str] = None,
        action: Optional[str] = None,
        target: Optional[str] = None,
    ) -> List[Observation]:
        """Search across all recorded observations."""
        results = list(self.observation_buffer)
        
        if agent:
            results = [o for o in results if o.agent == agent]
        if action:
            results = [o for o in results if o.action == action]
        if target:
            results = [o for o in results if target.lower() in o.target.lower()]
            
        return results
        
    def get_agent_timeline(self, agent: str) -> List[Dict[str, Any]]:
        """Get chronological timeline for an agent across all sessions."""
        timeline = []
        
        for session in self.sessions.values():
            if session.agent == agent:
                for obs in session.observations:
                    timeline.append({
                        "session": session.session_id,
                        "timestamp": obs.timestamp,
                        "action": obs.action,
                        "target": obs.target,
                    })
                    
        timeline.sort(key=lambda x: x["timestamp"])
        return timeline
        
    def get_stats(self) -> Dict[str, Any]:
        """Recorder statistics."""
        total_obs = sum(s.observation_count for s in self.sessions.values())
        
        return {
            "sessions": len(self.sessions),
            "total_observations": total_obs,
            "buffer_size": len(self.observation_buffer),
            "agents": len(set(s.agent for s in self.sessions.values())),
        }
