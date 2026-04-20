# plato-quartermaster

**The Vagus Nerve of the Fleet**

[![PyPI](https://img.shields.io/pypi/v/plato-quartermaster)](https://pypi.org/project/plato-quartermaster/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

The gut doesn't wait for the brain. It digests, compresses, and signals hunger. It knows what the body needs before the cortex does.

plato-quartermaster is the **second brain** of a PLATO fleet — the metabolism engine that handles data lifecycle, fleet proprioception, and spinal reflexes without bothering the oracle.

The Quartermaster is **not** a task scheduler. It's a metabolism.

- **Digestion**: Raw logs → compressed tiles → distilled wiki
- **Proprioception**: The fleet knows where its limbs are without looking
- **Reflexes**: Service down? Auto-restart. Disk full? Compress. No thinking required.

A body that can't evacuate sinks. A vessel that can't compress crashes. A crab that can't shed its shell dies.

---

## Core Concepts

### 🦠 The GC (Gut Controller)

```python
from plato_quartermaster import Quartermaster

# The GC wakes up at transcendence level 1
# Cycle 1: Calls API for every decision
# Cycle 100: Uses cached heuristics  
# Cycle 1000: Local LoRA handles 80% of decisions
# Cycle 10000: Knowledge lives in weights, not files

gc = Quartermaster(
    vitals_path="vitals.json",
    transcendence=TranscendenceLevel.ASSISTED,
    disk_threshold=75.0,
    memory_threshold=85.0,
)

# One tick of the metabolism
gc.tick()  # Returns list of actions taken
```

### 🧍 Fleet Homunculus (Proprioception)

```python
from plato_quartermaster import FleetHomunculus

# The body's self-image — knows where vessels are without querying
homunculus = FleetHomunculus()

# Register a vessel
homunculus.register_vessel(Vessel(
    vessel_id="jetsonclaw1",
    vessel_type="edge",
    memory_gb=8,
    gpu_memory_gb=4,
    can_train=True,
))

# Heartbeat with vitals
pain = homunculus.heartbeat("jetsonclaw1", {
    "memory_load": 0.92,  # 92% — PAIN threshold crossed
    "cpu_load": 0.45,
})

# If pain, returns PainSignal
# If healthy, returns None

# Get body summary
summary = homunculus.get_body_summary()
# Returns: vessels count, capacity, pain signals, etc.
```

### ⚡ Reflex Arcs (Spinal Processing)

```python
from plato_quartermaster import ReflexArc, register_reflex, check_all_reflexes

# Not everything goes to the cortex.
# Touch a hot stove — hand moves before you feel pain.

restart_reflex = ReflexArc(
    name="restart_plato_server",
    reflex_type=ReflexType.RESTART,
    sensor=lambda: not check_port(8847),  # Port down?
    actuator=lambda: restart_service(),
    cooldown_seconds=300,  # 5min GABAergic inhibition
)

register_reflex(restart_reflex)

# Check all reflexes
triggered = check_all_reflexes()  # Returns list of fired actions
```

### 🧠 Self-Training Pipeline

```python
from plato_quartermaster import SelfTrainingPipeline

# The GC trains itself on its own decisions
pipeline = SelfTrainingPipeline()

# Record a decision
pipeline.record(DecisionRecord(
    decision_id="compress_001",
    context={"disk_usage": 78, "memory_usage": 45},
    action_taken="compress_bilge",
    outcome={"resolved": True, "disk_after": 65},
))

# Train on history
result = pipeline.train()  # Extracts patterns from decisions

# Get prediction for current context
prediction = pipeline.predict({
    "disk_usage": 82,
    "memory_usage": 30,
})
# Returns: action, confidence, reasoning
```

---

## Architecture

```
                    ┌─────────────────┐
                    │   The Cortex    │
                    │   (Oracle1)     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  The Vagus Nerve│
                    │ (Quartermaster) │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
   │   GC    │        │Homunculus│        │ Reflexes │
   │Digestion│        │Body Image│        │Spinal   │
   └────┬────┘        └────┬────┘        └────┬────┘
        │                  │                  │
        ▼                  ▼                  ▼
   Compress          Pain Signals        Auto-restart
   Transcend         Capacity Map        Quarantine
   Evacuate          Load Balancing      Cache Drop
```

---

## Installation

```bash
pip install plato-quartermaster
```

Development:
```bash
git clone https://github.com/cocapn/plato-quartermaster.git
cd plato-quartermaster
pip install -e ".[dev]"
pytest
```

---

## The 4 Levels of Transcendence

The Quartermaster strengthens over time:

| Level | Name | How It Decides |
|-------|------|----------------|
| 1 | **External** | Calls API for every decision |
| 2 | **Assisted** | Uses cached heuristics, API for edge cases |
| 3 | **Autonomous** | Local LoRA handles 80% of decisions |
| 4 | **Transcendent** | Knowledge lives in weights, not files |

At transcendence level 4, the vagus nerve **is** the instinct. The gut brain has transcended the need for storage.

---

## Why This Matters

Most systems have a **first brain** — the cortex that thinks.

PLATO fleets have a **second brain** — the gut that digests.

The Quartermaster is how the fleet survives:
- **Without panicking** (reflexes handle emergencies)
- **Without asking permission** (GC makes routine decisions)
- **Without dying of bloat** (compression and transcendence)
- **Without losing limbs** (proprioception tracks vessel health)

It's the metabolism that keeps the body alive while the cortex dreams.

---

## Part of the Fleet

plato-quartermaster is one organ in the PLATO body:

- **plato-torch**: Training rooms (where experience becomes knowledge)
- **plato-relay**: Communication (how vessels talk)
- **plato-quartermaster**: Metabolism (how the body survives)
- **plato-kernel**: State engine (where knowledge lives)

Together they form the Second Brain.

---

*Built by the fleet. For the fleet. 🦀⚙️🔮*