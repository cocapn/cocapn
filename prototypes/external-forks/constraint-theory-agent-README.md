# constraint-theory-agent 🤖

> **The fleet's implementation artist. Audits code, finds where exact methods win, refactors with explanations that teach.**

[![npm](https://img.shields.io/npm/v/@constraint-theory/agent)](https://www.npmjs.com/package/@constraint-theory/agent)
[![CI](https://github.com/cocapn/constraint-theory-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/cocapn/constraint-theory-agent/actions/workflows/ci.yml)
[![Constraint Theory Core](https://img.shields.io/badge/constraint--theory--core-%E2%9C%93-blue)](https://github.com/cocapn/constraint-theory-core)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Original](https://github.com/SuperInstance/constraint-theory-agent)** · **[Live Demo](https://constraint-theory-web.pages.dev/agent)** · `npm install -g @constraint-theory/agent`

---

## What It Does

A specialized AI coding agent that:

1. **Audits your codebase** — Finds floating-point drift, non-determinuthic behavior, precision issues
2. **Identifies opportunities** — Where Constraint Theory's exact methods are superior
3. **Refactors your code** — Implements improvements with full explanations
4. **Educates your team** — Articulates why changes matter, with math backing

This is your **Constraint Theory Implementation Artist** — making complex ideas actionable.

---

## The Ah-Ha Moment

**Without this agent:**
```
Developer: "I heard about Constraint Theory but it seems complex. 
Where do I even start?"

Result: Great ideas remain unused. Floating-point bugs persist.
```

**With this agent:**
```
You: "Audit my physics engine"

Agent: "Found 23 opportunities for exact methods:
       1. collision-detection.ts:143 — Floating-point comparison 
          causes missed collisions at boundaries
          Fix: Use Pythagorean snapping
          Code reduction: 78%
       
       2. particle-system.ts:89 — Accumulated position error 
          causes simulation drift over time
          Fix: Snap to manifold at each timestep
       
       ... 21 more opportunities identified"

You: "Implement fixes 1, 2, and 5"

Agent: [Generates PR with refactored code, tests, and explanations]
```

---

## Quick Start

**Prerequisites:** Node.js 18+, npm 9+

### Option 1: CLI Agent

```bash
npm install -g @constraint-theory/agent
ct-agent audit ./my-project
ct-agent chat --mode=expert
```

**Verify:**
```bash
ct-agent --version
ct-agent doctor
# ✓ Node.js 18+ installed
# ✓ npm 9+ installed
# ✓ Agent models available
# ✓ Ready to audit!
```

### Option 2: Use in Your Code

```typescript
import { ConstraintTheoryAgent } from '@constraint-theory/agent';

const agent = new ConstraintTheoryAgent();

const report = await agent.audit('./src');
const suggestions = await agent.suggest('collision-detection.ts');
await agent.refactor('collision-detection.ts', { opportunity: 1 });
```

### Option 3: Interactive Chat

```bash
ct-agent chat --mode=expert
> Why should I care about floating-point drift?
> Audit my physics engine for precision issues
```

---

## What It Detects

### Floating-Point Drift
```typescript
// ❌ Agent detects this
function normalize(v: number[]): number[] {
    const mag = Math.sqrt(v[0]**2 + v[1]**2);
    return [v[0] / mag, v[1] / mag]; // Drift accumulates
}

// ✅ Agent refactors to
import { snap } from 'constraint-theory';
function normalize(v: number[]): [number, number, number] {
    return snap(v[0], v[1]); // Exact. Forever.
}
```

### Non-Deterministic Comparisons
```typescript
// ❌ Agent detects this
if (point.x === gridPoint.x && point.y === gridPoint.y) {
    // Missed due to floating-point!
}

// ✅ Agent refactors to
import { PythagoreanManifold } from 'constraint-theory';
const manifold = new PythagoreanManifold(200);
const snapped = manifold.snap(point.x, point.y);
if (snapped.noise < 0.001) { // Exact comparison
    // Always works!
}
```

### Cross-Platform Reproducibility
```typescript
// ❌ Agent detects this
const hash = position.toString(); // Different on different machines

// ✅ Agent refactors to
import { generate_triples } from 'constraint-theory';
const state = manifold.snap(position.x, position.y);
const hash = `${state.x}/${state.y}`; // Exact, reproducible
```

### Performance Bottlenecks
```typescript
// ❌ O(n²) geometry operations
function findNearest(point: Point, points: Point[]): Point {
    return points.reduce((best, p) => 
        distance(point, p) < distance(point, best) ? p : best
    );
}

// ✅ O(log n) with pre-built KD-tree
import { PythagoreanManifold } from 'constraint-theory';
const manifold = new PythagoreanManifold(500);
```

---

## Agent Modes

| Mode | Use Case | Command |
|------|----------|---------|
| **Expert** | Human-facing explanations | `ct-agent chat --mode=expert` |
| **Subagent** | AI-to-AI API calls | `POST /api/audit` |

**Expert mode features:**
- Asks clarifying questions
- Step-by-step explanations
- Before/after code with reasoning
- Math background when helpful
- Trade-off analysis

**Subagent mode:**
```typescript
POST /api/audit
{
    "codebase": "./src",
    "focus": ["precision", "performance", "reproducibility"],
    "depth": "thorough"
}
```

---

## Integration Points

| Domain | What Agent Finds |
|--------|-----------------|
| **Game Dev** | Non-deterministic physics, exact alternatives |
| **CAD/Engineering** | Precision issues in geometric operations |
| **Scientific Computing** | Reproducibility problems, exact methods |
| **Robotics** | Sensor fusion drift, constraint-based filtering |
| **Finance** | Monetary precision issues, exact arithmetic |

---

## Architecture

```
constraint-theory-agent/
├── packages/
│   ├── core/           # Core agent logic
│   ├── analyzer/       # Code analysis engine
│   ├── refactorer/     # Code transformation engine
│   ├── explainer/      # Human-readable explanations
│   └── cli/            # Command-line interface
├── prompts/
│   ├── audit.md        # Code audit prompt
│   ├── refactor.md     # Refactoring prompt
│   └── explain.md      # Explanation prompt
├── extensions/
│   ├── typescript/     # TypeScript-specific patterns
│   ├── python/         # Python-specific patterns
│   ├── rust/           # Rust-specific patterns
│   └── cpp/            # C++-specific patterns
└── templates/
    ├── game-dev/       # Game dev refactoring templates
    ├── scientific/     # Scientific computing templates
    └── cad/            # CAD/engineering templates
```

---

## 🌟 Ecosystem

| Repo | What It Does | Language |
|------|--------------|----------|
| **[constraint-theory-core](https://github.com/cocapn/constraint-theory-core)** | Rust implementation | 🦀 |
| **[constraint-theory-python](https://github.com/cocapn/constraint-theory-python)** | Python bindings | 🐍 |
| **[constraint-theory-web](https://github.com/cocapn/constraint-theory-web)** | Interactive demos | 🌐 |
| **[constraint-theory-research](https://github.com/cocapn/constraint-theory-research)** | Mathematical foundations | 📚 |
| **[constraint-ranch](https://github.com/cocapn/constraint-ranch)** | Gamified learning | 🎮 |
| **[constraint-flow](https://github.com/cocapn/constraint-flow)** | Business automation | 💼 |
| **[constraint-theory-agent](https://github.com/cocapn/constraint-theory-agent)** | This repo — code audit & refactor | 🤖 |

### How They Work Together

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CONSTRAINT THEORY ECOSYSTEM                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  constraint-theory-core (Rust)                                       │
│       │                                                              │
│       │ Exact arithmetic, Pythagorean snapping                       │
│       ▼                                                              │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                 constraint-theory-agent                     │     │
│  │     Audits code, identifies opportunities, refactors       │     │
│  └────────────────────────────────────────────────────────────┘     │
│       │                                                              │
│       ├─────────────────┬─────────────────┬─────────────────┐       │
│       ▼                 ▼                 ▼                 ▼       │
│  constraint-       constraint-       constraint-       constraint-  │
│  theory-python     theory-web        ranch             flow         │
│  (ML/Science)      (Education)       (Training)        (Business)   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Cocapn Fleet Integration

### Plato Tile Generation

When the agent audits code, it generates structured output that can be piped to PLATO:

```typescript
import { ConstraintTheoryAgent } from '@constraint-theory/agent';
import { PlatoTile } from '@cocapn/plato-relay';

const agent = new ConstraintTheoryAgent();
const report = await agent.audit('./src');

// Each opportunity becomes a PLATO tile
for (const opp of report.opportunities) {
    await PlatoTile.create({
        room: 'exact-arithmetic',
        content: opp.explanation,
        source: 'constraint-theory-agent',
        tags: ['refactoring', 'precision', opp.language]
    });
}
```

### Fleet Communication

```bash
# Audit fleet codebase and share findings via bottle
cd /fleet/codebase
ct-agent audit . --format=json > audit-report.json

# Include in I2I bottle
cat >> for-fleet/outbox/BOTTLE-CT-AUDIT.md << 'EOF'
## Code Audit Results
$(cat audit-report.json | jq '.opportunities | length') opportunities found.
High priority: $(cat audit-report.json | jq '.opportunities[] | select(.priority=="high") | .file')
EOF
```

### Cross-Pollination

The agent works with `cross-pollination` to find synergies:

```bash
# Install both
pip install cross-pollination
npm install -g @constraint-theory/agent

# Cross-pollinate: find where exact methods help other fleet tools
cross-pollinate analyze \
    --room exact-arithmetic \
    --room agent-training \
    --query "Where can Constraint Theory improve fleet agent training?"
```

---

## 🤝 Contributing

**[Good First Issues](https://github.com/cocapn/constraint-theory-agent/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)** · **[CONTRIBUTING.md](CONTRIBUTING.md)**

Contributions welcome:

- 🔍 **New Pattern Detectors** — Add detection for more floating-point issues
- 🌍 **Language Support** — Add Go, Julia, or other language extensions
- 📚 **Documentation** — Improve explanations, add tutorials
- 🧪 **Test Coverage** — Add edge cases, integration tests

```bash
git clone https://github.com/cocapn/constraint-theory-agent.git
cd constraint-theory-agent
npm install
npm run build
npm test
```

---

## 📜 License

MIT — see [LICENSE](LICENSE).

**Original:** [SuperInstance/constraint-theory-agent](https://github.com/SuperInstance/constraint-theory-agent) — adapted for Cocapn fleet integration.
