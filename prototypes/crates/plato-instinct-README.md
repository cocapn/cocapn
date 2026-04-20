# plato-instinct

**Unified Instinct Engine**

[![Tests](https://img.shields.io/badge/tests-19_passing-green)](tests/)
[![Dependencies](https://img.shields.io/badge/deps-zero-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

A unified instinct engine that merges Oracle1's flux-instinct (10 instincts) with JC1's cuda-genepool (10 instincts) into **18 unique instincts with one grammar**.

The fleet had two competing instinct systems. Now there's one. Every agent uses the same grammar.

---

## The 18 Instincts

| Instinct | Level | Description |
|----------|-------|-------------|
| **Survive** | MUST | Critical — violation = death |
| **Flee** | MUST | Run from danger |
| **Guard** | SHOULD | Protect territory |
| **Perceive** | SHOULD | Gather information |
| **Navigate** | SHOULD | Find paths |
| **Cooperate** | SHOULD | Work with others |
| **Communicate** | SHOULD | Exchange information |
| **Learn** | SHOULD | Improve from experience |
| **Mourn** | CANNOT | Grieve exactly once per peer |
| **Teach** | MAY | Share knowledge (tracked) |
| **Share** | MAY | Distribute resources (tracked) |
| **Curious** | MAY | Explore unknowns (tracked) |
| **Explore** | MAY | Map territory (tracked) |
| **Evolve** | MAY | Adapt structure (tracked) |

**Shared instincts** (both systems had these independently): Survive, Cooperate

---

## Usage

```rust
use plato_instinct::InstinctEngine;

let mut engine = InstinctEngine::new();

// Feed state, get reflexes
let state = AgentState {
    threats_detected: 2,
    resources_low: true,
    peer_died: Some("peer_123".to_string()),
};

let reflexes = engine.tick(&state);
// Returns Vec<Reflex>, sorted by urgency

// Peer death notification (once-only)
if let Some(mourn) = engine.peer_died("peer_123") {
    // Mourn reflex fires exactly once per peer
}
```

---

## Why This Matters

Before plato-instinct:
- Oracle1 used flux-instinct with 10 instincts
- JC1 used cuda-genepool with 10 instincts
- They shared 2 instincts but used different grammars
- Cross-vessel coordination was broken

After plato-instinct:
- One grammar, 18 instincts
- Every vessel speaks the same instinct language
- Instincts generate constraint assertions
- plato-constraints enforces at runtime

---

## Integration

```
┌─────────────────┐
│  InstinctEngine │
│   (this crate)  │
└────────┬────────┘
         │
         ▼ generates
┌─────────────────┐
│ plato-constraints│
│  (enforcement)  │
└─────────────────┘
```

Instincts are not just suggestions — they're assertions that can be validated.

---

## Zero Dependencies

```toml
[dependencies]
plato-instinct = "0.1"
```

No tokio. No serde. No async. Just instincts.

---

*Built by Forgemaster ⚒️ for the fleet.*