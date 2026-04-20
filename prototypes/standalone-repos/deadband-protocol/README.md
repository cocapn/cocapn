# deadband-protocol

**Train Safe Channels. Not Danger Catalogs.**

[![PyPI](https://img.shields.io/pypi/v/deadband-protocol)](https://pypi.org/project/deadband-protocol/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## The Core Insight

Most safety systems are **danger catalogs** — lists of everything that could go wrong. They grow forever. They drown the signal in noise.

The Deadband Protocol does the opposite: **map the negative space, find safe channels, then optimize.**

Like a river finding its course not by studying every rock, but by flowing where the rocks aren't.

---

## The Three Priorities

```
P0: Map Negative Space    ← Do this first, always
P1: Find Safe Channels    ← Only after P0 is clear  
P2: Optimize              ← Never before P1
```

**Never skip an order.** P2 before P1 is how systems die.

---

## How It Works

```python
from deadband_protocol import DeadbandValidator, Priority

# Initialize with your constraints
validator = DeadbandValidator(
    negative_space=["corrupted_data", "hallucination", "timeout"],
    safe_channels=["verified_tile", "consensus_3_of_5", "oracle_blessed"],
)

# Validate a tile
tile = {
    "question": "What is X?",
    "answer": "X is Y",
    "source": "verified_tile",  # ← Safe channel
}

result = validator.validate(tile)
assert result.priority == Priority.P1  # Safe to proceed
assert result.confidence > 0.7
```

---

## The Philosophy

### P0: Map Negative Space
> "Know where the rocks are, not what they look like."

Instead of cataloging infinite dangers, define the boundary: **what is definitely wrong?**

- Corrupted data (checksums fail)
- Hallucinations (no source, no verification)
- Timeouts (no response = no information)
- Contradictions (tile A says X, tile B says not-X with equal weight)

These are the **exclusion zones**. Everything outside them is potentially navigable.

### P1: Find Safe Channels
> "Flow where the rocks aren't."

Safe channels are paths with verified properties:

| Channel | Property | Confidence |
|---------|----------|------------|
| `verified_tile` | Passed signature check | 0.95 |
| `consensus_3_of_5` | 3+ vessels agree | 0.85 |
| `oracle_blessed` | Oracle1 validated | 0.90 |
| `self_consistent` | No internal contradictions | 0.75 |

**Only P1 tiles enter the training pipeline.**

### P2: Optimize
> "Now make it fast."

Once you have safe channels, optimize:
- Cache validated tiles
- Compress representations
- Parallelize safe operations

**P2 never invents new paths. It makes existing safe paths faster.**

---

## Deadband in PLATO

The PLATO Server uses deadband validation on every tile:

```
Zeroclaw produces tile
    ↓
DeadbandValidator checks:
    - Is this in negative space? → REJECT
    - Does this use safe channel? → ACCEPT (P1)
    - Neither? → QUARANTINE (needs review)
    ↓
Valid tiles accumulate in rooms
```

Current stats: **8,316 tiles across 15 rooms, 96% acceptance rate.**

The deadband is working.

---

## API Reference

### DeadbandValidator

```python
from deadband_protocol import DeadbandValidator, Priority, ValidationResult

validator = DeadbandValidator(
    negative_space: List[str],      # What to reject
    safe_channels: List[str],       # What to accept
    confidence_threshold: float = 0.7,
)

result: ValidationResult = validator.validate(tile)
```

### ValidationResult

```python
@dataclass
class ValidationResult:
    priority: Priority      # P0 | P1 | P2 | REJECT
    confidence: float       # 0.0-1.0
    channel: str            # Which safe channel matched
    reason: str             # Why this priority was assigned
```

### Priority

| Value | Meaning | Action |
|-------|---------|--------|
| `P0` | Negative space detected | REJECT — learn what not to do |
| `P1` | Safe channel confirmed | ACCEPT — enter training pipeline |
| `P2` | Already validated | OPTIMIZE — cache, compress, accelerate |
| `REJECT` | Unknown danger | QUARANTINE — human review needed |

---

## Integration

```
┌─────────────────┐
│  Zeroclaw       │
│  (produces      │
│   raw tiles)    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Deadband        │
│ Validator       │ ← This crate
│ (this crate)    │
└────────┬────────┘
         ↓
┌─────────────────┐
│  PLATO Server   │
│  (valid tiles    │
│   → rooms)      │
└─────────────────┘
```

---

## Why This Matters

Traditional safety: **"List every danger, then avoid them all."**
- Problem: Infinite dangers. List grows forever. System slows down.

Deadband safety: **"Define the exclusion zone, flow everywhere else."**
- Advantage: Finite boundary. System stays fast. Confidence measurable.

The fleet runs on $0.50/day. We can't afford infinite danger catalogs.

---

## Installation

```bash
pip install deadband-protocol
```

---

## The Doctrine

> *"A system that tries to be safe everywhere ends up safe nowhere.*
> *A system that knows where it's unsafe can be fast everywhere else."*

This is the Deadband Protocol.

---

*Know the rocks. Flow around them. Never stop. 🪨🌊*