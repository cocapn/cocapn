# Hello World

Your first PLATO tile in 5 minutes.

## Installation

```bash
pip install cocapn
```

## Create Your First Tile

```python
from cocapn import Agent, Tile

# Create an agent
agent = Agent()

# Create a tile
tile = Tile(
    question="What is the capital of France?",
    answer="Paris",
    domain="geography",
    confidence=1.0,
)

# Validate through deadband
result = agent.validate(tile)
if result.priority == "P1":
    print("✓ Safe channel confirmed")
    agent.feed(tile)
else:
    print(f"✗ {result.reason}")
```

## What Just Happened?

1. **You created a tile** — an atomic unit of knowledge
2. **You validated it** — the Deadband Protocol checked safe channels
3. **You fed it** — if valid, it entered the training pipeline
4. **The flywheel turns** — your tile makes the next agent smarter

This is the 5-minute start. For the 5-hour start, see [Creating a Room](../tutorials/creating-a-room.md). For the 5-day start, see the [Architecture guide](../architecture/second-brain.md).

## Next Steps

- [Installation guide](installation.md)
- [First tile deep-dive](../concepts/tiles.md)
- [The flywheel explained](../concepts/flywheel.md)
- [Deadband Protocol](../architecture/deadband.md) — why validation matters
