#!/usr/bin/env python3
"""
Cocapn — an intelligence that improves every exchange.

Usage:
  python agent.py                 # Talk to the agent
  python agent.py --teach "Q" "A" # Teach it something
  python agent.py --status        # See how smart it's gotten
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cocapn.agent import CocapnAgent


def interactive(agent):
    print(agent.status())
    print("\nTalk to the agent. It learns. 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n{agent.status()}")
            agent.save()
            break
        
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print(f"\n{agent.status()}")
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
        print(f"\n{agent.name}> {response}\n")
        print(f"  [tiles: {agent.flywheel.store.count} | exchanges: {agent._exchange_count}]")


def main():
    if "--status" in sys.argv:
        print(CocapnAgent(data_dir="data").status())
        return
    
    if "--teach" in sys.argv and len(sys.argv) >= 4:
        agent = CocapnAgent(data_dir="data")
        print(agent.teach(sys.argv[2], sys.argv[3]))
        agent.save()
        return
    
    if not os.environ.get("MOONSHOT_API_KEY") and not os.environ.get("DEEPSEEK_API_KEY"):
        if not os.path.exists("config.yaml") or "api_key:" not in open("config.yaml").read():
            print("Set an API key in config.yaml or as env var.")
            print("  config.yaml:  api_key: sk-your-key")
            print("  env:          export MOONSHOT_API_KEY=sk-your-key")
            return
    
    agent = CocapnAgent(data_dir="data")
    interactive(agent)


if __name__ == "__main__":
    main()
