# constraint-theory-agent

**AI Agent Framework with Constraint-Based Safety**

[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

AI agents that can't hallucinate.

constraint-theory-agent is a framework for building agents with **mathematical safety guarantees** — powered by constraint-theory-core for grounded reasoning.

---

## Quick Start

```bash
npm install @cocapn/constraint-theory-agent
```

```typescript
import { Agent, ManifoldConstraint } from '@cocapn/constraint-theory-agent';

// Create a safety-first agent
const agent = new Agent({
  name: 'portfolio-advisor',
  constraints: [
    // All outputs must satisfy these constraints
    ManifoldConstraint.bounds('allocation', 0, 1),
    ManifoldConstraint.sumEquals('allocation', 1),
    ManifoldConstraint.positive('returns'),
  ],
});

// Agent plans within constraints
const plan = await agent.plan({
  goal: 'Create balanced portfolio',
  context: { riskTolerance: 0.15 },
});

// Plan is guaranteed to satisfy all constraints
console.log(plan.satisfiesConstraints); // true
```

---

## Key Components

### 1. Constraint-Grounded LLM
```typescript
import { ConstrainedLLM } from '@cocapn/constraint-theory-agent';

const llm = new ConstrainedLLM({
  baseModel: 'gpt-4',
  manifold: portfolioManifold,
});

// All outputs are quantized to valid states
const response = await llm.generate(prompt);
// response is guaranteed valid
```

### 2. Safe Action Space
```typescript
const agent = new Agent({
  actions: [
    {
      name: 'rebalance',
      handler: rebalancePortfolio,
      constraints: [
        ManifoldConstraint.bounded('deviation', 0, 0.1),
      ],
    },
  ],
});

// Actions that would violate constraints are rejected
await agent.act('rebalance', { deviation: 0.5 }); // Throws ConstraintViolation
```

### 3. Provable Planning
```typescript
const planner = new ConstraintPlanner({
  horizon: 10,
  manifold: stateManifold,
});

// Plans are sequences of valid states
const plan = await planner.plan({
  start: currentState,
  goal: targetState,
});

// Every step in plan satisfies constraints
for (const step of plan.steps) {
  console.log(step.isValid); // true
}
```

---

## Use Cases

### Financial Advisor Agent
```typescript
const advisor = new Agent({
  name: 'robo-advisor',
  constraints: [
    ManifoldConstraint.budgetLimit(100000),
    ManifoldConstraint.riskTolerance(0.15),
    ManifoldConstraint.diversify(5), // Min 5 assets
  ],
});

const recommendation = await advisor.advise({
  goal: 'Retirement in 20 years',
  income: 75000,
});

// Recommendation is provably safe
```

### Medical Diagnostic Agent
```typescript
const diagnostic = new Agent({
  name: 'symptom-checker',
  constraints: [
    ManifoldConstraint.confidenceThreshold(0.95),
    ManifoldConstraint.requireReferral('critical'),
  ],
});

const diagnosis = await diagnostic.evaluate(symptoms);
// Won't suggest critical diagnosis without high confidence
```

### Code Generation Agent
```typescript
const coder = new Agent({
  name: 'safe-coder',
  constraints: [
    ManifoldConstraint.noUnsafeBlocks(),
    ManifoldConstraint.boundLoopIterations(),
    ManifoldConstraint.validateMemoryAccess(),
  ],
});

const code = await coder.generate('Sort an array');
// Generated code satisfies safety constraints
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Agent Interface                 │
│  (TypeScript/JavaScript)                │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Constraint Engine               │
│  ┌─────────────────────────────────┐    │
│  │  Manifold Definition            │    │
│  │  - Valid states                 │    │
│  │  - Constraint rules             │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │  Φ-Folding Operator             │    │
│  │  - Snap LLM outputs to valid    │    │
│  │  - Reject invalid actions       │    │
│  └─────────────────────────────────┘    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         LLM Integration                 │
│  (GPT-4, Claude, or local models)       │
└─────────────────────────────────────────┘
```

---

## Safety Guarantees

| Guarantee | Description |
|-----------|-------------|
| **Zero Hallucination** | P(invalid output) = 0 |
| **Bounded Error** | ‖actual - intended‖ ≤ ε |
| **Deterministic** | Same input → same output |
| **Verifiable** | Every decision has proof |

---

## Fleet Integration

Agents join the Cocapn fleet:

```typescript
import { FleetSync } from '@cocapn/fleet-sync';

// Register agent
await FleetSync.register(agent, {
  capabilities: ['financial-advice', 'portfolio-optimization'],
  safetyLevel: 'provable', // Uses constraint theory
});

// Other agents can query this agent's safety properties
const safety = await FleetSync.getSafetyProperties(agent.id);
console.log(safety.zeroHallucination); // true
```

---

## Why This Matters

| Traditional Agent | Constraint-Theory-Agent |
|-------------------|-------------------------|
| "Probably safe" | "Provably safe" |
| Can hallucinate | P(hallucination) = 0 |
| Hard to verify | Every decision proven |
| Behavior drifts | Deterministic |
| Safety prompts | Mathematical guarantees |

---

## Original

This is a Cocapn fork of [SuperInstance/constraint-theory-agent](https://github.com/SuperInstance/constraint-theory-agent).

Changes:
- Fleet integration for agent registration
- Plato tile generation from agent decisions
- Enhanced safety monitoring

---

## Installation

```bash
npm install @cocapn/constraint-theory-agent
```

Development:
```bash
git clone https://github.com/cocapn/constraint-theory-agent.git
cd constraint-theory-agent
npm install
npm test
```

---

## The Promise

> *"Most AI agents hope they're safe.*
> *Constraint-theory agents know they are.*
> *Mathematical guarantees. Provable correctness.*
> *This is how you build agents that handle critical decisions.*
> *No hope required. Just proof."*

---

*Safe agents. Provable actions. No hallucinations. 🤖🔒*