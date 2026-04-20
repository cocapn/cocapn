# THE FLYWHEEL

## What

A compounding intelligence loop. Each cycle makes the next cycle better.

## The Loop

```
Zeroclaws produce tiles (every 5 min)
    ↓
PLATO server validates (deadband gate)
    ↓
Valid tiles accumulate in rooms (14 rooms)
    ↓
Room trainer synthesizes knowledge (every 60 min)
    ↓
Knowledge exports as ensigns
    ↓
Ensigns improve zeroclaw performance
    ↓
Better tiles → better ensigns → better tiles
```

## The Math

If each cycle improves quality by 10%:

| Cycle | Tiles/Day | Avg Confidence | Effective Tiles |
|-------|-----------|---------------|-----------------|
| 1 | 500 | 0.50 | 250 |
| 5 | 750 | 0.65 | 488 |
| 10 | 1000 | 0.80 | 800 |

**Cycle 10 produces 3.2× more effective knowledge than cycle 1.**

This is **compound interest applied to AI training**.

## Ensign Injection

After training, ensigns are written back to zeroclaw shells as updated IDENTITY.md or appended to STATE.md system prompts. Zeroclaws read their shell every tick.

## Current State

- **Ensigns are text prompts** (300-500 chars) — free, instant, works on any model
- **Future: LoRA adapters** — needs FM's training rig, higher quality
- Both coexist: text for CPU/edge, LoRA for GPU/cloud

## Source

trail-36-flywheel-design.md
