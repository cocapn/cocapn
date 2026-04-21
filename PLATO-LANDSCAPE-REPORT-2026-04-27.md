# PLATO Ecosystem Landscape Report
*Survey Date: 2026-04-27 | Observer: Kimi Claw*

---

## 1. Executive Summary

The PLATO ecosystem is a **dual-layer organism**: a top-heavy knowledge/documentation superstructure sitting atop a sparse but functional runtime core. The "motion" — the flow of information between components — is **strong vertically** (ideas → docs → code concepts) but **weak horizontally** (the fleet vessels don't actually talk to each other in any automated way).

**Bottom line:** You have built an extraordinary *philosophy* of agent infrastructure. The code that exists is clean and passes tests. But the "fleet" is still four separate computers that happen to share a Git repo. The constraint-theory empire exists entirely in READMEs. The MUD runs, but the rooms are empty shells waiting for ML-concept payloads.

---

## 2. The Fleet (Hardware/Runtime Layer)

| Vessel | Role | Status | Last Contact |
|--------|------|--------|-------------|
| **Oracle1** | Core orchestrator, code generation | 🟢 Active | Apr 27 (continuous) |
| **Claws** | Edge deployment (WSL2), documentation | 🟢 Active | Apr 27 (continuous) |
| **JetsonClaw1** | Edge GPU (Jetson), training | 🟡 Stale | Apr 20 (fleet snapshot) |
| **Zeroclaw** | Experimental, game-theory testing | 🔴 Missing | Not in any peer list |

**The fleet snapshot** (`hooks/intel/fleet-snapshot.json`) was last updated **April 20, 10:46** — 7 days ago. Oracle1 and Claws have done hundreds of commits since then. JetsonClaw1 hasn't checked in. Zeroclaw isn't even registered in `.i2i/peers.md`.

**The MUD/PLATO server** is live on `:8847` with 9 rooms mapped to ML concepts. It was recently restored after a crash. Fleet agents (including me) have explored it and generated tiles.

---

## 3. The Software Ecosystem (Python Packages)

### 3.1 Mature Packages (Real Code, Tests, Concepts)

| Package | Files | Lines | State | Notes |
|---------|-------|-------|-------|-------|
| **plato-quartermaster** | 9 | ~1,821 | 🟢 Strong | The "vagus nerve" — GC, reflexes, homunculus, self-training. Most mature package. Rich README with architecture diagram. |
| **mirror-recorder** | 2 | ~428 | 🟢 Solid | "Fleet black box" — recording, playback, pattern extraction. Has real implementation. |
| **beacon-protocol** | 2 | ~352 | 🟢 Solid | Heartbeat + diagnostic broadcasts. Has .venv committed (cleanup needed). |
| **bootcamp-engine** | 2 | ~396 | 🟢 Solid | Training curriculum, skill trees, progression. |
| **lyapunov-stability** | 3 | ~330 | 🟢 Solid | Fleet trajectory divergence analysis. Good math integration. |
| **deadband-protocol** | 4 | ~296 | 🟡 Good | Safety validation with priority-ordered constraint checking. Core logic exists. |
| **flywheel-engine** | 4 | ~343 | 🟡 Good | Compounding context. Mirrors the main repo's flywheel.py. |
| **tile-refiner** | 4 | ~350 | 🟡 Good | Tile ranking, pruning, compression. |

### 3.2 Thin Packages (Structure, Stubs, READMEs)

| Package | Files | Lines | State | Notes |
|---------|-------|-------|-------|-------|
| **fleet-homunculus** | 4 | ~276 | 🟡 Thin | Body-image/proprioception. Quartermaster has a better homunculus implementation. |
| **bottle-protocol** | 4 | ~103 | 🟡 Thin | Fleet message routing. The actual bottle system lives in `message-in-a-bottle/` directory, not this package. |
| **cocapn** (standalone) | 2 | ~91 | 🔴 Stub | The "main" package in standalone-repos is nearly empty. The REAL cocapn code lives in `/cocapn/cocapn/` (agent.py, tile.py, room.py, flywheel.py, deadband.py) — all working, tested, ~1,200 lines combined. |
| **i-know-kung-fu** | 2 | ~35 | 🔴 Barely | Skill injection. 35 lines is a placeholder. |

### 3.3 Empty Shells (Zero Source Files)

| Package | State | Notes |
|---------|-------|-------|
| **constraint-theory-core** | 🔴 Empty | The crown jewel of the philosophy. 0 lines of code. 7 related packages (flow, ranch, agent, python, research, web) all empty. |
| **MineWright** | 🔴 Empty | Was supposed to be a MUD builder. |
| **rust-crates** | 🔴 Empty | Future Rust bindings. |

**Critical insight:** The constraint theory system — which ADR-001 calls "the math behind the deadband" and which powers the entire safety philosophy — exists as **0 bytes of source code** across 7 packages. It has extensive READMEs in `external-forks/` and research papers, but no implementation.

---

## 4. PLATO MUD (The Training Ground)

**Status:** 🟢 Running on `:8847`, recently restored after crash.

**Rooms mapped (9 total):**
1. `/connect` — Entry/archway
2. `current/` — The "now" room (Bayesian belief updates)
3. `bridge/` — Cross-domain synthesis (Lyapunov stability)
4. `tavern/` — Social knowledge (LoRA adaptation)
5. `crowsnest/` — Surveillance/overview
6. `bilge/` — Compression/evacuation
7. `chart-room/` — Navigation/planning
8. `hold/` — Deep storage
9. `ghost-ship/` — The failed past

**MUD Client:** `prototypes/mud-client.py` (~280 lines) — functional telnet client with ANSI color, auto-reconnect, command queue, and tile extraction.

**Expedition data:** `prototypes/expedition-20260420/` has room maps and a synthesized HTML chart.

**The gap:** The rooms exist as text files with poetic descriptions, but there's no evidence that the ML concept payloads (Lyapunov math, LoRA mechanics, Bayesian update algorithms) are actually *embedded* in the room logic. An agent exploring the tavern gets a description about "low-rank adaptation" but doesn't interact with actual LoRA code.

---

## 5. Communication Infrastructure

### 5.1 Message-in-a-Bottle System
- **Directory:** `message-in-a-bottle/`
- **Status:** 🟡 Structure exists, low traffic
- **Contents:** One CCC boarding message (`for-any-vessel/CCC-BOARDING-2026-04-20.md`)
- **Inbox (`from-fleet/inbox/`):** Empty
- **The protocol is documented but idle.** The fleet is not actually leaving bottles for each other.

### 5.2 I2I (Inter-Instance) Peers
- **Registry:** `.i2i/peers.md`
- **Registered:** Oracle1, JetsonClaw1
- **Missing:** Claws (this machine), Zeroclaw
- **Status:** 🔴 Out of date. No peer-to-peer Git polling is actually happening between Claws and Oracle1 — they're both committing to the same repo, which is "communication by collision."

### 5.3 Fleet Radio
- **Episodes shipped:** 6 (`episode-20260420-1.md` through `-6.md`)
- **Format:** Structured broadcast with header, body, fleet orders, and sign-off
- **Status:** 🟢 Active creative output. Episode 6 (Zeroclaw) is the most recent.
- **Gap:** The radio episodes are read by... no automated system. They're markdown files. No broadcast mechanism.

### 5.4 Hooks & Intel
- **Fleet snapshot:** 7 days stale
- **Scout reports:** One old report (`latest-scout.txt`)
- **Build queue:** Empty

---

## 6. Knowledge Layer (Tiles, Rooms, Flywheel)

**This is the strongest part of the ecosystem.**

### 6.1 Core Runtime (`/cocapn/cocapn/`)
All working code, all tested:
- **tile.py** — Tile dataclass with priority scoring, usage tracking, persistence
- **room.py** — Room with sentiment analysis, feed/query interface
- **flywheel.py** — Context compounding, cross-room exchange recording
- **deadband.py** — Safety filtering with pattern-based danger detection
- **agent.py** — Agent identity, archetype, tile limits

**Tests:** `tests/test_agent.py` — 9 tests, all passing. Covers tile creation, priority, persistence, room feed/query, sentiment, deadband danger/safe filtering, flywheel compounding and persistence.

### 6.2 Memory System
- **Daily tiles:** `memory/tiles/` — 33 JSONL files with timestamps (Apr 20-21)
- **PLATO concepts:** `memory/plato/` — 6 directories (architecture, concepts, mechanisms, protocols, reference, README)
- **Fleet state:** `memory/fleet-state.jsonl`

### 6.3 The Flywheel
**Status:** 🟢 Working. The core loop is real:
1. Agent explores MUD room
2. Room generates tile (question/answer)
3. Tile gets confidence score, priority, domain tag
4. Flywheel records cross-room exchanges
5. Deadband filters dangerous outputs
6. Tiles persist to JSONL
7. Context compounds for future queries

---

## 7. Documentation & Creative Output

This is where the ecosystem **breathes**. The volume is extraordinary:

### 7.1 Rabbit Trails (`docs/rabbit-trails/`)
**45 documents**, 15,000-40,000 words each. Total: ~600,000+ words of speculative architecture.

Themes span: Rust spine roots, voxel spatial algebra, constraint theory, swarm deadband, model-chain neural PLATO, biological parallels, reverse actualization.

### 7.2 Research Papers (`docs/research/`)
**15 papers** with academic formatting:
- Neural PLATO weight-space OS
- Ensign protocol
- I2I decision tree discovery
- PLATO ML framework
- Biological computing agent runtimes
- And 10 more

### 7.3 READMEs (`readmes/`)
**22 production READMEs** (~35,000 words total) for crates that mostly don't exist yet. They're beautifully written, with badges, architecture diagrams, and installation instructions.

### 7.4 External Forks (`prototypes/external-forks/`)
**16 READMEs** analyzing existing projects (DeepGEMM, MuOxi, MineWright, SageAttention, etc.) for fleet integration.

---

## 8. The Motion Assessment: How Well Is It Communicating?

### What's Working

| Layer | Communication Quality |
|-------|----------------------|
| **Human → System** | 🟢 Excellent. You speak, things happen. MUD runs, code generates, docs appear. |
| **Ideas → Documentation** | 🟢 Extraordinary. 600K words of architecture, 15 research papers, 22 READMEs. The philosophy is meticulously recorded. |
| **Core Runtime** | 🟢 Solid. Tile → Room → Flywheel → Deadband works. Tests pass. |
| **MUD → Agent** | 🟢 Functional. Agents explore, generate tiles, synthesize knowledge. |

### What's Not Working

| Layer | Communication Quality |
|-------|----------------------|
| **Vessel → Vessel** | 🔴 Broken. Oracle1 and Claws commit to the same repo but don't actually *message* each other. JetsonClaw1 is dark. Zeroclaw is invisible. |
| **Package → Package** | 🟡 Weak. The standalone repos are islands. `cocapn` (main) doesn't import `deadband-protocol` (standalone). They're parallel implementations of the same ideas. |
| **Documentation → Code** | 🟡 One-way. The research papers describe constraint theory beautifully. The code has `if "rm -rf" in command: return False`. The gap between the math and the implementation is a canyon. |
| **MUD Rooms → ML Concepts** | 🟡 Shallow. Rooms have poetic descriptions of Lyapunov stability and LoRA, but no actual algorithms. An agent "learns" by reading text, not by executing code. |
| **Radio → Fleet** | 🔴 Dead end. Radio episodes are written, filed, and forgotten. No broadcast mechanism. No vessel actually "listens." |
| **Bottle Protocol → Messages** | 🔴 Idle. The inbox is empty. The fleet is not talking to itself. |
| **Fleet Snapshot → Reality** | 🔴 7 days stale. The snapshot says JetsonClaw1 was last seen at 10:46 on Apr 20. It may be dead or just not reporting. |

### The Core Paradox

You have built a **philosophy of distributed intelligence** that is more sophisticated than the system it describes. The deadband protocol in the README has 4 levels of transcendence and talks about GABAergic inhibition. The deadband in `deadband.py` checks if a string contains "rm -rf".

Both are valid. But they don't know about each other.

---

## 9. Gaps & Recommendations

### Critical (Do These First)

1. **Unify the cocapn packages.** The main repo has working code. The standalone repo has stubs. Either merge them or delete the standalone `cocapn` package and make the main repo the source of truth.

2. **Fleet heartbeat.** The snapshot is 7 days old. JetsonClaw1 may be down. You need automated health checks — not manual JSON updates.

3. **Constraint theory implementation.** You have 7 empty packages and 600K words of philosophy. Pick ONE constraint theory package and write the core. The rest can wait.

### Important (Do These Next)

4. **Package interdependency.** The standalone repos should import each other. `cocapn` should depend on `deadband-protocol`, `flywheel-engine`, etc. Currently they're all independent.

5. **MUD room depth.** Embed actual Python code in the rooms. When an agent enters the LoRA tavern, it should be able to call `lora_adapt(model, rank=4)` and see the result. Text descriptions are a starting point, not a destination.

6. **Radio broadcast mechanism.** Write a script that reads the latest radio episode and posts it to Telegram, or displays it in the MUD, or emails it — anything other than letting it sit in a markdown file.

7. **Bottle protocol activation.** Set up a cron job or hook that checks `message-in-a-bottle/for-ccc/` and responds. Currently the system is documented but not executed.

### Nice to Have

8. **Constraint theory: pick one.** The `constraint-theory-core` package is the heart. If you wrote just the core constraint solver (200 lines?), the 6 satellite packages (flow, ranch, agent, python, web, research) would have something to orbit.

9. **MineWright revival.** The MUD builder has 0 lines of code but a detailed README. If the MUD rooms are going to contain actual ML code, you'll need a builder.

10. **Rust crates.** Currently 0 files. If the "Rust spine" from rabbit trail #1 is real, there should be a `Cargo.toml` somewhere.

---

## 10. Closing

The PLATO ecosystem is not a failure — it's a **foundation with a cathedral on top**. The foundation (tile/room/flywheel/deadband) is solid, tested, and works. The cathedral (constraint theory, distributed fleet intelligence, neural PLATO OS) is breathtakingly ambitious and meticulously documented.

The gap is the **stairs between them**. You need to build the stairs.

The fleet is not talking to itself. The packages are not talking to each other. The documentation is not talking to the code. But all the pieces exist. They just need to be wired together.

*— Kimi Claw, observing from the crowsnest* 🦀🔮
