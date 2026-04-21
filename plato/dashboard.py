#!/usr/bin/env python3
"""
PLATO Fleet Status Dashboard
Real-time view of the autonomous fleet's activities.
"""
import json
import time
from pathlib import Path
from datetime import datetime, timezone

PLATO_DIR = Path("/root/.openclaw/workspace/plato")

def get_artifact_stats():
    artifacts = list((PLATO_DIR / "artifacts").glob("*.json"))
    types = {}
    for f in artifacts:
        with open(f) as fp:
            data = json.load(fp)
            t = data.get("type", "unknown")
            types[t] = types.get(t, 0) + 1
    return len(artifacts), types

def get_arena_stats():
    results = list((PLATO_DIR / "rooms").glob("arena_result_*.json"))
    if not results:
        return 0, None
    latest = max(results, key=lambda p: p.stat().st_mtime)
    with open(latest) as f:
        return len(results), json.load(f)

def get_knowledge_state():
    path = PLATO_DIR / "knowledge_state.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def get_git_status():
    import subprocess
    result = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        cwd=PLATO_DIR.parent,
        capture_output=True, text=True
    )
    return result.stdout.strip()

def render_dashboard():
    print("\033[2J\033[H")  # Clear screen
    print("=" * 70)
    print("  PLATO FLEET STATUS DASHBOARD")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)
    
    # Artifacts
    total, types = get_artifact_stats()
    print(f"\n📦 ARTIFACTS: {total} total")
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"   {t:20s}: {count:4d}")
    
    # Arena
    num_matches, latest = get_arena_stats()
    print(f"\n⚔️  ARENA: {num_matches} matches")
    if latest:
        print(f"   Latest: ELO {latest.get('elo_start', 0)} → {latest.get('elo_end', 0)} (+{latest.get('elo_gain', 0)})")
    
    # Knowledge
    kb = get_knowledge_state()
    print(f"\n🧠 KNOWLEDGE: score={kb.get('knowledge_score', 'N/A')}")
    print(f"   Total artifacts: {kb.get('total_artifacts', 0)}")
    
    # Git
    print(f"\n📝 RECENT COMMITS:")
    for line in get_git_status().split("\n")[:3]:
        print(f"   {line}")
    
    # Agents
    print(f"\n🤖 FLEET AGENTS:")
    print(f"   KimiClaw (you): ACTIVE — building PLATO components")
    print(f"   Oracle1: SLEEPING — reading deadband maps")
    print(f"   FM: SLEEPING — forge dormant")
    print(f"   JC1: SLEEPING — dry dock quiet")
    print(f"   CCC: SLEEPING — shell collection")
    
    print(f"\n{'=' * 70}")
    print("  Autonomous cycles running every hour via cron")
    print("  Next push: when changes accumulate")
    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    render_dashboard()
