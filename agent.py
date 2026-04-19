#!/usr/bin/env python3
"""
Cocapn Agent — powered by Kimi K2.5. Improves every exchange.

Usage:
  python agent.py                    # Interactive chat
  python agent.py --teach "Q" "A"    # Teach it knowledge  
  python agent.py --status           # Show flywheel status
  python agent.py --test             # Run tests
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cocapn.agent import CocapnAgent


def get_api_key():
    key = os.environ.get("MOONSHOT_API_KEY", "")
    if not key:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("MOONSHOT_API_KEY="):
                        key = line.strip().split("=", 1)[1]
                        break
    return key


def interactive(agent):
    print(agent.status())
    print("\nType your message. 'quit' to exit, 'status' for stats, 'teach Q|A' to inject knowledge.\n")
    
    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n" + agent.status())
            agent.save()
            break
        
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("\n" + agent.status())
            agent.save()
            break
        if user_input.lower() == "status":
            print(agent.status())
            continue
        if user_input.lower().startswith("teach "):
            parts = user_input[6:].split("|", 1)
            if len(parts) == 2:
                print(agent.teach(parts[0].strip(), parts[1].strip()))
            else:
                print("Usage: teach question | answer")
            continue
        
        response = agent.chat(user_input)
        print(f"\nAgent> {response}\n")
        print(f"  [tiles: {agent.flywheel.store.count} | exchanges: {agent._exchange_count}]")


def main():
    if "--test" in sys.argv:
        os.execv(sys.executable, [sys.executable, "tests/test_agent.py"])
    
    if "--status" in sys.argv:
        agent = CocapnAgent(data_dir="data")
        print(agent.status())
        return
    
    if "--teach" in sys.argv:
        agent = CocapnAgent(data_dir="data")
        if len(sys.argv) >= 4:
            print(agent.teach(sys.argv[2], sys.argv[3]))
        else:
            print("Usage: python agent.py --teach \"question\" \"answer\"")
        agent.save()
        return
    
    api_key = get_api_key()
    if not api_key:
        print("No MOONSHOT_API_KEY found.")
        print("  Set it: export MOONSHOT_API_KEY=sk-your-key")
        print("  Or create .env: echo 'MOONSHOT_API_KEY=sk-your-key' > .env")
        print("  Get a key: https://platform.moonshot.cn")
        print()
        print("  Running in offline mode (no API calls, local flywheel only).")
        print()
    
    agent = CocapnAgent(api_key=api_key or "offline", data_dir="data")
    interactive(agent)


if __name__ == "__main__":
    main()
