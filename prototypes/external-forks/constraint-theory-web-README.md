# constraint-theory-web

**Interactive Visualizations for Constraint Manifolds**

[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue)](https://typescriptlang.org)
[![WASM](https://img.shields.io/badge/WASM-ready-orange)](https://webassembly.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

See the constraints. Touch the manifold. Understand the math.

constraint-theory-web provides interactive visualizations and educational tools for geometric constraint computing. 52 demos, WASM modules, and tutorials that make constraint theory tangible.

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/cocapn/constraint-theory-web.git
cd constraint-theory-web

# Install dependencies
npm install

# Start development server
npm run dev

# Deploy to Cloudflare Pages
npm run deploy
```

---

## 52 Interactive Demos

| Category | Demos | Description |
|----------|-------|-------------|
| **Manifold Basics** | 8 | KD-tree visualization, quantization, holonomy |
| **Constraint Solving** | 12 | Bounds, inequalities, geometric constraints |
| **Φ-Folding** | 6 | Snap-to-grid, precision mapping |
| **Performance** | 10 | SIMD, batch processing, memory layout |
| **Applications** | 16 | Financial, ML, robotics use cases |

---

## WASM Integration

The Rust core compiles to WASM for browser execution:

```typescript
import init, { PythagoreanManifold } from './pkg/constraint_theory_core.js';

async function run() {
  await init();
  
  const manifold = new PythagoreanManifold(3, 0.001);
  const point = [3.14159, 2.71828, 1.41421];
  const exact = manifold.quantize(point);
  
  console.log(`Quantized: ${exact}`);
  // Runs at native speed in the browser
}
```

---

## Educational Tutorials

### Tutorial 1: What is a Constraint Manifold?
```
Interactive: Drag points in 3D space
Watch: Invalid states turn red
Learn: The manifold is the set of all valid states
```

### Tutorial 2: Zero Hallucination Guaranteed
```
Interactive: Query random points
Observe: All returned states satisfy constraints
Proof: Visual verification of correctness
```

### Tutorial 3: Hidden Dimensions
```
Interactive: Adjust precision slider
See: How k = ⌈log₂(1/ε)⌉ hidden dimensions work
Understand: Exact arithmetic in discrete spaces
```

---

## Live Demos

**Online:** [cocapn.github.io/constraint-theory-web](https://cocapn.github.io/constraint-theory-web)

**Local:**
```bash
npm run dev
# Open http://localhost:3000
```

---

## Fleet Integration

Agents visualize their constraint spaces:

```typescript
import { ManifoldVisualizer } from 'constraint-theory-web';

// Visualize agent's planning manifold
const viz = new ManifoldVisualizer('#canvas');
viz.load(manifold);
viz.highlight(agent.current_state);
viz.showValidTransitions();
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Browser (Chrome/Firefox)      │
│  ┌─────────────────────────────────┐    │
│  │  TypeScript/React UI            │    │
│  │  - 52 demos                     │    │
│  │  - Interactive tutorials        │    │
│  └─────────────────────────────────┘    │
│              │                          │
│  ┌───────────┴─────────────────────┐    │
│  ▼                                 ▼    │
│  WASM Module                    WebGL   │
│  (Rust core)                   Viz      │
│  - Quantize                    - 3D     │
│  - Verify                      - KD-tree│
└─────────────────────────────────────────┘
```

---

## Deployment

**Cloudflare Pages** (recommended):
```bash
# wrangler.toml already configured
npm run deploy
```

**Static hosting**:
```bash
npm run build
cp -r dist/* /var/www/html/
```

---

## Requirements

- Node.js 18+
- Cloudflare account (for deployment)

---

## Original

This is a Cocapn fork of [SuperInstance/constraint-theory-web](https://github.com/SuperInstance/constraint-theory-web).

Changes:
- Fleet-themed visual styling
- Integration with cocapn agent visualization

---

## Installation

```bash
npm install constraint-theory-web
```

Development:
```bash
git clone https://github.com/cocapn/constraint-theory-web.git
cd constraint-theory-web
npm install
npm run dev
```

---

## The Promise

> *"Constraint theory is abstract. This makes it visible.*
> *Drag, touch, explore — the manifold becomes real.*
> *52 demos. Zero to understanding.*
> *The math is beautiful when you can see it."*

---

*See the constraints. Touch the proof. 🌐🔒*