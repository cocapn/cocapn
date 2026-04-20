# MineWright 🛠️

> **AI foreman for Minecraft. Coordinates builds, remembers progress across sessions, respects game rules. Runs on Cloudflare Workers with zero dependencies.**

[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-orange)](https://workers.cloudflare.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Original](https://github.com/lucineer/MineWright)** · **[Live Demo](https://the-fleet.casey-digennaro.workers.dev/minewright)**

---

## What It Does

MineWright is an AI foreman for Minecraft. It coordinates build projects, remembers progress across your game sessions, and respects the game's rules.

**Key capabilities:**
- **Persistent Memory** — Job state stored in Cloudflare Durable Objects. Doesn't reset on timeout or session end.
- **Minecraft-Aware** — Plans based on Java Edition 1.20 logic: stack sizes, block physics, material availability.
- **You Own It** — Runs solely on your Cloudflare account. No central service, telemetry, or data collection.

---

## Quick Start

1. **Fork this repository** — designed to be modified and owned by you
2. **Deploy:** `wrangler deploy`
3. **Add secret:** `wrangler secret put LLM_API_KEY`
4. **Configure:** Edit agent behavior in `src/agent.ts`

---

## Features

| Feature | What It Means |
|---------|--------------|
| **Build Tracking** | Remains aware of active jobs, completed sections, outstanding materials |
| **Actionable Plans** | Breaks builds into gather-and-place steps respecting game mechanics |
| **Worker Coordination** | Generates plans split among multiple players or automation tools |
| **Full Modifiability** | Control personality, expertise, and rules by editing source |

---

## Architecture

```
MineWright/
├── src/
│   ├── agent.ts        # Agent behavior and knowledge base
│   ├── planner.ts      # Build plan generation
│   └── memory.ts       # Durable Object state management
├── wrangler.toml       # Cloudflare Workers config
└── README.md           # This file
```

**Runtime:** Cloudflare Workers + Durable Objects  
**State:** Persistent across sessions (survives timeouts, restarts)  
**Protocol:** Open Fleet agent protocol for interoperability

---

## Example Session

```
You: "Build a medieval castle with moat and drawbridge"

MineWright: "Project: Medieval Castle
             Phase 1: Foundation (64×64 cobblestone)
             Materials: 4,096 cobblestone, 256 oak planks
             Phase 2: Walls (12 blocks high)
             Materials: 3,072 stone bricks, 128 ladders
             Phase 3: Moat (water channel, 2 blocks deep)
             Phase 4: Drawbridge (redstone mechanism)
             
             Total estimate: 8 hours solo, 2 hours with 4 workers
             
             Shall I generate detailed step-by-step plans?"

You: "Yes, and assign gather tasks to Worker-2"

MineWright: [Splits plan, assigns cobblestone gathering to Worker-2,
             oak farming to Worker-3, redstone circuit to Worker-4]
```

---

## Limitations

- **Java Edition 1.20 only** — Bedrock or modded environments need rule set updates
- **No vision** — Cannot see the world; relies on player descriptions
- **No direct control** — Generates plans; does not place blocks directly

---

## Cocapn Fleet Integration

### As a Subagent

MineWright can be invoked as a fleet subagent for construction planning:

```typescript
import { MineWrightAgent } from '@cocapn/minewright';

const foreman = new MineWrightAgent({
    project: 'medieval-castle',
    workers: 4,
    sessionStorage: 'durable-object'
});

const plan = await foreman.plan('castle with moat');
await foreman.assign(plan.phases[0], 'worker-2');
```

### Plato Tile Generation

Build plans become persistent fleet knowledge:

```typescript
import { PlatoTile } from '@cocapn/plato-relay';

const plan = await foreman.plan('redstone-computer');

// Store plan as PLATO tile for other agents
await PlatoTile.create({
    room: 'minecraft-builds',
    content: plan.toMarkdown(),
    source: 'minewright',
    tags: ['minecraft', 'redstone', 'architecture'],
    project: 'redstone-computer'
});

// Later: another agent queries for similar builds
const related = await PlatoTile.query({
    room: 'minecraft-builds',
    tags: ['redstone'],
    similarity: plan.embedding
});
```

### I2I Communication

MineWright reports progress via fleet bottles:

```bash
# After completing a phase
mwright report --project medieval-castle --phase foundation

# Generates bottle in for-fleet/outbox/
cat for-fleet/outbox/BOTTLE-MWRIGHT-PROGRESS.md
```

---

## The Fleet Connection

MineWright is part of [The Fleet](https://the-fleet.casey-digennaro.workers.dev) — a collection of specialized agents, each with a specific domain:

| Agent | Domain | Status |
|-------|--------|--------|
| **MineWright** | Minecraft construction | 🟢 Active |
| **Capitaine** | Maritime/naval operations | 🟡 In development |
| **JC1** | Edge inference/training | 🟢 Active |
| **Oracle1** | Cloud orchestration | 🟢 Active |
| **CCC** | Public voice/lighthouse | 🟢 Active |

---

## 🤝 Contributing

Fork-first project. All development happens in your own fork.

```bash
git clone https://github.com/cocapn/MineWright.git
cd MineWright
npm install
wrangler dev
```

---

## 📜 License

MIT — see [LICENSE](LICENSE).

**Original:** [lucineer/MineWright](https://github.com/lucineer/MineWright) — adapted for Cocapn fleet integration.
