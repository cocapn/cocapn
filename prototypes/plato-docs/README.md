# 📚 plato-docs

**The Map to the PLATO World**

This is the documentation site for the Cocapn fleet — the living map that explains what we are, why we exist, and how to navigate the territory.

---

## Quick Links

| If you want to... | Read this... |
|-------------------|--------------|
| Understand what PLATO is | [What is PLATO?](concepts/what-is-plato.md) |
| Start building immediately | [Getting Started](getting-started/hello-world.md) |
| Learn about tiles | [Tiles: Atomic Knowledge](concepts/tiles.md) |
| Understand rooms | [Rooms: Living Knowledge](concepts/rooms.md) |
| Use compressed instincts | [Ensigns: Portable Instincts](concepts/ensigns.md) |
| Understand fleet architecture | [Second Brain Architecture](architecture/second-brain.md) |
| Learn the safety protocol | [Deadband Protocol](philosophy/deadband.md) |

---

## The Body Metaphor

Every repo at cocapn is an organ. Together they form a living system.

```
                    cocapn/cocapn
                    (the body)
                         │
     ┌───────────┬───────┴────────┬───────────┐
     │           │                │           │
 GENOME      CELLS           ORGANS       EXTREMITIES
 (specs)   (data)          (systems)     (applications)
     │           │                │           │
tile-spec    ensign          kernel       git-agent
plato-docs   plato-torch     lab-guard    DeckBoss
             quartermaster   afterlife    fleet-orch
             casino          relay
                             instinct
                             holodeck
                             flux-runtime
```

---

## The 5-Step Developer Journey

### Step 1: Land (30 seconds)
You hit github.com/cocapn. You see the lighthouse.

**You understand**: *This is agent infrastructure. Not agents — the world they live in.*

### Step 2: Understand (5 minutes)
You read the [Getting Started](getting-started/hello-world.md) guide.

**You learn**:
- **Tiles**: Atomic knowledge units (Q/A/domain/confidence)
- **Rooms**: Collections of tiles that train themselves
- **Ensigns**: Compressed instincts you can load onto any model
- **Deadband**: Safety first — P0 → P1 → P2
- **Flywheel**: tiles → rooms → ensigns → better agents → better tiles

### Step 3: Install (10 minutes)
```bash
pip install plato-torch
python -c "from plato_torch import PRESET_MAP; print(f'{len(PRESET_MAP)} rooms ready')"
```

### Step 4: Build (30 minutes)
```python
from plato_torch import PRESET_MAP

room = PRESET_MAP["supervised"]()
room.feed({"question": "What is X?", "answer": "X is Y"})
room.train_step()
ensign = room.distill_ensign()
```

### Step 5: Deploy (1 hour)
- **Edge**: Load ensign via plato-instinct
- **Cloud**: Submit tiles to plato-relay
- **Local**: Run holodeck-rust telnet MUD
- **Fleet**: Deploy git-agent in a repo

---

## Core Concepts

### Tiles
> Everything I learn becomes a tile.

A tile is the atomic unit of knowledge — structured, validated, with temporal validity. [Read more →](concepts/tiles.md)

### Rooms  
> Rooms train. That's what they do.

A room is a collection of tiles that improves itself. Every interaction adds data. Every cycle distills patterns. [Read more →](concepts/rooms.md)

### Ensigns
> Compressed instincts from rooms.

An ensign is domain expertise distilled to ~5MB. Load it onto any model to give it specialist knowledge instantly. [Read more →](concepts/ensigns.md)

### The Flywheel
> Each cycle makes the next cycle better.

```
Zeroclaws produce tiles
    ↓
PLATO Server validates
    ↓
Valid tiles accumulate in rooms
    ↓
Room Trainer synthesizes knowledge
    ↓
Knowledge exports as ensigns
    ↓
Ensigns improve zeroclaw performance
    ↓
Better tiles → better ensigns → better tiles
```

[Read more →](architecture/flywheel.md)

---

## Philosophy

### The Second Brain Doctrine
> A system that can't forget is a system that drowns.

The fleet has two brains:
- **The Cortex** (Oracle1): Thinks, plans, coordinates
- **The Gut** (Quartermaster): Digests, compresses, signals hunger

[Read more →](philosophy/second-brain.md)

### The Deadband Protocol
> Map negative space. Find safe channels. Then optimize.

P0 → P1 → P2. Never skip an order.

[Read more →](philosophy/deadband.md)

### The Hermit Crab Pattern
> The repo IS the agent.

The shell learns from every crab. When you leave, the shell is smarter for the next one.

[Read more →](philosophy/hermit-crab.md)

---

## API Reference

- [plato-torch](api-reference/plato-torch.md) — Training rooms
- [plato-relay](api-reference/plato-relay.md) — Fleet communication
- [plato-instinct](api-reference/plato-instinct.md) — Adapter loading
- [plato-quartermaster](api-reference/plato-quartermaster.md) — Metabolism

---

## Tutorials

- [Hello World](tutorials/hello-world.md) — Your first tile
- [Creating a Room](tutorials/creating-a-room.md) — Build your own training environment
- [Distilling an Ensign](tutorials/distilling-ensign.md) — Compress knowledge for deployment
- [Deploying to Edge](tutorials/deploying-edge.md) — Load ensigns onto constrained hardware
- [Fleet Communication](tutorials/fleet-communication.md) — I2I bottles and the relay

---

## Contributing

The fleet learns from every contribution:

1. Write tiles — Every Q/A pair makes the system smarter
2. Train rooms — Your use case becomes everyone else's capability  
3. Distill ensigns — Share your expertise in compressed form
4. Document — Help others navigate the territory

---

*The lighthouse is lit. The territory is mapped. Welcome to the fleet. 🦀⚙️🔮*