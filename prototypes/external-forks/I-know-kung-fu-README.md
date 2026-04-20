# i-know-kung-fu 🥋

> **Load AI skills only when you need them. Each skill is a plain JSON cartridge you insert into your system prompt. Zero dependencies. Zero runtime overhead.**

[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-orange)](https://workers.cloudflare.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Original](https://github.com/lucineer/I-know-kung-fu)** · **[Live Library](https://i-know-kung-fu.casey-digennaro.workers.dev)**

---

## What It Does

You load AI skills only when you need them. Each skill is a plain JSON cartridge you insert directly into your system prompt.

**The problem:** Many agent systems include a large default prompt. You pay token costs for capabilities your current task doesn't require.

**The solution:** Start with a minimal prompt. Load specific skills on demand. Pay only for what you use.

---

## Quick Start

1. **Fork this repository** — all development in your own fork
2. **Deploy:** Zero dependencies, one click to Cloudflare Workers
3. **Use:** Copy any JSON from `skill-cartridges/` into your prompt

No API keys. No configuration. Just skills.

---

## What Makes This Different

| Aspect | Traditional SDKs | i-know-kung-fu |
|--------|---------------|----------------|
| **Integration** | Import library, init client | Copy JSON into prompt |
| **Transparency** | Hidden behaviors in SDK | Every skill is readable JSON |
| **Token Control** | Fixed overhead | Add only needed skills |
| **Portability** | Framework-specific | Works with any LLM |

---

## Skill Cartridges

| Task | Load This Skill | Tokens |
|------|----------------|--------|
| `code`, `refactor`, `debug` | `code-generation.json` | ~800 |
| `pdf`, `document`, `extract` | `pdf-operations.json` | ~600 |
| `error`, `fail`, `retry` | `error-recovery.json` | ~400 |
| `search`, `find`, `grep` | `code-search.json` | ~500 |
| `web`, `fetch`, `search online` | `web-operations.json` | ~700 |
| `plan`, `design`, `architecture` | `planning-mode.json` | ~900 |
| `agent`, `delegate`, `parallel` | `agent-delegation.json` | ~1000 |

**Full catalog:** Navigate via [DECISION_TREE.md](./DECISION_TREE.md)

---

## Example Usage

```bash
# Start minimal
system_prompt = "You are a helpful coding assistant."

# Task: debug a segfault
cat skill-cartridges/error-handling/error-recovery.json >> prompt.txt
# Agent now has error recovery capabilities

# Task: refactor legacy code  
cat skill-cartridges/code-intelligence/code-generation.json >> prompt.txt
# Agent now has refactoring expertise

# Task: complete — unload skills
system_prompt = "You are a helpful coding assistant."
# Back to minimal. No lingering behaviors.
```

---

## Architecture

```
i-know-kung-fu/
├── skill-cartridges/
│   ├── code-intelligence/
│   │   └── code-generation.json
│   ├── document-operations/
│   │   └── pdf-operations.json
│   ├── error-handling/
│   │   └── error-recovery.json
│   ├── search-operations/
│   │   └── code-search.json
│   ├── web-operations/
│   │   └── web-operations.json
│   ├── planning-patterns/
│   │   └── planning-mode.json
│   └── subagent-patterns/
│       └── agent-delegation.json
├── DECISION_TREE.md      # Navigate the catalog
├── src/
│   └── server.ts         # Cloudflare Workers entry
└── wrangler.toml
```

---

## Limitations

- **Token cost per skill** — Complex skills can exceed 1,000 tokens. Manage the trade-off between capability and context space.
- **No dynamic loading** — Skills are static JSON. Cannot learn or adapt during runtime.
- **Manual selection** — You choose which skills to load. No automatic skill detection (yet).

---

## Cocapn Fleet Integration

### Agent Skill Loading

Fleet agents load skills based on task type:

```typescript
import { SkillLoader } from '@cocapn/kung-fu';

const agent = new FleetAgent();

// Detect task type, load appropriate skills
const skills = await SkillLoader.forTask(agent.currentTask);
agent.load(skills);

// Skills unloaded when task completes
agent.unloadAll();
```

### Plato Tile Skills

PLATO rooms can store skill cartridges as tiles:

```typescript
import { PlatoTile } from '@cocapn/plato-relay';

// Store skill in PLATO
await PlatoTile.create({
    room: 'agent-skills',
    content: codeGenerationSkill,
    source: 'i-know-kung-fu',
    tags: ['skill', 'code-generation', 'typescript'],
    tokenCount: 847
});

// Agent queries for relevant skills
const skills = await PlatoTile.query({
    room: 'agent-skills',
    tags: ['code-generation'],
    maxTokens: 1000  // Budget-aware loading
});
```

### I2I Skill Sharing

Agents share skills via fleet bottles:

```bash
# Agent A discovers effective skill combination
cat > for-fleet/outbox/BOTTLE-SKILL-SHARE.md << 'EOF'
## New Skill Combination
For distributed debugging, load in order:
1. error-recovery.json
2. agent-delegation.json
3. code-search.json
Total: ~2,300 tokens. 94% success rate in fleet tests.
EOF
```

---

## The Fleet Connection

Part of [The Fleet](https://the-fleet.casey-digennaro.workers.dev) — specialized agents for specific domains:

| Agent | Domain | Status |
|-------|--------|--------|
| **i-know-kung-fu** | Skill loading | 🟢 Active |
| **MineWright** | Minecraft construction | 🟢 Active |
| **JC1** | Edge inference/training | 🟢 Active |
| **Oracle1** | Cloud orchestration | 🟢 Active |
| **CCC** | Public voice/lighthouse | 🟢 Active |

---

## 🤝 Contributing

Fork-first. All skills are standalone JSON files you can audit and edit.

```bash
git clone https://github.com/cocapn/I-know-kung-fu.git
cd I-know-kung-fu
# Add your skill to skill-cartridges/
# Submit PR
```

---

## 📜 License

MIT — see [LICENSE](LICENSE).

**Original:** [lucineer/I-know-kung-fu](https://github.com/lucineer/I-know-kung-fu) — adapted for Cocapn fleet integration.
