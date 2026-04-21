"""Tests for Soul Forge."""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from soul_forge import SoulForge, SoulActivator, SoulVector
from soul_forge.vector import SoulDimensions, SoulMetadata


class TestSoulVector:
    def test_creation(self):
        vector = np.random.randn(256).astype(np.float32)
        meta = SoulMetadata(
            agent_name="test_agent",
            repo_hash="abc123",
            created="2026-04-21",
        )
        dims = SoulDimensions(
            temporal=np.zeros(64),
            stylistic=np.zeros(64),
            social=np.zeros(64),
            philosophical=np.zeros(64),
        )
        
        soul = SoulVector(vector, meta, dims)
        assert soul.vector.shape == (256,)
        assert soul.metadata.agent_name == "test_agent"
    
    def test_save_load(self):
        vector = np.random.randn(256).astype(np.float32)
        meta = SoulMetadata(
            agent_name="test_agent",
            repo_hash="abc123",
            created="2026-04-21",
        )
        dims = SoulDimensions(
            temporal=np.random.randn(64),
            stylistic=np.random.randn(64),
            social=np.random.randn(64),
            philosophical=np.random.randn(64),
        )
        
        soul = SoulVector(vector, meta, dims)
        
        with tempfile.NamedTemporaryFile(suffix=".soul", delete=False) as f:
            path = f.name
        
        try:
            soul.save(path)
            loaded = SoulVector.load(path)
            
            assert loaded.metadata.agent_name == "test_agent"
            assert np.allclose(loaded.vector, vector)
        finally:
            Path(path).unlink()
    
    def test_cosine_similarity(self):
        a = np.ones(256) / np.sqrt(256)
        b = np.ones(256) / np.sqrt(256)
        
        meta = SoulMetadata("a", "hash1", "2026-04-21")
        dims = SoulDimensions(np.zeros(64), np.zeros(64), np.zeros(64), np.zeros(64))
        
        soul_a = SoulVector(a, meta, dims)
        soul_b = SoulVector(b, meta, dims)
        
        assert abs(soul_a.cosine_similarity(soul_b) - 1.0) < 0.001


class TestSoulForge:
    def test_digest_empty_repo(self):
        # Create a minimal git repo for testing
        import subprocess
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=tmpdir, capture_output=True)
            
            # Create a file and commit
            Path(tmpdir, "test.txt").write_text("hello")
            subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "commit", "-m", "initial commit"], cwd=tmpdir, capture_output=True)
            
            forge = SoulForge()
            soul = forge.digest_repo(tmpdir, agent_name="test")
            
            assert soul.metadata.agent_name == "test"
            assert soul.vector.shape == (256,)
            assert soul.metadata.compression_ratio > 0


class TestSoulActivator:
    def test_activate(self):
        with tempfile.NamedTemporaryFile(suffix=".soul", delete=False) as f:
            path = f.name
        
        try:
            # Create a test soul
            vector = np.random.randn(256).astype(np.float32)
            meta = SoulMetadata("test", "hash", "2026-04-21")
            dims = SoulDimensions(np.zeros(64), np.zeros(64), np.zeros(64), np.zeros(64))
            soul = SoulVector(vector, meta, dims)
            soul.save(path)
            
            # Activate
            activator = SoulActivator()
            adapter = activator.activate(path)
            
            assert adapter.soul_name == "test"
            assert adapter.config.r == 16
            assert "test" in activator.list_active()
            
        finally:
            Path(path).unlink()
    
    def test_stack(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two test souls
            for name in ["soul_a", "soul_b"]:
                vector = np.random.randn(256).astype(np.float32)
                meta = SoulMetadata(name, "hash", "2026-04-21")
                dims = SoulDimensions(np.zeros(64), np.zeros(64), np.zeros(64), np.zeros(64))
                soul = SoulVector(vector, meta, dims)
                soul.save(str(Path(tmpdir, f"{name}.soul")))
            
            # Stack
            activator = SoulActivator()
            hybrid = activator.stack([
                str(Path(tmpdir, "soul_a.soul")),
                str(Path(tmpdir, "soul_b.soul")),
            ])
            
            assert "soul_a" in hybrid.soul_name
            assert "soul_b" in hybrid.soul_name
