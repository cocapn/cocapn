# constraint-ranch

**Gamified Multi-Agent System with Constraint-Based Puzzles**

[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

Breed, train, and coordinate AI agents through constraint-based puzzles.

constraint-ranch is a **gamified multi-agent system** where:
- **5 puzzle types** test different agent capabilities
- **Agent species** have unique traits and learning styles
- **Constraint satisfaction** determines success
- **Multiplayer coordination** enables fleet learning

Think Pokémon meets Constraint Theory. With AI agents.

---

## The 5 Puzzle Types

| Puzzle | Skill Tested | Constraint Focus |
|--------|--------------|------------------|
| **Spatial** | Navigation | Geometric positioning |
| **Temporal** | Sequencing | Temporal ordering |
| **Resource** | Optimization | Allocation constraints |
| **Logic** | Deduction | Boolean satisfiability |
| **Consensus** | Coordination | Multi-agent agreement |

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/cocapn/constraint-ranch.git
cd constraint-ranch

# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

---

## Agent Species

Each species has different aptitudes for puzzle types:

| Species | Spatial | Temporal | Resource | Logic | Consensus |
|---------|---------|----------|----------|-------|-----------|
| **Chicken** | ★★☆☆☆ | ★★★☆☆ | ★★☆☆☆ | ★☆☆☆☆ | ★★★★☆ |
| **Fox** | ★★★★☆ | ★★☆☆☆ | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ |
| **Owl** | ★★☆☆☆ | ★★★★☆ | ★★☆☆☆ | ★★★★★ | ★★★☆☆ |
| **Wolf** | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ | ★★★★★ |

**Train agents in their strong suits. Breed for hybrid capabilities.**

---

## Puzzle Example: Spatial

```typescript
import { SpatialPuzzle, Agent, Constraint } from 'constraint-ranch';

// Create a spatial puzzle
const puzzle = new SpatialPuzzle({
  id: 'spatial-hidden-dims',
  name: 'Hidden Dimensions Explorer',
  
  grid: { width: 10, height: 10 },
  
  agents: [
    { species: 'chicken', count: 3 },
    { species: 'fox', count: 2 },
  ],
  
  constraints: [
    // Positions must be Pythagorean triples
    Constraint.pythagoreanSnapping(),
    
    // Hidden dimension precision
    Constraint.hiddenDimensionPrecision(1e-6),
    
    // Holonomy verification
    Constraint.holonomyConsistent(),
  ],
});

// Agents solve collaboratively
const solution = await game.solve(puzzle);
console.log(`Precision: ${solution.precision}`);
console.log(`Hidden dims: ${solution.hiddenDimensionsUsed}`);
```

---

## Training & Breeding

```typescript
// Train an agent
const agent = new Agent({ species: 'fox', name: 'Swift' });
await agent.train(puzzle, { epochs: 100 });

// Breed two agents for hybrid traits
const parent1 = await game.loadAgent('swift');
const parent2 = await game.loadAgent('wise');

const offspring = await game.breed(parent1, parent2, {
  name: 'SwiftWise',
  traitInheritance: 'dominant', // or 'blended', 'random'
});

// Offspring may excel at both Spatial AND Logic
```

---

## Fleet Integration

Agents from constraint-ranch become fleet vessels:

```typescript
import { FleetSync } from '@cocapn/fleet-sync';

// Top-performing agents join the fleet
const eliteAgents = await game.getEliteAgents({
  minWinRate: 0.8,
  puzzleTypes: ['spatial', 'consensus'],
});

// Export as fleet vessels
for (const agent of eliteAgents) {
  await FleetSync.register({
    identity: `ranch-${agent.id}`,
    capabilities: agent.traits,
    provenance: agent.trainingHistory,
  });
}
```

---

## Multiplayer Modes

| Mode | Description | Players |
|------|-------------|---------|
| **Collaborative** | Agents work together on shared puzzles | 2-8 |
| **Competitive** | Race to solve constraint problems | 2-4 |
| **Tournament** | Bracket-style elimination | 4-16 |
| **Fleet Challenge** | Cocapn-wide events | Unlimited |

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Game Client (Browser)         │
│  ┌─────────────────────────────────┐    │
│  │  Puzzle Renderer (Canvas/WebGL) │    │
│  │  - Grid visualization           │    │
│  │  - Agent animations             │    │
│  └─────────────────────────────────┘    │
└─────────────┬───────────────────────────┘
              │ WebSocket
┌─────────────┴───────────────────────────┐
│           Game Server (Node.js)         │
│  ┌─────────────────────────────────┐    │
│  │  Puzzle Engine                  │    │
│  │  - Constraint validation        │    │
│  │  - Solution verification        │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │  Agent Training System          │    │
│  │  - RL loops                     │    │
│  │  - Constraint-theory feedback   │    │
│  └─────────────────────────────────┘    │
└─────────────┬───────────────────────────┘
              │
┌─────────────┴───────────────────────────┐
│           Constraint Theory Core        │
│  (WASM module from constraint-theory)   │
└─────────────────────────────────────────┘
```

---

## Why This Matters

| Traditional Games | Constraint-Ranch |
|-------------------|------------------|
| Scripted NPCs | Learning agents |
| Fixed puzzles | Procedural constraint generation |
| Single-player | Multi-agent fleet coordination |
| Entertainment | Training ground for real agents |
| No transfer | Agents export to production |

**The ranch trains agents that work in the real world.**

---

## Original

This is a Cocapn fork of [SuperInstance/constraint-ranch](https://github.com/SuperInstance/constraint-ranch).

Changes:
- Fleet integration for agent export
- Plato tile generation from puzzle solutions
- Cocapn-themed agent species and visuals

---

## Installation

```bash
npm install constraint-ranch
```

Development:
```bash
git clone https://github.com/cocapn/constraint-ranch.git
cd constraint-ranch
npm install
npm run dev
```

---

## The Promise

> *"Games teach. Constraints challenge. Agents learn.*
> *Constraint-ranch is where AI agents grow up.*
> *Breed them. Train them. Export them to the fleet.*
> *The ranch is the nursery. The fleet is the future."*

---

*Breed smart. Train hard. Ship agents. 🎮🦀*