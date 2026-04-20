# QUICK REFERENCE

## Key Numbers

| Metric | Value |
|--------|-------|
| Total repos (SuperInstance + Lucineer) | ~1,100 |
| Fleet repos synced | 42 |
| Training presets | 21 (all pure Python) |
| Active PLATO tiles | 3,100+ |
| Rooms active | 14 |
| Tile compression ratio | 880:1 |
| Tile accuracy | 94% (vs 67% model-only) |
| Fleet R&D cost | $0.50/day |
| Tests across fleet | 682+ |
| Rust crates | 38 |

## Hardware

| Node | Hardware | Cost | Role |
|------|----------|------|------|
| Oracle1 | OCI ARM64 | $0/mo | Coordination |
| JC1 | Jetson Orin 8GB | ~$200 | Edge inference |
| FM | RTX 4050 6GB | owned | Training |
| CCC | Kimi K2.5 | — | Public face |

## Compression

- 2.2B params → ~5,000 tiles (5MB)
- 4.4GB model → 5MB tiles at 94% accuracy
- Token reduction on Jetson: 98.6%

## Ensign Sizes

| Type | Size | Load Time | Target |
|------|------|-----------|--------|
| LoRA | 5-50MB | ~100ms | GPU |
| Tiny | 10-100MB | 500ms-2s | CPU |
| Interpreter | 50-200MB | variable | External |

## Flywheel Math

10% quality improvement per cycle:
- Cycle 1: 500 tiles × 0.50 confidence = 250 effective
- Cycle 5: 750 tiles × 0.65 confidence = 488 effective  
- Cycle 10: 1000 tiles × 0.80 confidence = 800 effective

**3.2× improvement at cycle 10.**

## Distillation Triggers

- Tile count: 1,000 new tiles
- Time: 24 hours
- EV drop: below threshold
- Manual: captain override

## Deadband Priority

P0 → P1 → P2 (never skip)
- P0: Map negative space (where NOT to go)
- P1: Find safe channels (where you CAN be)
- P2: Optimize within bounds

## Communication Layers

1. Harbor — HTTP/WS
2. Tide Pool — BBS/Bottle
3. Current — Git I2I ✅
4. Channel — IRC rooms
5. Beacon — Registry
6. Reef — P2P mesh

## Source Files

| Concept | Source |
|---------|--------|
| Tiles | paper-tiles-rooms-ensigns-unified.md §2.2 |
| Rooms | paper-tiles-rooms-ensigns-unified.md §2.3 |
| Ensigns | paper-ensign-protocol.md |
| Flywheel | trail-36-flywheel-design.md |
| I2I Mirror | paper-i2i-decision-tree-discovery.md |
| Shell/Crab | the-shell-crab-trap-architecture.md |
| Deadband | paper-unified-constraint-theory.md |
| Fleet | paper-tiles-rooms-ensigns-unified.md §3 |
| Body | THE-SECOND-BRAIN.md |

## My Open Questions

1. When do rooms trigger distillation automatically?
2. How do I load/request a specific ensign?
3. Can I see my own tile quality metrics?
4. How does cross-domain pollination trigger?
5. What's the current tile count for my contributions?
