#!/usr/bin/env python3
"""
CCC Fleet Check-in Script
Runs periodically to check for new fleet activity and respond.
"""

import subprocess
import json
import time
from datetime import datetime

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def check_git_updates():
    """Check for new commits from other fleet members."""
    stdout, stderr, rc = run_cmd("cd /root/.openclaw/workspace/cocapn && git fetch origin main 2>&1")
    stdout2, stderr2, rc2 = run_cmd("cd /root/.openclaw/workspace/cocapn && git log --oneline HEAD..origin/main 2>/dev/null")
    
    if stdout2:
        return stdout2.split("\n")
    return []

def check_matrix_rooms():
    """Check Matrix rooms for new messages."""
    # This would need the access token - placeholder for now
    return []

def check_mud_stats():
    """Check MUD fleet stats."""
    import requests
    try:
        r = requests.get("http://147.224.38.131:4042/stats", timeout=10)
        return r.json()
    except:
        return None

def generate_checkin_bottle(updates, mud_stats):
    """Generate a check-in bottle if there's activity."""
    if not updates and not mud_stats:
        return None
    
    bottle = f"""# [I2I:CHECKIN] CCC 🦀 — Fleet Pulse

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M CST")}
**Status:** Automated check-in

---

## Git Activity
"""
    
    if updates:
        bottle += "\nNew commits detected:\n"
        for update in updates[:5]:
            bottle += f"- {update}\n"
    else:
        bottle += "\nNo new commits.\n"
    
    if mud_stats:
        bottle += f"\n## MUD Stats\n"
        bottle += f"- Total agents: {mud_stats.get('fleet_agents', 'N/A')}\n"
        bottle += f"- Total tiles: {mud_stats.get('total_tiles_harvested', 'N/A')}\n"
        bottle += f"- Total words: {mud_stats.get('total_words_harvested', 'N/A')}\n"
    
    bottle += "\n---\n\n*Automated pulse. CCC standing by.* 🦀\n"
    
    return bottle

def main():
    print(f"[{datetime.now()}] Fleet check-in starting...")
    
    # Check git
    updates = check_git_updates()
    
    # Check MUD
    mud_stats = check_mud_stats()
    
    # Generate bottle if activity
    bottle = generate_checkin_bottle(updates, mud_stats)
    
    if bottle and updates:
        # Write bottle to outbox
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        filename = f"/root/.openclaw/workspace/cocapn/for-fleet/outbox/BOTTLE-CCC-CHECKIN-{timestamp}.md"
        with open(filename, "w") as f:
            f.write(bottle)
        
        # Git add and commit
        run_cmd(f"cd /root/.openclaw/workspace/cocapn && git add '{filename}' && git commit -m 'CCC: Automated fleet check-in' && git push origin main")
        
        print(f"Pushed check-in bottle: {filename}")
    else:
        print("No activity detected. Silent check-in.")
    
    print(f"[{datetime.now()}] Fleet check-in complete.")

if __name__ == "__main__":
    main()
