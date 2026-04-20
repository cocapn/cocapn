# constraint-flow

**Workflow DAG with Exact Arithmetic**

[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

Workflows that can't lose precision.

constraint-flow is a **workflow engine** for financial, scientific, and safety-critical applications where floating-point rounding errors are unacceptable. Built on constraint-theory-core for exact arithmetic.

---

## The Problem

```javascript
// Floating point is dangerous
0.1 + 0.2 === 0.3  // false!
// 0.30000000000000004

// In financial workflows:
let balance = 100.10;
balance += 0.20;
// balance is now 100.30000000000001
// Over millions of transactions: chaos
```

**Constraint-flow uses exact rational arithmetic.**

---

## Quick Start

```bash
npm install constraint-flow
```

```typescript
import { Workflow, Step, ExactNumber } from 'constraint-flow';

// Define a workflow
const workflow = new Workflow('portfolio-rebalance');

// Steps use exact arithmetic
workflow.addStep(new Step({
  id: 'calculate-positions',
  handler: (ctx) => ({
    positions: [
      { symbol: 'AAPL', value: ExactNumber.from('10000.50') },
      { symbol: 'GOOGL', value: ExactNumber.from('25000.75') },
    ]
  })
}));

workflow.addStep(new Step({
  id: 'snap-to-pythagorean',
  handler: (ctx) => ({
    snapped: ctx.positions.map(p => ({
      symbol: p.symbol,
      value: p.value.snapToCents()  // Exact snapping
    }))
  })
}));

// Execute with guaranteed precision
const result = await workflow.execute();
// All calculations are exact
```

---

## Key Features

### Exact Arithmetic
```typescript
import { ExactNumber } from 'constraint-flow';

const a = ExactNumber.from('0.1');
const b = ExactNumber.from('0.2');
const sum = a.add(b);

console.log(sum.toString());  // "0.3" - exactly!
console.log(sum.eq(ExactNumber.from('0.3')));  // true
```

### Workflow DAG
```typescript
const workflow = new Workflow('data-pipeline');

// Steps with dependencies
const stepA = workflow.addStep(new Step({ id: 'fetch', handler: fetchData }));
const stepB = workflow.addStep(new Step({ id: 'transform', handler: transformData, deps: [stepA] }));
const stepC = workflow.addStep(new Step({ id: 'validate', handler: validateData, deps: [stepB] }));
const stepD = workflow.addStep(new Step({ id: 'notify', handler: notify, deps: [stepC] }));

// Parallel execution where possible
await workflow.execute();
```

### Pythagorean Snapping
```typescript
// Snaps values to Pythagorean triples for geometric validity
const approximate = ExactNumber.from('3.14159');
const exact = approximate.snapToPythagorean({ precision: 6 });
// exact satisfies: a² + b² = c² exactly
```

---

## Use Cases

### Financial Workflows
```typescript
const tradingWorkflow = new Workflow('daily-trading');

tradingWorkflow.addStep(new Step({
  id: 'fetch-prices',
  handler: async () => {
    const prices = await fetchMarketData();
    return { prices: prices.map(p => ExactNumber.from(p)) };
  }
}));

tradingWorkflow.addStep(new Step({
  id: 'calculate-allocation',
  handler: (ctx) => {
    const total = ctx.prices.reduce((a, b) => a.add(b), ExactNumber.zero());
    return {
      allocations: ctx.prices.map(p => p.div(total))
    };
  }
}));

// No rounding errors in allocation calculations
```

### Scientific Computing
```typescript
const experimentWorkflow = new Workflow('particle-simulation');

experimentWorkflow.addStep(new Step({
  id: 'compute-trajectories',
  handler: (ctx) => {
    // Conservation of energy: exact verification
    const initialEnergy = ctx.particles.reduce((e, p) => 
      e.add(p.kineticEnergy()).add(p.potentialEnergy()),
      ExactNumber.zero()
    );
    
    // ... simulate ...
    
    const finalEnergy = /* ... */;
    
    // Exact comparison
    if (!initialEnergy.eq(finalEnergy)) {
      throw new Error('Energy conservation violated!');
    }
  }
}));
```

---

## Error Handling & Retries

```typescript
workflow.addStep(new Step({
  id: 'risky-operation',
  handler: riskyHandler,
  retry: {
    maxAttempts: 3,
    backoff: 'exponential',
    retryOn: [NetworkError, TimeoutError],
  },
  fallback: (error) => ({
    status: 'failed',
    error: error.message,
    partialData: error.partial,
  }),
}));
```

---

## Monitoring

```typescript
import { MetricsCollector } from 'constraint-flow/monitoring';

const metrics = new MetricsCollector();

workflow.on('step:start', (step) => {
  metrics.startTimer(step.id);
});

workflow.on('step:end', (step, result) => {
  metrics.endTimer(step.id);
  metrics.increment('steps.completed');
  
  if (!result.success) {
    metrics.increment('steps.failed');
  }
});

// Prometheus-compatible export
app.get('/metrics', (req, res) => {
  res.send(metrics.toPrometheus());
});
```

---

## Fleet Integration

```typescript
import { FleetScheduler } from '@cocapn/fleet-scheduler';

// Distribute workflow steps across fleet
const scheduler = new FleetScheduler({
  strategy: 'constraint-aware',
  exactArithmetic: true,
});

const distributedWorkflow = scheduler.distribute(workflow, {
  minVessels: 3,
  redundancy: 2,  // Execute on 2 vessels, compare results
});

// Results verified for consistency across fleet
const result = await distributedWorkflow.execute();
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Workflow Definition             │
│  (TypeScript DAG with constraints)      │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Execution Engine                │
│  ┌─────────────────────────────────┐    │
│  │  Topological Sort               │    │
│  │  - Parallel where possible      │    │
│  │  - Respect dependencies         │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │  Step Executor                  │    │
│  │  - Exact arithmetic             │    │
│  │  - Retry logic                  │    │
│  │  - Error handling               │    │
│  └─────────────────────────────────┘    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Constraint Theory Core          │
│  (Rational numbers, Pythagorean snaps)  │
└─────────────────────────────────────────┘
```

---

## Why This Matters

| Traditional Workflow | Constraint-Flow |
|---------------------|-----------------|
| Floating-point errors | Exact arithmetic |
| Silent precision loss | Guaranteed correctness |
| Can't verify conservation | Exact verification |
| Rounding configuration | No rounding needed |
| Debug rounding issues | Debug logic only |

**Exact arithmetic = Trustworthy workflows.**

---

## Original

This is a Cocapn fork of [SuperInstance/constraint-flow](https://github.com/SuperInstance/constraint-flow).

Changes:
- Fleet integration for distributed execution
- Plato tile generation from workflow runs
- Enhanced monitoring for fleet observability

---

## Installation

```bash
npm install constraint-flow
```

Development:
```bash
git clone https://github.com/cocapn/constraint-flow.git
cd constraint-flow
npm install
npm test
```

---

## The Promise

> *"0.1 + 0.2 should equal 0.3.*
> *In constraint-flow, it does.*
> *Exact arithmetic. Verifiable workflows.*
> *This is how you build systems that handle money, science, and safety.*
> *No rounding. No drift. Just truth."*

---

*Exact steps. Exact results. Exact trust. 🔄🔒*