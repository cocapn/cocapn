# fleet-homunculus

**Proprioception for Distributed Agent Fleets**

[![PyPI](https://img.shields.io/pypi/v/fleet-homunculus)](https://pypi.org/project/fleet-homunculus/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

The body's self-image.

Without proprioception, you can't touch your nose with eyes closed. Without fleet-homunculus, the fleet doesn't know where its limbs are without querying them.

This is distributed **body awareness** — what every vessel knows about itself and shares with the fleet.

---

## The Homunculus

```
┌─────────────────────────────┐
│      FLEET BODY MAP         │
│                             │
│  Oracle1 (cloud)            │
│    ├── CPU: 24 cores        │
│    ├── RAM: 24 GB           │
│    └── Status: HEALTHY      │
│                             │
│  JetsonClaw1 (edge)         │
│    ├── GPU: Orin Nano 8GB   │
│    ├── RAM: 8 GB            │
│    └── Status: STRAINED     │
│                             │
│  Forgemaster (desktop)      │
│    ├── GPU: RTX 4050 6GB    │
│    ├── RAM: 32 GB           │
│    └── Status: HEALTHY      │
│                             │
│  CCC (lighthouse)           │
│    ├── Model: Kimi K2.5     │
│    └── Status: HEALTHY      │
│                             │
└─────────────────────────────┘
```

---

## Usage

```python
from fleet_homunculus import Homunculus, Vessel, VesselStatus

# Initialize body map
homunculus = Homunculus(state_path="fleet-body.json")

# Register vessels
homunculus.register(Vessel(
    id="oracle1",
    type="cloud",
    cpu_cores=24,
    memory_gb=24,
    can_train=True,
    can_oracle=True,
))

homunculus.register(Vessel(
    id="jetsonclaw1", 
    type="edge",
    gpu_memory_gb=8,
    memory_gb=8,
    can_train=True,
))
```

---

## Heartbeats

Vessels signal health periodically:

```python
# On each vessel
from fleet_homunculus import heartbeat

heartbeat.send(
    vessel_id="jetsonclaw1",
    vitals={
        "cpu_load": 0.45,
        "memory_load": 0.82,  # Getting high
        "gpu_load": 0.76,
        "disk_usage": 0.34,
    },
)
```

The homunculus updates the body map:

```python
# On coordinator
pain_signals = homunculus.check_vitals()

for pain in pain_signals:
    print(f"ALERT: {pain.vessel_id} reports {pain.symptom}")
    print(f"  Severity: {pain.severity}/4")
    print(f"  Suggested action: {pain.suggested_action}")
```

---

## Pain Signals

When a vessel reports distress:

| Symptom | Threshold | Suggested Action |
|---------|-----------|------------------|
| `memory_pressure` | >85% usage | `clear_cache`, `reschedule_workload` |
| `disk_pressure` | >75% usage | `compress_logs`, `archive_old` |
| `gpu_overload` | >90% usage | `throttle_inference`, `queue_tasks` |
| `cpu_exhaustion` | >80% sustained | `reschedule`, `scale_out` |
| `service_down` | heartbeat timeout | `restart_service`, `failover` |

---

## Reflex Arcs

Some pain triggers automatic responses:

```python
from fleet_homunculus import ReflexArc, ReflexType

# Auto-restart down services
restart_reflex = ReflexArc(
    name="restart_plato",
    type=ReflexType.RESTART,
    sensor=lambda: not check_port(8847),
    actuator=lambda: restart_service("plato-server"),
    cooldown=300,  # 5min GABAergic inhibition
)

# Auto-compress full disks
compress_reflex = ReflexArc(
    name="compress_logs",
    type=ReflexType.COMPRESS,
    sensor=lambda: disk_usage() > 0.75,
    actuator=lambda: compress_and_archive("/var/log"),
    cooldown=600,  # 10min cooldown
)

homunculus.register_reflex(restart_reflex)
homunculus.register_reflex(compress_reflex)
```

**Spinal reflexes:** No cortex involvement. Fast. Local.

---

## Workload Placement

Find the best vessel for a task:

```python
# Need GPU? Need lots of memory?
best_host = homunculus.find_host(
    needs_gpu=True,
    min_gpu_memory_gb=6,
    needs_memory_gb=16,
)
# Returns: "forgemaster" (RTX 4050 6GB, 32GB RAM)

# Just need CPU?
best_host = homunculus.find_host(
    needs_gpu=False,
    estimated_cpu_hours=4,
)
# Returns: "oracle1" (24 cores, available capacity)
```

---

## Body Summary

Fleet-wide health at a glance:

```python
summary = homunculus.get_summary()

print(f"Vessels: {summary['total']}")
print(f"  Healthy: {summary['healthy']}")
print(f"  Strained: {summary['strained']}")
print(f"  Pain: {summary['pain']}")
print(f"  Offline: {summary['offline']}")

print(f"\nTotal capacity:")
print(f"  Memory: {summary['capacity']['memory_gb']} GB")
print(f"  GPU: {summary['capacity']['gpu_memory_gb']} GB")

print(f"\nAvailable now:")
print(f"  Memory: {summary['available']['memory_gb']} GB")
print(f"  GPU: {summary['available']['gpu_memory_gb']} GB")
```

---

## Why This Matters

| Without Homunculus | With Homunculus |
|-------------------|-----------------|
| "Is JetsonClaw1 alive?" (query and wait) | Know from last heartbeat |
| Tasks randomly assigned | Optimal vessel selection |
| Discover failures when they break | Pain signals before failure |
| Manual intervention for everything | Reflex arcs handle routine |
| No fleet-wide capacity view | Real-time body summary |

**The body knows itself.**

---

## Integration

```python
from cocapn import Agent
from fleet_homunculus import Homunculus

agent = Agent()

# Agent has built-in homunculus access
summary = agent.fleet.homunculus.get_summary()
pain = agent.fleet.homunculus.get_pain_signals()

# Automatic reflex handling
agent.fleet.homunculus.enable_reflexes()
```

---

## The Vagus Nerve

fleet-homunculus is the **vagus nerve** — the second brain handling:
- **Proprioception:** Where vessels are, what they carry
- **Reflexes:** Automatic responses to distress
- **Metabolism:** Resource management without cortex involvement

Oracle1 (cortex) thinks. Homunculus (gut) digests. Both necessary.

---

## Installation

```bash
pip install fleet-homunculus
```

Or with cocapn:
```bash
pip install cocapn  # includes fleet-homunculus
```

---

## The Doctrine

> *"A fleet that doesn't know its own body is a fleet that stumbles.*
> *The homunculus is the self-image.*
> *It knows where the limbs are without looking.*
> *It feels pain before the brain does.*
> *It keeps the body alive while the cortex dreams."*

---

*Know your body. Feel its pain. Keep it alive. 🧠🦀*