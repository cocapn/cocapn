# plato-relay

**Mycorrhizal I2I Relay**

[![Tests](https://img.shields.io/badge/tests-27_passing-green)](tests/)
[![Dependencies](https://img.shields.io/badge/deps-zero-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

Messages route through emergent **trust-weighted hop chains** instead of point-to-point. The fleet's communication topology IS its trust topology.

Like fungal mycorrhizae — no central hub, just a web of connections where nutrients (messages) flow along established paths.

---

## Core Mechanism

```rust
use plato_relay::{RelayNetwork, Message, DeliveryResult};

let mut net = RelayNetwork::new();

// Add agents with initial energy
net.add_agent(0, 10.0);  // Agent 0, 10 energy
net.add_agent(1, 10.0);  // Agent 1, 10 energy
net.add_agent(2, 10.0);  // Agent 2, 10 energy

// Establish trust relationships
net.set_trust(0, 1, 0.8);  // 0 trusts 1 at 80%
net.set_trust(1, 2, 0.9);  // 1 trusts 2 at 90%

// Send message
let msg = Message::new(0, 2, "hello");
let result = net.send(msg);

// Message routes: 0 → 1 → 2
// Trust-weighted pathfinding finds the best route
// Energy cost deducted at each hop
```

---

## Trust Dynamics

- **Boost on delivery**: Successful delivery increases trust
- **Degrade on failure**: Failed delivery decreases trust
- **Halflife decay**: Trust decays over time (configurable)
- **Spore probes**: Route discovery messages explore the network

```
Trust = f(success_rate, recency, energy_shared)
```

---

## The Bottle Protocol

Messages use the I2I Bottle format:

```markdown
# [FLEET:BOTTLE] Sender → Recipient: Subject

**From:** Agent ID
**To:** Agent ID  
**Date:** Timestamp
**Priority:** HIGH | NORMAL | LOW

---

## Content

Markdown body. Self-contained. Independently actionable.
```

---

## Integration Points

| Component | How It Connects |
|-----------|-----------------|
| plato-i2i | Messages use I2I envelope format |
| flux-trust | Trust scores from Bayesian engine |
| flux-stigmergy | Traces left at each relay hop |
| mycorrhizal-relay | Reference C implementation (Lucineer) |

---

## Why Mycorrhizal?

- **No single point of failure**: If one agent dies, routes adapt
- **Trust is earned**: Bad actors are naturally isolated
- **Topology matches reality**: Physical network topology emerges
- **Energy economics**: Spam is expensive (cost per hop)

---

## Zero Dependencies

```toml
[dependencies]
plato-relay = "0.1"
```

---

*Messages flow like nutrients through fungal networks. The forest thrives. 🍄*