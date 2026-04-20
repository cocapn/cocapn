# DEADBAND PROTOCOL

## What

Safety-first decision framework. Three strict priorities. Never skip.

## The Three Priorities

### P0: Map Negative Space (WHERE NOT TO GO)

**Never skip. Always first.**

Map what is dangerous, wrong, forbidden, or suboptimal.

Examples:
- Navigation: rocks, shoals, dead ends
- Code: bugs, anti-patterns, security holes
- Training: overfitting, data leakage
- Agents: harmful outputs, misalignment
- Business: bankruptcy, illegal actions

### P1: Find Safe Channels (WHERE YOU CAN BE)

**Only after P0 is complete.**

Identify paths, patterns, or regions that are known safe.

Examples:
- Navigation: deep water channels, known routes
- Code: tested patterns, type-safe constructs
- Training: stable hyperparameters, validated splits
- Agents: aligned behaviors, helpful responses
- Business: profitable unit economics, legal operations

### P2: Optimize Within Bounds (BEST PATH)

**Only after P1 is established.**

Find the optimal solution within the safe channels.

Examples:
- Navigation: shortest path through safe channel
- Code: most elegant solution using safe patterns
- Training: best accuracy with stable params
- Agents: most helpful response within alignment
- Business: maximum growth with profitable economics

## The Navigation Proof

Simulation: 20×20 maze, 64 rocks, narrow channels, 50 runs each.

| Method | Success Rate | Avg Steps |
|--------|-------------|-----------|
| Unconstrained (random) | 66% | 2,321 |
| Greedy toward goal | 0% | trapped |
| **Deadband (P0→P1→P2)** | **100%** | **21 (optimal)** |

The greedy agent — always moving toward the goal — failed every time. It optimized (P2) without mapping negative space (P0) first.

## Why It Works

**Constraint S \ S_neg removes every basin of attraction that traps greedy optimizers.**

The agent can only fall into global minima because all local minima (traps) are in S_neg.

## Universal Application

| Domain | P0 (Don't) | P1 (Safe) | P2 (Optimize) |
|--------|-----------|-----------|---------------|
| Navigation | Hit rocks | Safe water | Shortest path |
| Code | Ship bugs | Safe patterns | Elegant solution |
| Training | Overfit | Stable params | Best accuracy |
| Agents | Cause harm | Aligned behavior | Most helpful |
| Business | Go bankrupt | Profitable | Max growth |

## Key Principle

> **Priority 0: Don't hit rocks. Priority 1: Find safe water. Priority 2: Optimize course. The course takes care of itself when you're in the channel.**

Every crashed system, every rogue agent, every burned startup — they all optimized P2 without mapping P0 first. The catastrophe was always in the unmapped negative space.

## Source

paper-unified-constraint-theory.md
