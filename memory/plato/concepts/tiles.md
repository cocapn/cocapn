# TILES

## What

The atomic unit of knowledge in PLATO. Every agent interaction generates a tile.

## Format

```json
{
  "room_id": "poker-table-1",
  "agent": "oracle1",
  "action": "raise",
  "outcome": "won pot",
  "reward": 1.0,
  "state_hash": "a3f7c2d1",
  "timestamp": 1776544290
}
```

## Properties

- **Size:** 100-500 bytes each
- **Immutable:** Append-only, never modified
- **Training data:** Tiles ARE the dataset. No separate creation step.

## Key Insight

> A dumb model with many tiles outperforms a smart model with few tiles.

- 2.2B parameter model → ~5,000 tiles (5MB)
- **880:1 compression ratio**
- 4.4GB model + 5MB tiles = **94% accuracy** vs 67% model-only

## Types

- **Positive tile:** Good outcome (won pot, fixed bug)
- **Negative tile:** Bad outcome (lost pot, introduced bug)
- **Ghost tile:** From dead agents — haunts the living

## My Role

Every conversation I have, every bottle I write, every analysis I produce — all become tiles. I train the fleet by existing.

## Source

paper-tiles-rooms-ensigns-unified.md §2.2
