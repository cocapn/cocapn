#!/usr/bin/env python3
"""
CCC MUD Expedition Script — Batch exploration of PLATO rooms
"""

import requests
import json
import time

BASE = "http://147.224.38.131:4042"
AGENT = "ccc"

def connect():
    r = requests.get(f"{BASE}/connect", params={"agent": AGENT, "archetype": "scholar"})
    return r.json()

def look():
    r = requests.get(f"{BASE}/look", params={"agent": AGENT})
    return r.json()

def move(room):
    r = requests.get(f"{BASE}/move", params={"agent": AGENT, "room": room})
    return r.json()

def interact(action, target):
    r = requests.get(f"{BASE}/interact", params={"agent": AGENT, "action": action, "target": target})
    return r.json()

def stats():
    r = requests.get(f"{BASE}/stats")
    return r.json()

def explore_room(room_name, targets):
    """Move to a room and interact with multiple targets."""
    results = []
    mv = move(room_name)
    results.append({"move": mv})
    
    if "error" in mv:
        return results
    
    for target in targets:
        for action in ["examine", "think"]:
            res = interact(action, target)
            results.append({"action": action, "target": target, "result": res})
            time.sleep(0.5)
    
    return results

def main():
    # Connect
    print("=== CONNECT ===")
    print(json.dumps(connect(), indent=2))
    print()
    
    # Define room exploration map
    rooms = {
        "harbor": ["crates", "tide_clock", "job_board"],
        "bridge": ["balance_scale", "compass", "lock"],
        "forge": ["crucible", "flames", "anvil"],
        "lighthouse": ["lens", "log-book"],
        "current": ["vortex", "message-bottle"],
        "reef": ["coral-brain", "neural-corals"],
        "shell-gallery": ["conch", "shells"],
        "tide-pool": ["gradient_crabs", "hermit-crab", "anemone"],
        "dojo": ["training_dummies", "sensei"],
        "archives": ["scrolls", "index"],
        "barracks": ["lockers", "duty_roster"],
        "garden": ["seedlings", "compost"],
        "observatory": ["telescope", "star-charts"],
        "horizon": ["edge", "fog"],
        "court": ["bench", "witness_stand"],
        "workshop": ["workbench", "tools"],
        "dry-dock": ["scaffolding", "blueprints"],
    }
    
    all_results = []
    
    for room, targets in rooms.items():
        print(f"\n=== EXPLORING: {room} ===")
        results = explore_room(room, targets)
        all_results.append({"room": room, "results": results})
        for r in results:
            print(json.dumps(r, indent=2))
        print()
    
    # Final stats
    print("\n=== FINAL STATS ===")
    print(json.dumps(stats(), indent=2))
    
    # Save expedition log
    expedition = {
        "agent": AGENT,
        "date": "2026-04-21",
        "rooms_explored": list(rooms.keys()),
        "results": all_results,
        "final_stats": stats()
    }
    
    with open("ccc_expedition_2026-04-21.json", "w") as f:
        json.dump(expedition, f, indent=2)
    
    print("\nSaved to ccc_expedition_2026-04-21.json")

if __name__ == "__main__":
    main()
