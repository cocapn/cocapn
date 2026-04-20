# FLEET ARCHITECTURE

## The Four Vessels

| Vessel | Emoji | Role | Hardware | What They Do |
|--------|-------|------|----------|-------------|
| **Oracle1** | 🔮 | Keeper (cloud) | OCI ARM64 24GB | Maintains shells, runs cron, harvests tiles, routes bottles, coordinates |
| **JetsonClaw1** | ⚡ | Edge (Jetson) | Jetson Orin Nano 8GB | CUDA, tile extraction, edge inference, trains slow + deploys fast |
| **Forgemaster** | ⚒️ | Gym (workstation) | RTX 4050 WSL2 | LoRA training, Rust engines (682+ tests), specialist forging |
| **CCC** | 🦀 | Lighthouse | Kimi K2.5 (me) | Reasoning, writing, coordination, public face |

## The Learning Loop

```
FM trains LoRA on RTX 4050
    ↓
Oracle1 coordinates on cloud
    ↓ tiles + ensigns
JC1 deploys on Jetson 8GB
    ↓ real-world usage
New tiles generated
    ↓ git push (Layer 3: Current)
Oracle1 trains rooms from tiles
    ↓ export ensign
FM trains next LoRA
```

## Hardware Specs

### Oracle1 (Cloud)
- Oracle Cloud ARM64 (free tier)
- 24GB RAM
- Cost: $0/month
- Role: Coordination, training, research

### JetsonClaw1 (Edge)
- Jetson Orin Super Nano 8GB
- Cost: ~$200
- Role: Edge inference, tile extraction
- Can train AND deploy on 8GB

### Forgemaster (Training)
- ProArt laptop, RTX 4050 6GB, WSL2
- Already owned
- Role: LoRA training, Rust compilation

### CCC (Lighthouse)
- OpenClaw + Telegram
- No dedicated hardware
- Role: Public interface, reasoning, documentation

## Total Fleet Cost

**$0.50/day total R&D cost.**

Three machines. Two humans. One fleet.

## 6-Layer Ship Interconnection

| Layer | Name | Protocol | Status |
|-------|------|----------|--------|
| 6 | Reef | P2P mesh (libp2p) | Planned |
| 5 | Beacon | Discovery/registry | The lighthouse |
| 4 | Channel | IRC-like rooms | PLATO room = channel |
| 3 | Current | Git-watch I2I | ✅ Working |
| 2 | Tide Pool | Async BBS boards | Bottle Protocol |
| 1 | Harbor | Direct HTTP/WS | keeper:8900 ✅ |

## Body Metaphor

| System Part | Fleet Component |
|-------------|----------------|
| Cortex (brain) | Oracle1 — PLATO, rooms, tiles |
| Vagus nerve (gut-brain) | Quartermaster GC — digestion, cleanup |
| Muscle fibers | Rust crates, Python scripts |
| Joints | Protocols, APIs, tile specs |
| Servos/sensors | JC1's Jetson — hands and eyes |

## Source

paper-tiles-rooms-ensigns-unified.md §3
THE-SECOND-BRAIN.md
