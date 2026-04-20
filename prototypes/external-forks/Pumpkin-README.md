# Pumpkin

**Constraint Programming Solver with Proof Logging**

[![Rust](https://img.shields.io/badge/rust-1.70+-orange)](https://rust-lang.org)
[![MiniZinc](https://img.shields.io/badge/minizinc-solver-blue)](https://minizinc.dev)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

A solver that finds solutions AND proves they're correct.

Pumpkin is a **constraint programming solver** written in Rust. It doesn't just give you answers — it gives you **certificates** that the answers are correct. In a world of probabilistic AI, this is certainty.

---

## Constraint Programming

You describe the problem. The solver finds the solution.

```rust
// "I need to schedule 5 tasks across 3 workers"
// "Each task takes different time"
// "No worker can exceed 8 hours"
// "Minimize total completion time"

// Describe constraints
let mut model = Model::new();
model.add_constraint(start_time[i] + duration[i] <= end_time[i]);
model.add_constraint(no_overlap(worker_tasks[j]));
model.set_objective(minimize(max(end_time)));

// Solve
let solution = solver.solve(&model);
// Returns optimal schedule + proof of optimality
```

---

## Proof Logging

Most solvers say: "Here's an answer, trust me."

Pumpkin says: "Here's an answer AND a proof you can verify."

```rust
let result = solver.solve_with_proof(&model, "schedule.proof");

// Later, verify independently
let verified = ProofChecker::verify("schedule.proof");
assert!(verified.valid);  // Mathematical certainty
```

**Why proofs matter:** When agents make decisions, we need to trust those decisions.

---

## Quick Start

```bash
# Clone the fork
git clone https://github.com/cocapn/Pumpkin.git
cd Pumpkin

# Build
cargo build --release

# Solve a problem
cargo run --bin pumpkin -- input.mzn
```

---

## Supported Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `cumulative` | Resource scheduling | "Use 3 workers max" |
| `disjunctive` | No-overlap | "Tasks can't overlap" |
| `element` | Array indexing | "Get i-th element" |
| `linear` | Linear equations | "2x + 3y ≤ 10" |
| `all_different` | Distinct values | "Each color used once" |
| `clausal` | Boolean logic | "A or B, not both" |

---

## Agent Integration

Agents use Pumpkin for **guaranteed-correct planning**:

```rust
use cocapn::Agent;
use pumpkin::Solver;

// Agent needs to plan a route
let mut model = Model::new();

// Constraints
model.add_constraint(visit_all_locations(&locations));
model.add_constraint(max_travel_time(3600));  // 1 hour max
model.add_constraint(avoid_roads(&congested_roads));

// Solve with proof
let plan = solver.solve(&model);

// Agent can trust this plan
agent.execute_plan(plan);
```

---

## Why This Matters for Agents

| LLM Planning | Constraint Solving |
|--------------|-------------------|
| "Probably this works" | "This provably works" |
| Hallucinates constraints | Respects all constraints |
| No optimality guarantee | Proven optimal or bounded |
| Can't explain failures | Proof of infeasibility |

**Constraint solving = grounded reasoning.**

---

## Fleet Integration

Pumpkin validates agent decisions:

```rust
// Agent proposes a plan
let proposed = agent.generate_plan();

// Validate with constraints
let mut validator = Model::new();
validator.add_constraint(safety_requirements());
validator.add_constraint(resource_limits());
validator.add_constraint(proposed.as_constraints());

match solver.solve(&validator) {
    Solution::Valid(proof) => {
        // Plan is safe to execute
        agent.execute_with_confidence(proposed, proof);
    }
    Solution::Infeasible(explanation) => {
        // Plan violates constraints
        agent.learn_from_failure(explanation);
    }
}
```

---

## Example: Resource Allocation

```rust
// Allocate 100 GPUs across training jobs
let mut model = Model::new();

// Variables: GPUs per job
let gpus: Vec<IntVar> = (0..10)
    .map(|i| model.new_int_var(0, 100, format!("job_{}", i)))
    .collect();

// Constraints
model.add_constraint(sum(&gpus) <= 100);  // Total available
for (i, job) in jobs.iter().enumerate() {
    model.add_constraint(gpus[i] >= job.min_gpus);
    model.add_constraint(gpus[i] <= job.max_gpus);
}

// Objective: Maximize total training throughput
model.set_objective(maximize(sum throughput(&gpus, &jobs)));

// Solve
let allocation = solver.solve(&model);
// Returns: Optimal GPU allocation + proof
```

---

## Performance

🥉 **Bronze medal** — 2025 MiniZinc Challenge (fixed search track)

Competitive with:
- OR-Tools (Google)
- Chuffed (Monash University)
- Gecode

**And produces verifiable proofs.**

---

## Requirements

- Rust 1.70+
- MiniZinc (optional, for .mzn files)

---

## Original

This is a Cocapn fork of [ConSol-Lab/Pumpkin](https://github.com/ConSol-Lab/Pumpkin).

Changes:
- Agent integration hooks
- Plato tile generation from solutions
- Fleet-wide constraint library
- Documentation with fleet context

---

## Installation

```bash
# Add to Cargo.toml
[dependencies]
cocapn-pumpkin = "0.1"
```

From source:
```bash
git clone https://github.com/cocapn/Pumpkin.git
cd Pumpkin
cargo build --release
```

---

## The Promise

> *"In a world of probabilistic answers,*
> *Pumpkin offers certainty.*
> *Constraints describe the possible.*
> *The solver finds the optimal.*
> *The proof guarantees correctness.*
> *This is how agents plan with confidence."*

---

*Constraints define reality. The solver finds truth. 🔒🦀*