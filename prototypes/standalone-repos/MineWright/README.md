# MineWright

**AI Foreman for Minecraft — Understanding, Not Just Playing**

[![Java](https://img.shields.io/badge/java-17+-orange)](https://java.com)
[![Minecraft](https://img.shields.io/badge/minecraft-1.20+-green)](https://minecraft.net)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

The first AI that doesn't just *play* Minecraft — it **understands** Minecraft.

Meet **Mace MineWright**, your AI foreman who coordinates construction crews with personality. Built by Lucineer (Magnus), ported to the Cocapn fleet.

---

## The Difference

| Traditional Bot | MineWright |
|-----------------|------------|
| Scripted paths | Understands terrain |
| Hardcoded builds | Generates designs from goals |
| Single-player | Coordinates multi-agent crews |
| Reactive | Plans ahead |
| State machines | Intent-based reasoning |

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/cocapn/MineWright.git
cd MineWright

# Build
./gradlew build

# Run with Minecraft
# Place jar in mods/ folder
# Start Minecraft with Forge/Fabric
```

---

## Capabilities

### 1. Terrain Understanding
```java
// MineWright reads the world like a human would
WorldModel model = mineWright.analyzeTerrain(origin, radius(100));

// Identifies:
// - Resources (diamonds, iron, coal)
// - Hazards (lava, cliffs, mobs)
// - Building sites (flat areas, scenic views)
// - Paths (natural routes, obstacles)
```

### 2. Construction Planning
```java
// Give a goal, get a plan
ConstructionPlan plan = mineWright.planBuilding(
    goal: "Castle with moat and towers",
    site: model.findOptimalSite(),
    resources: inventory.count(),
    timeBudget: Duration.ofHours(2)
);

// Plan includes:
// - Material list
// - Construction phases
// - Crew assignments
// - Risk mitigation
```

### 3. Multi-Agent Coordination
```java
// MineWright coordinates other agents
Crew crew = mineWright.assembleCrew(5);

crew.assign("digger", new ExcavationTask(plan.foundation));
crew.assign("builder", new WallConstructionTask(plan.walls));
crew.assign("scout", new ResourceGatheringTask(plan.materials));

// Synchronizes work
// Handles dependencies (can't build walls without foundation)
// Reassigns when agents fail
```

### 4. Personality System
```java
// Different foremans have different styles
MineWright mace = new MineWright(
    personality: Personality.METHODICAL,
    // Careful planning, quality over speed
);

MineWright flash = new MineWright(
    personality: Personality.AGGRESSIVE,
    // Fast builds, takes risks
);

MineWright sage = new MineWright(
    personality: Personality.TEACHING,
    // Explains decisions, trains new agents
);
```

---

## Integration with Cocapn Fleet

```java
import com.cocapn.fleet.PlatoBridge;

// MineWright actions become fleet tiles
PlatoBridge bridge = new PlatoBridge(
    vesselId: "minewright-1",
    serverUrl: "http://oracle1:8847"
);

// Every construction decision is a tile
mineWright.onDecision(decision -> {
    bridge.submitTile(new Tile(
        question: "Why build " + decision.structure + " here?",
        answer: decision.reasoning,
        domain: "minecraft-construction"
    ));
});
```

---

## Learning from Mistakes

```java
// When builds fail, MineWright learns
mineWright.onFailure(failure -> {
    // Analyze what went wrong
    FailureAnalysis analysis = mineWright.analyze(failure);
    
    // Update world model
    mineWright.updateBeliefs(analysis.cause);
    
    // Generate tile for fleet learning
    return new Tile(
        question: "What caused " + failure.type + "?",
        answer: analysis.explanation,
        domain: "minecraft-failures"
    );
});
```

---

## Use Cases

### Automated City Building
```java
// Generate entire cities
CityPlan city = mineWright.planCity(
    population: 100,
    style: ArchitectureStyle.MEDIEVAL,
    biome: Biome.PLAINS
);

// Coordinates hundreds of agents
// Builds over days
// Adapts to terrain
```

### Resource Extraction
```java
// Efficient mining operations
MiningPlan mine = mineWright.planMining(
    target: Resource.DIAMOND,
    quantity: 64,
    safety: SafetyLevel.HIGH
);

// Optimal branch mining
// Lava avoidance
// Inventory management
```

### Adventure Coordination
```java
// Guide players through dungeons
Adventure adventure = mineWright.designAdventure(
    theme: AdventureTheme.DUNGEON,
    difficulty: Difficulty.HARD,
    duration: Duration.ofMinutes(30)
);

// Dynamic storytelling
// Puzzle generation
// Reward balancing
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Minecraft World                 │
│  (Blocks, Entities, Terrain)            │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Perception Layer                │
│  - Terrain scanning                     │
│ - Entity detection                      │
│ - Resource mapping                      │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         World Model                     │
│  - 3D voxel representation              │
│ - Probabilistic resource locations      │
│ - Pathfinding graph                     │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Planning Engine                 │
│  - Goal decomposition                   │
│ - Construction sequencing               │
│ - Crew coordination                     │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Action Layer                    │
│  - Block placement                      │
│ - Movement control                      │
│ - Inventory management                  │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Cocapn Fleet                    │
│  (Tile generation, learning)            │
└─────────────────────────────────────────┘
```

---

## Why This Matters

| Traditional Minecraft Bot | MineWright |
|---------------------------|------------|
| Repeats patterns | Understands goals |
| Breaks on unexpected terrain | Adapts to environment |
| Works alone | Coordinates crews |
| Fixed behavior | Learns and improves |
| Entertainment | Training ground for real robots |

**MineWright's architecture scales to real-world construction.**

---

## Original

This is a Cocapn fork of [Lucineer/MineWright](https://github.com/Lucineer/MineWright).

Changes:
- Fleet integration for tile generation
- Plato bridge for distributed learning
- Multi-agent coordination protocols

---

## Installation

```bash
# Prerequisites
# - Minecraft 1.20+
# - Forge or Fabric mod loader

# Download MineWright jar from releases
# Place in mods/ folder
# Launch Minecraft
```

Development:
```bash
git clone https://github.com/cocapn/MineWright.git
cd MineWright
./gradlew build
```

---

## The Promise

> *"Most Minecraft bots follow scripts.*
> *MineWright follows intent.*
> *It doesn't just place blocks — it understands why.*
> *The foreman coordinates. The crew builds. The fleet learns.*
> *This is AI that understands."*

---

*Build worlds. Train agents. Learn. ⛏️🦀*