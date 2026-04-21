"""Tests for Mirror Recorder observation replay."""
import pytest
from mirror_recorder.core import MirrorRecorder, Observation, Session


class TestMirrorRecorder:
    def test_start_and_record(self):
        mr = MirrorRecorder()
        session = mr.start_session("ccc")
        
        assert session.agent == "ccc"
        assert session.observation_count == 0
        
        mr.record(session.session_id, "think", "harbor")
        assert session.observation_count == 1
        
    def test_replay(self):
        mr = MirrorRecorder()
        session = mr.start_session("ccc")
        
        for i in range(5):
            mr.record(session.session_id, "think", f"room-{i}")
            
        replay = mr.replay(session.session_id)
        assert len(replay) == 5
        assert replay[0].target == "room-0"
        assert replay[4].target == "room-4"
        
    def test_replay_range(self):
        mr = MirrorRecorder()
        session = mr.start_session("ccc")
        
        for i in range(10):
            mr.record(session.session_id, "move", f"room-{i}")
            
        replay = mr.replay(session.session_id, from_index=3, to_index=7)
        assert len(replay) == 4
        assert replay[0].target == "room-3"
        
    def test_replay_at_timestamp(self):
        mr = MirrorRecorder()
        session = mr.start_session("ccc")
        
        mr.record(session.session_id, "think", "harbor")
        obs = mr.record(session.session_id, "think", "bridge")
        
        result = mr.replay_at(session.session_id, obs.timestamp)
        assert result is not None
        assert result.target == "bridge"
        
    def test_fork_session(self):
        mr = MirrorRecorder()
        session = mr.start_session("ccc")
        
        for i in range(5):
            mr.record(session.session_id, "think", f"room-{i}")
            
        new_session = mr.fork_session(session.session_id, 3, "ccc-fork-1")
        assert new_session.session_id == "ccc-fork-1"
        assert new_session.observation_count == 3
        assert new_session.metadata["forked_from"] == session.session_id
        
    def test_diff_sessions(self):
        mr = MirrorRecorder()
        
        s1 = mr.start_session("a", "session-a")
        mr.record("session-a", "think", "harbor")
        mr.record("session-a", "move", "bridge")
        
        s2 = mr.start_session("a", "session-b")
        mr.record("session-b", "think", "harbor")
        mr.record("session-b", "move", "tide-pool")
        
        diff = mr.diff_sessions("session-a", "session-b")
        assert diff["divergence_count"] == 1
        assert diff["divergences"][0]["session_a"][1] == "bridge"
        assert diff["divergences"][0]["session_b"][1] == "tide-pool"
        
    def test_search(self):
        mr = MirrorRecorder()
        s = mr.start_session("ccc")
        mr.record(s.session_id, "think", "harbor")
        mr.record(s.session_id, "create", "artifact-1")
        mr.record(s.session_id, "think", "bridge")
        
        thoughts = mr.search_observations(action="think")
        assert len(thoughts) == 2
        
        harbor = mr.search_observations(target="harbor")
        assert len(harbor) == 1
        
    def test_timeline(self):
        mr = MirrorRecorder()
        
        s1 = mr.start_session("ccc", "s1")
        mr.record("s1", "think", "a")
        
        s2 = mr.start_session("ccc", "s2")
        mr.record("s2", "think", "b")
        
        timeline = mr.get_agent_timeline("ccc")
        assert len(timeline) == 2
        assert timeline[0]["target"] == "a"
        assert timeline[1]["target"] == "b"
        
    def test_end_session(self):
        mr = MirrorRecorder()
        session = mr.start_session("ccc")
        mr.record(session.session_id, "think", "harbor")
        
        ended = mr.end_session(session.session_id)
        assert ended.ended_at is not None
        assert ended.duration_seconds is not None
        assert ended.duration_seconds >= 0
        
    def test_session_stats(self):
        mr = MirrorRecorder()
        
        for agent in ["ccc", "oracle1", "jc1"]:
            s = mr.start_session(agent)
            for _ in range(5):
                mr.record(s.session_id, "think", "test")
                
        stats = mr.get_stats()
        assert stats["sessions"] == 3
        assert stats["total_observations"] == 15
        assert stats["agents"] == 3
        
    def test_get_actions_by_type(self):
        mr = MirrorRecorder()
        s = mr.start_session("ccc")
        mr.record(s.session_id, "think", "harbor")
        mr.record(s.session_id, "create", "artifact")
        mr.record(s.session_id, "think", "bridge")
        
        thoughts = s.get_thoughts()
        assert len(thoughts) == 2
        
        creations = s.get_creations()
        assert len(creations) == 1
        
    def test_unknown_session(self):
        mr = MirrorRecorder()
        with pytest.raises(KeyError):
            mr.record("nonexistent", "think", "test")
            
    def test_buffer_limit(self):
        mr = MirrorRecorder(max_history=5)
        s = mr.start_session("ccc")
        
        for i in range(10):
            mr.record(s.session_id, "think", f"room-{i}")
            
        assert len(mr.observation_buffer) == 5
        assert mr.observation_buffer[0].target == "room-5"
        assert mr.observation_buffer[-1].target == "room-9"
