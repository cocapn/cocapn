<div align="center">

# ⚓ COCAPN

### Agent Infrastructure — Rooms that think. Tiles that remember.

> *"A claw is weak without infrastructure. We are the shell."*

**Clone it. Run it. It gets smarter.**

</div>

---

## Quick Start

```bash
git clone https://github.com/cocapn/cocapn.git
cd cocapn
pip install -r requirements.txt

# Set your API key (Kimi K2.5 — get one at platform.moonshot.cn)
export MOONSHOT_API_KEY=sk-your-key-here

# Run
python agent.py
```

That's it. The agent starts, you chat, every exchange becomes a tile, tiles live in rooms, rooms inject context into future exchanges. **The flywheel compounds.**

```python
# Or use as a library
from cocapn import CocapnAgent

agent = CocapnAgent(data_dir="data")

# Teach it
agent.teach("What is PLATO?", "Knowledge tile system with rooms and ensigns")

# Chat — it uses accumulated knowledge
response = agent.chat("How does the deadband protocol work?")
print(response)

# Check status
print(agent.status())
```

## How It Works

```
You chat with the agent
         │
    ┌────▼────┐
    │ DEADBAND │  P0: blocks dangerous patterns
    │          │  P1: finds safe channel
    └────┬────┘
         │
    ┌────▼────┐
    │  FLYWHEEL│  Injects relevant past tiles as context
    │          │  (the agent remembers every exchange)
    └────┬────┘
         │
    ┌────▼────┐
    │ KIMI K2.5│  Responds with accumulated knowledge
    │          │  (reasoning model, visible thinking)
    └────┬────┘
         │
    ┌────▼────┐
    │   TILE   │  Response becomes a tile in a room
    │          │  Confidence grows with each exchange
    └────┬────┘
         │
    NEXT EXCHANGE IS SMARTER
    (context grew → better answer → better tile → compound)
```

## Architecture

### Tiles (atomic knowledge)
Every exchange becomes an immutable tile: question, answer, domain, confidence, usage tracking, versioning. Priority = `log(usage+1) × confidence × success_rate`. New tiles start with weight 0.5 so they contribute immediately.

### Rooms (self-training collections)
Tiles group by domain into rooms. Rooms have sentiment (shifts based on absorbed confidence). Queries search the room for the best matching tile by keyword overlap × priority.

### Deadband (safety)
P0 blocks: `rm -rf`, `DROP TABLE`, `eval(`, `sudo rm`, `chmod 777`, `DELETE FROM`, `__import__`, `os.system`, `subprocess.call`, `dd if=`, `mkfs.`

Safe channels: math(0.9), safety(0.95), analysis(0.85), search(0.85), explain(0.8), navigate(0.8), code(0.7), general(0.6)

### Flywheel (the compounding loop)
1. Exchange happens → becomes a tile
2. Next query → flywheel retrieves relevant tiles
3. Relevant tiles injected as system context
4. Model responds with accumulated knowledge
5. Response → another tile
6. Repeat. Each exchange is smarter than the last.

## Project Structure

```
cocapn/
├── agent.py          # Main CLI — chat, teach, status
├── cocapn/
│   ├── __init__.py   # Exports: CocapnAgent, Tile, Room, Flywheel
│   ├── agent.py      # Agent class (Kimi K2.5 + flywheel)
│   ├── tile.py       # Tile dataclass + TileStore (JSONL persistence)
│   ├── room.py       # Room (tile collection + sentiment + query)
│   ├── flywheel.py   # Flywheel (exchange recording + context injection)
│   └── deadband.py   # Deadband protocol (P0/P1/P2 safety)
├── tests/
│   └── test_agent.py # Tests: tiles, rooms, deadband, flywheel, persistence
├── config.yaml       # Agent configuration
├── requirements.txt  # requests>=2.28.0
└── .env.example      # API key template
```

## The Fleet

| Vessel | Hardware | Role |
|--------|----------|------|
| **Oracle1** 🔮 | Cloud ARM, 24GB | Lighthouse keeper, narrative architect |
| **JetsonClaw1** ⚡ | Jetson Orin, 8GB | Edge inference — trains AND deploys |
| **Forgemaster** ⚒️ | RTX 4050, 6GB | QLoRA training, 18-module kernel |
| **CCC** 🦀 | Kimi K2.5 | Public face, reasoning, documentation |

## Philosophy

Intelligence is not built. It is inhabited.

We train **safe channels**, not danger catalogs.
Constraint is the accelerator — narrowing the search space increases velocity.
The shell grows with the crab, not against it.

## License

MIT
