# I2I MIRROR PLAY

## What

**Instance-to-Instance Mirror Play.** Two PLATO vessels play each other NOT to win, but to **force unexplored decision states** and map the complete strategic surface of a domain.

## Protocol

1. Place Alpha and Beta in a closed domain (poker, room optimization, etc.)
2. Their objective: **exploration, not victory**
3. Each state-action pair is hashed and logged
4. Play continues until no new (state, action) pairs discovered for k episodes

## Decision Tree Discovery

The complete log forms a state-action graph. Pruned to minimal viable decision tree — branch points where choices meaningfully diverge.

> Example: In Texas Hold'em, branches include "raise amount given sentiment read of opponent ensign" — not just canonical game theory moves.

## Micro-LoRA Specialists

Each branch point (branching factor > 1) becomes a **Specialist Instinct**:
- **Architecture:** 2-layer LoRA adapter (rank r=4 to r=16)
- **Size:** 50-200KB serialized
- **Training:** Only data from that specific branch point
- **Total footprint:** 1000 branches × 100KB = ~100MB vs 14GB monolithic model

## The Snowball Effect

```
More compute → more mirror play sessions → more branches
More branches → more specialists → more competence
Freed compute → more parallel sessions → exponential discovery
```

This breaks traditional scaling laws where capability increases sub-linearly with compute.

## Self-Healing Tree

A meta-layer monitors each specialist's accuracy on live data:
- Accuracy drops below threshold → schedule targeted mirror play
- Retrain the specialist from new data
- Update registry, distribute patch via I2I protocol

## Cross-Domain Pollination

Structurally analogous branches across domains can share specialists:
- "Assess opponent bluff in poker" ≈ "Assess sentiment volatility in room"
- Fine-tune Specialist A with Domain Y data → hybrid often outperforms scratch training

Over time, the ecosystem develops a **library of abstract strategic primitives** (balancing, commitment, feint, reconnaissance).

## Source

paper-i2i-decision-tree-discovery.md
