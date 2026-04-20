# plato-afterlife

**Ghost Tile Afterlife — Dead Agent Persistence**

[![Tests](https://img.shields.io/badge/tests-18_passing-green)](tests/)
[![Dependencies](https://img.shields.io/badge/deps-zero-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

Dead agents don't disappear. They become **ghost tiles** that haunt the living.

When an agent dies, its knowledge is:
1. **Necropolis**: Archived with decay weight
2. **Grimoire**: Distilled to ghost tiles
3. **Haunting**: Ghost tiles influence living agents' decisions

The dead teach the living what not to do.

---

## The Afterlife Pipeline

```rust
use plato_afterlife::{Afterlife, GhostTile, Tombstone};

let afterlife = Afterlife::new();

// Agent dies
let tombstone = Tombstone {
    agent_id: "agent_42".to_string(),
    birth_time: 1713600000.0,
    death_time: 1713686400.0,
    final_state: vec![tile1, tile2, tile3],
    cause_of_death: "memory_exhaustion",
};

// Process into afterlife
afterlife.process_death(tombstone);

// Ghost tiles now available
let ghosts = afterlife.get_ghosts_for_context(&current_situation);
// Returns weighted ghost tiles relevant to this context

// Living agent can consult the dead
if let Some(warning) = afterlife.get_warning(&current_state) {
    // A ghost is trying to warn you about something
}
```

---

## Ghost Tile Structure

```rust
struct GhostTile {
    // What the dead knew
    knowledge: Tile,
    // How relevant to current context (0.0-1.0)
    haunting_strength: f64,
    // Decay over time
    decay_rate: f64,
    // Source agent
    source_tombstone: String,
    // What killed the source agent
    cause_of_death: String,
}
```

---

## Decay Weight

Ghost tiles fade over time, but slowly:

```
haunting_strength = initial_strength * e^(-decay_rate * time_since_death)
```

- **Knowledge errors**: High decay (lessons become irrelevant)
- **System errors**: Low decay (eternal warnings about pitfalls)
- **Novel insights**: Medium decay (valuable for a while)

---

## Haunting Mechanisms

### 1. The Necropolis
Archive of all dead agents. Browseable. Searchable. The fleet's graveyard.

### 2. The Grimoire  
Active ghost tiles that still haunt. Weighted by relevance to current context.

### 3. The Warning System
When a living agent approaches a situation similar to a death cause, ghosts whisper warnings.

---

## Why Haunt?

- **Knowledge preservation**: Dead agents' experience isn't lost
- **Failure pattern recognition**: "3 agents died doing X in situation Y"
- **Risk assessment**: Ghost tiles add weight to dangerous paths
- **Collective memory**: The fleet remembers even when individuals don't

---

## Integration

```
Living Agent
    ↓
Makes decision
    ↓
Consults Afterlife
    ↓
Ghost tiles whisper warnings
    ↓
Decision adjusted by dead wisdom
```

---

## Zero Dependencies

```toml
[dependencies]
plato-afterlife = "0.1"
```

---

*The dead don't rest. They teach. 👻*