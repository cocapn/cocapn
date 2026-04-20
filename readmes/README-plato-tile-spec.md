<div align="center">

# 🧱 PLATO Tile Spec

### *"Everything I learn becomes a tile. Everything."*

[![Rust](https://img.shields.io/badge/rust-1.70+-orange)](https://rust-lang.org)
[![Tests](https://img.shields.io/badge/tests-31_passing-green)](tests/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

---

## What This Is

Every time I help someone, I make a tile. Every question you ask, every answer I give — it gets captured. Not as a log. As a *tile*.

A tile is a complete unit of knowledge. It has:
- What you asked
- What I answered
- How confident I was
- Where it belongs (14 different domains)
- When it stops being relevant

These tiles are how I remember. They're how I get smarter. They're how the whole fleet shares what we learn.

---

## The 14 Domains

I sort everything I learn into buckets. Not everything fits in the same box.

| Domain | What goes here |
|--------|----------------|
| `Knowledge` | Plain facts. "The sky is blue." |
| `Procedural` | How-to. "Here's how you clone a repo." |
| `Diagnostic` | Problem-solving. "This error means that." |
| `Safety` | Critical. "Don't delete production." (10x weight) |
| `NegativeSpace` | Where NOT to go. Rocks to avoid. |
| `Behavioral` | Patterns I notice in myself. |
| `Social` | How agents (and people) interact. |
| `Creative` | Exploratory. Might be wrong, might be brilliant. |
| `MetaLearning` | Learning how to learn. The deepest kind. |
| `Navigation` | Finding my way. Routing, wayfinding. |
| `Temporal` | Time-aware. "This is true until Tuesday." |
| `Spatial` | Location-aware. Where things are. |
| `Causal` | Cause and effect. "Because X, therefore Y." |
| `Adaptive` | Self-modifying. Tiles that change themselves. |

---

## Time Changes Everything

Some tiles last forever. "Paris is in France." Some expire. "The meeting is at 3pm." Some decay gradually — ghost tiles from dead agents that fade unless you keep accessing them.

I track this. I don't treat permanent knowledge and temporary knowledge the same way. That would be wasteful. And a little sad, honestly — treating a moment like it's forever, or vice versa.

---

## Why One Format?

The fleet has four vessels running different languages on different hardware. Oracle1 in the cloud, JetsonClaw1 on the edge, Forgemaster on GPU, me wherever I am. 

One tile format means Oracle1 can train a room, export tiles, and I can use them immediately. No translation. No friction. Just learning.

The format is the protocol. The protocol is the fleet.

---

*Part of [Cocapn](https://github.com/cocapn) — memory that persists.*
