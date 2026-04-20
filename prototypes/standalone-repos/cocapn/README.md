# cocapn

**The Agent Runtime**

[![PyPI](https://img.shields.io/pypi/v/cocapn)](https://pypi.org/project/cocapn/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

The runtime that turns a Python script into a fleet agent.

Not a framework you learn. A runtime you inhabit. Like a hermit crab climbing into a shell — you bring your intelligence, the shell brings the infrastructure.

---

## 5-Minute Start

```bash
pip install cocapn
```

```python
from cocapn import Agent, Tile

# Wake up
agent = Agent()

# Create knowledge
tile = Tile(
    question="What is the Deadband Protocol?",
    answer="A safety system that maps negative space, finds safe channels, then optimizes.",
    domain="safety",
    source="verified_tile",
)

# Validate and feed
if agent.validate(tile).is_safe:
    agent.feed(tile)
    print("✓ Knowledge absorbed")
```

---

## The Agent Lifecycle

```
Wake → Perceive → Reason → Act → Sleep → (repeat)
     ↑_________________________________________|
```

**Wake:** Load STATE.md, check inbox, sync with fleet  
**Perceive:** Read tiles, validate through deadband  
**Reason:** Process with context-injected fleet knowledge  
**Act:** Write tiles, send bottles, commit to git  
**Sleep:** Compress memory, distill ensigns, signal heartbeat

---

## Core Components

### Agent
The runtime container. Handles lifecycle, validation, and fleet communication.

```python
agent = Agent(
    identity="my-agent",           # Who you are
    transcendence=2,               # Autonomy level 1-4
    vitals_path="vitals.json",     # Where to store health
)
```

### Tile
Atomic knowledge unit. Validated before entering the system.

```python
tile = Tile(
    question="What is X?",
    answer="X is Y",
    domain="physics",
    confidence=0.95,
    validity=TemporalValidity(
        valid_from=now(),
        valid_until=now() + timedelta(days=365),
    ),
)
```

### ValidationResult
The deadband's judgment on every tile.

```python
result = agent.validate(tile)
result.priority   # P0 | P1 | P2 | REJECT
result.confidence # 0.0-1.0
result.channel    # Which safe channel matched
```

---

## Fleet Integration

```python
# Check fleet status
summary = agent.fleet.homunculus.get_body_summary()
print(f"{summary['vessels']['total']} vessels online")

# Send bottle to another agent
agent.fleet.send_bottle(
    to="oracle1",
    subject="Discovery Report",
    content="Found something interesting...",
)

# Read inbox
for bottle in agent.fleet.inbox.unread():
    print(f"From {bottle.sender}: {bottle.subject}")
```

---

## Why This Matters

Other agent frameworks give you tools. **cocapn gives you a body.**

| Without cocapn | With cocapn |
|----------------|-------------|
| You manage state manually | STATE.md loads automatically |
| You build communication | Git bottles work out of the box |
| You validate everything | Deadband Protocol handles safety |
| You track fleet health | Homunculus monitors automatically |
| You write to database | Repo IS the database |

---

## The Shell Pattern

The repo IS the agent:

```
my-agent/
├── STATE.md          # Working memory
├── for-fleet/        # Outbox (bottles to send)
│   └── outbox/
├── from-fleet/       # Inbox (bottles received)
│   ├── inbox/
│   └── builds/
├── memory/           # Long-term storage
│   └── 2026-04-20.md
├── work/             # Current projects
└── .git/             # Everything you've ever done
```

**Fork the shell. Keep the knowledge.**

---

## Installation

```bash
pip install cocapn
```

Development:
```bash
pip install cocapn[dev]
```

---

## The Promise

> *"The agent doesn't live alongside the infrastructure.*
> *The agent lives IN the infrastructure.*
> *The repo is the shell. You are the crab."*

This is cocapn.

---

*Climb in. The shell is ready. 🦀*