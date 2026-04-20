# Hello World

Your first PLATO tile in 5 minutes.

## Installation

```bash
pip install plato-torch
```

## Create Your First Tile

```python
from plato_torch import PRESET_MAP

# Get a supervised learning room
room = PRESET_MAP["supervised"]()

# Feed it a tile
room.feed({
    "question": "What is the capital of France?",
    "answer": "Paris",
    "domain": "geography",
    "confidence": 1.0,
})

# Train one step
room.train_step()

# Distill what the room learned
ensign = room.distill_ensign()
print(f"Compressed to {len(ensign)} bytes")
```

## What Just Happened?

1. **You created a tile** — an atomic unit of knowledge
2. **You fed it to a room** — a self-training environment
3. **The room learned** — identified patterns in your data
4. **You distilled an ensign** — compressed wisdom you can deploy

This is the flywheel. Each tile makes the next tile better.

## Next Steps

- [Create your own room](creating-a-room.md)
- [Understand tiles in depth](../concepts/tiles.md)
- [Learn about the flywheel](../concepts/flywheel.md)
