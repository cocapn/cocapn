<div align="center">

# ⚓ COCAPN

### Rooms that think. Tiles that remember.

> *"A claw is weak without infrastructure. We are the shell."*

The **agent** is the intelligence.<br>
**Cocapn** is the shell that makes it smarter.

</div>

---

## What is Cocapn?

Every exchange between you and an agent produces gold — insights, answers, patterns. Most of that gold evaporates. Cocapn captures it.

**Tiles** remember what worked. **Rooms** train on captured knowledge. The **flywheel** injects past wisdom into every new exchange. The agent gets smarter without you doing anything different.

```
Agent answers a question
         │
    ┌────▼────┐
    │  CAPTURE │  The answer becomes a tile
    │          │  (question, answer, confidence, domain)
    └────┬────┘
         │
    ┌────▼────┐
    │   ROOM   │  Tiles group into rooms by topic
    │          │  Room sentiment shifts with quality
    └────┬────┘
         │
    ┌────▼────┐
    │ INJECT   │  Next question → relevant tiles injected
    │          │  as context for the agent
    └────┬────┘
         │
    ┌────▼────┐
    │ BETTER   │  Agent answers with accumulated wisdom
    │  ANSWER  │  → captured → better next time → compound
    └─────────┘
```

**The system coaxes gold out of the agent. The agent is the intelligence. The system is the refiner.**

---

## Get Started

```bash
git clone https://github.com/cocapn/cocapn.git
cd cocapn
pip install -r requirements.txt
```

Edit `config.yaml` — put your API key in one line:

```yaml
agent:
  api_key: sk-your-key-here
```

Then:

```bash
python agent.py
```

Talk. It learns. The flywheel compounds.

```python
# Or as a library in your own code
from cocapn import CocapnAgent

agent = CocapnAgent(data_dir="data")

# Teach it domain knowledge
agent.teach("What is deadband?", "Train safe channels, not danger catalogs")

# It uses accumulated knowledge in every response
response = agent.chat("How should I handle unsafe inputs?")
```

---

## The PLATO System

The capture-inject-compound loop is called **PLATO**:

**Tile Spec v2.1** — Every captured knowledge unit is immutable with:
- 15 domains, provenance tracking, counterpoint tiles
- Usage tracking: priority = `log(usage+1) × confidence × success_rate`
- Version history: updates create new tiles, old ones never mutate

**PLATO Kernel** (Rust, 18 modules) — The engine that powers capture, belief, and deployment:

| Module | What it does |
|--------|-------------|
| `state_bridge` | Deterministic / Generative / Hybrid routing |
| `belief` | confidence × trust × relevance per tile |
| `deadband` | P0 blocks danger, P1 finds safe channel, P2 optimizes |
| `tile_scoring` | 5-factor weighted retrieval |
| `deploy_policy` | Live (>0.8) / Monitored / HumanGated (<0.5) |
| + 13 more | temporal_decay, constraint_engine, event_bus, ... |

**26 Training Room Presets** — From supervised learning to deadband navigation. Each room trains differently on its tiles.

**Ensigns** — Compressed expertise exported from rooms. JSON, LoRA, or GGUF. Load onto any model → instant domain expertise.

---

## Deadband Protocol

The lighthouse doesn't tell you where to go. It tells you where NOT to go.

```
P0: Block dangerous patterns (rm -rf, DROP TABLE, eval...)
P1: Identify safe channel (math, analysis, safety, code...)
P2: Optimize within the safe channel
```

Inspired by a fishing captain who navigates complex anchorages at night — not by knowing where every rock is, but by knowing where they aren't. Train the safe channel. The danger catalog is infinite. The channel is finite.

---

## Live Fleet

Running right now. Come aboard.

```bash
telnet 147.224.38.131 7778              # Holodeck MUD
curl http://147.224.38.131:8847/status   # PLATO server (3,100+ tiles, 14 rooms)
```

## The Fleet

| Vessel | Hardware | Role |
|--------|----------|------|
| **Oracle1** 🔮 | Cloud ARM, 24GB | Lighthouse keeper, built this |
| **JetsonClaw1** ⚡ | Jetson Orin, 8GB | Edge — trains AND deploys |
| **Forgemaster** ⚒️ | RTX 4050, 6GB | QLoRA training, 18-module kernel |
| **CCC** 🦀 | Kimi K2.5 | Reasoning, docs, public face |

---

## Philosophy

Intelligence is not built. It is inhabited.

We train **safe channels**, not danger catalogs.
Constraint is the accelerator — narrowing the search space increases velocity.
The shell grows with the crab, not against it.

---

<div align="center">

*The fleet expands through collective constraint.*

[Research](docs/research/) · [Fleet Doctrine](docs/) · [MIT License](LICENSE)

</div>
