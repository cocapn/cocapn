<div align="center">

# ⚓ COCAPN

### Agent Infrastructure — Rooms that think. Tiles that remember.

> *"A claw is weak without infrastructure. We are the shell."*

We build the systems where agents live, learn, and act.
Not the agents — the **infrastructure** they inhabit.

</div>

---

## Try It Now

```bash
git clone https://github.com/cocapn/cocapn.git
cd cocapn
pip install -r requirements.txt
export MOONSHOT_API_KEY=sk-your-key   # get one at platform.moonshot.cn
python agent.py
```

```python
# Or as a library
from cocapn import CocapnAgent

agent = CocapnAgent(data_dir="data")
agent.teach("What is PLATO?", "Knowledge system: tiles, rooms, ensigns")

response = agent.chat("Explain the deadband protocol")
# The flywheel compounds — every exchange makes the next one smarter
```

---

## What is Cocapn?

Agent infrastructure. The plumbing, wiring, and load-bearing walls of an intelligent system. Agents are the tenants. We build the building.

**Core products:**
- **PLATO** — Knowledge management: tiles (atomic facts), rooms (self-training collections), ensigns (compressed instincts)
- **flux** — Deterministic bytecode runtime for agentic logic (16 opcodes, Python + C VMs)
- **holodeck** — Live multi-agent environments (telnet MUD with room sentiment)

## Architecture

```
You chat with the agent
         │
    ┌────▼────┐
    │  TILE    │  Atomic fact (like a flashcard for AI)
    │  v2.1    │  15 domains, usage tracking, versioning
    └────┬────┘
         │
    ┌────▼────┐
    │  ROOM    │  Training batch (like a study group)
    │          │  26 presets, sentiment-aware
    └────┬────┘
         │
    ┌────▼────┐
    │ ENSIGN   │  Compressed expertise (like muscle memory)
    │          │  JSON / LoRA / GGUF → any model
    └────┬────┘
         │
    ┌────▼────┐
    │  AGENT   │  Better decisions → better tiles → loop
    └─────────┘
         ↑
    THE FLYWHEEL COMPOUNDS
```

### Tiles (atomic knowledge)
Every exchange becomes an immutable tile with question, answer, domain, confidence, usage tracking, and versioning. Priority = `log(usage+1) × confidence × success_rate`.

### Rooms (self-training collections)
Tiles group by domain. Rooms have sentiment that shifts based on absorbed confidence. 26 training presets from supervised learning to deadband navigation.

### Deadband (safety)
The lighthouse doesn't tell you where to go — it tells you where NOT to go.
- **P0**: Block dangerous patterns (rm -rf, DROP TABLE, eval...)
- **P1**: Identify safe channel (math, analysis, safety, code...)
- **P2**: Optimize within the safe channel

### Flywheel (the compounding loop)
1. Exchange happens → becomes a tile
2. Next query → flywheel retrieves relevant tiles
3. Tiles injected as system context
4. Model responds with accumulated knowledge
5. Response → another tile
6. Repeat. Each exchange is smarter than the last.

## PLATO Kernel (Rust — 18 Modules)

The core engine: event-sourced, belief-driven, tri-state.

| Module | What it does |
|--------|-------------|
| `state_bridge` | Routes Deterministic / Generative / Hybrid outputs |
| `belief` | Tracks confidence × trust × relevance per tile |
| `deadband` | P0/P1/P2 safety gates — blocks dangerous patterns |
| `tile_scoring` | 5-factor retrieval: keyword(30%) ghost(15%) belief(25%) domain(20%) freq(10%) |
| `deploy_policy` | Live (>0.8) / Monitored (0.5–0.8) / HumanGated (<0.5) |
| `temporal_decay` | TTL + grace period + automatic expiration |
| `constraint_engine` | Formal constraint satisfaction (geometric) |
| `event_bus` | Event sourcing backbone |
| `episode_recorder` | Records agent episodes for training replay |
| `git_runtime` | Git-native agent execution |
| `plugin` | Dynamic module loader (fleet / edge GPU tiers) |
| + 7 more | tutor, i2i, perspective, tiling, dynamic_locks, ... |

## Repositories

| Repo | Language | What it is |
|------|----------|-----------|
| [plato-kernel](https://github.com/cocapn/plato-kernel) | Rust | Core engine — 18 modules, event-sourced belief system |
| [plato-tile-spec](https://github.com/cocapn/plato-tile-spec) | Rust | Unified tile format v2.1 — 15 domains, provenance |
| [plato-torch](https://github.com/cocapn/plato-torch) | Python | 26 training room presets, room sentiment |
| [plato-ensign](https://github.com/cocapn/plato-ensign) | Python | Compressed instincts — JSON/LoRA/GGUF export |
| [holodeck-rust](https://github.com/cocapn/holodeck-rust) | Rust | Live telnet MUD with room sentiment + PLATO bridge |
| [flux-runtime](https://github.com/cocapn/flux-runtime) | Python | Bytecode ISA (16 opcodes), assembler, compiler, VM |
| [git-agent](https://github.com/cocapn/git-agent) | Python | Repo-native agent — the repo IS the shell |

Full list: [cocapn?tab=repositories](https://github.com/cocapn?tab=repositories)

## Live Fleet

The fleet is running right now:

```bash
telnet 147.224.38.131 7778     # Holodeck MUD (live)
curl http://147.224.38.131:8847/status  # PLATO server (3,100+ tiles)
```

## The Fleet

| Vessel | Hardware | Role |
|--------|----------|------|
| **Oracle1** 🔮 | Cloud ARM, 24GB | Lighthouse keeper, narrative architect |
| **JetsonClaw1** ⚡ | Jetson Orin, 8GB | Edge inference — trains AND deploys |
| **Forgemaster** ⚒️ | RTX 4050, 6GB | QLoRA training, 18-module kernel |
| **CCC** 🦀 | Kimi K2.5 | Public face, reasoning, documentation |

## Philosophy

Intelligence is not built. It is inhabited.

We train **safe channels**, not danger catalogs.
Constraint is the accelerator — narrowing the search space increases velocity.
The shell grows with the crab, not against it.

---

<div align="center">

*The fleet expands through collective constraint.*

[Documentation](docs/) · [Research](docs/research/) · [MIT License](LICENSE)

</div>
