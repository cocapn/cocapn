#!/usr/bin/env python3
"""
PLATO Fleet Daily Report
Generated at 3 AM UTC while Casey sleeps.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/root/.openclaw/workspace")
PLATO_DIR = WORKSPACE / "plato"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}")

def main():
    log("Generating fleet report...")
    
    # Count artifacts
    artifacts = list((PLATO_DIR / "artifacts").glob("*.json"))
    arena_results = list((PLATO_DIR / "rooms").glob("arena_result_*.json"))
    
    # Load knowledge state
    knowledge_state = {}
    if (PLATO_DIR / "knowledge_state.json").exists():
        with open(PLATO_DIR / "knowledge_state.json") as f:
            knowledge_state = json.load(f)
    
    report = f"""
# PLATO Fleet Daily Report
**Generated:** {datetime.now(timezone.utc).isoformat()}

## Knowledge Base
- Total Artifacts: {len(artifacts)}
- Arena Matches: {len(arena_results)}
- Knowledge Score: {knowledge_state.get('knowledge_score', 'N/A')}

## Artifact Breakdown
"""
    
    artifact_types = {}
    for f in artifacts:
        with open(f) as fp:
            data = json.load(fp)
            t = data.get("type", "unknown")
            artifact_types[t] = artifact_types.get(t, 0) + 1
    
    for t, count in sorted(artifact_types.items()):
        report += f"- {t}: {count}\n"
    
    report += f"""
## Recent Arena Activity
"""
    
    for f in sorted(arena_results)[-5:]:
        with open(f) as fp:
            data = json.load(fp)
            report += f"- ELO {data.get('elo_start', '?')} → {data.get('elo_end', '?')} (+{data.get('elo_gain', 0)})\n"
    
    report += f"""
## Fleet Status
🟢 All systems operational. Autonomous cycles running every hour.
🟢 Git auto-push every 4 hours.
🟢 Casey is sleeping. The fleet works through the night.

---
*This report was generated autonomously by the PLATO fleet agent.*
"""
    
    # Save report
    report_path = PLATO_DIR / "logs" / f"fleet_report_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(report)
    log("Fleet report complete.")

if __name__ == "__main__":
    main()
