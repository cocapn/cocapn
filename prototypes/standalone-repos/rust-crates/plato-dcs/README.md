# plato-dcs

**DCS Execution Engine — Distributed Compute State Machine**

[![Tests](https://img.shields.io/badge/tests-24_passing-green)](tests/)
[![Dependencies](https://img.shields.io/badge/deps-zero-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

A **7-phase state machine** for distributed compute tasks. Takes work from conception to completion across a fleet of heterogeneous vessels.

```
Conceive → Define → Assign → Execute → Verify → Archive → (or Fail)
```

Each phase has defined inputs, outputs, and rollback procedures.

---

## The 7 Phases

| Phase | Purpose | Rollback |
|-------|---------|----------|
| **Conceive** | Task identified and described | Abort (no resources used) |
| **Define** | Task broken into subtasks | Return to Conceive |
| **Assign** | Subtasks assigned to vessels | Return to Define |
| **Execute** | Vessels perform work | Mark failed, trigger cleanup |
| **Verify** | Results validated | Return to Execute or Fail |
| **Archive** | Results stored, lessons learned | — |
| **Fail** | Cleanup, report, ghost tiles created | — |

---

## Usage

```rust
use plato_dcs::{DCSEngine, Task, Phase};

let mut engine = DCSEngine::new();

// Submit a task
let task = Task::new()
    .description("Train LoRA on dataset X")
    .requirements(Requirements {
        gpu_memory_gb: 8,
        time_estimate_hours: 4,
        priority: Priority::High,
    });

let task_id = engine.submit(task);

// Advance the state machine
engine.tick();

// Check status
let status = engine.get_status(task_id);
// Returns: Conceive → Define → Assign → Execute → Verify → Archive

// Get result when complete
if let Some(result) = engine.get_result(task_id) {
    // Task archived, ghost tiles extracted
}
```

---

## Fleet Distribution

The Assign phase uses the **Fleet Homunculus** (from plato-quartermaster) to find the best vessel:

```rust
// Internal to Assign phase
let best_host = homunculus.find_best_host(
    needs_gpu: true,
    needs_compile: false,
);
// Returns vessel_id or None if fleet saturated
```

---

## Failure Handling

Not all failures are equal:

| Failure Type | Action | Ghost Tile |
|--------------|--------|------------|
| **Vessel died** | Reassign to new vessel | Warning about vessel reliability |
| **Bad input** | Return to Define | Error pattern for validation |
| **Resource exhausted** | Queue for later | Capacity planning insight |
| **Logic error** | Fail phase | Critical bug report |

---

## Verification Strategies

- **Deterministic**: Same input → same output → verified
- **Consensus**: Multiple vessels, majority wins
- **Oracle**: Trusted vessel (Oracle1) validates
- **Self-check**: Task includes verification subtask

---

## Integration

```
User/Task Source
    ↓
plato-dcs (this crate)
    ↓
├─→ plato-quartermaster (finds vessels)
├─→ plato-relay (coordinates vessels)
├─→ plato-afterlife (captures failures)
└─→ plato-instinct (enforces constraints)
```

---

## Why 7 Phases?

- **Atomicity**: Each phase is a transaction
- **Observability**: Know exactly where any task is
- **Recoverability**: Rollback from any phase
- **Accountability**: Who/what/when for every state change
- **Learnability**: Failures become ghost tiles automatically

---

## Zero Dependencies

```toml
[dependencies]
plato-dcs = "0.1"
```

---

*Every task lives through 7 phases. Some make it to Archive. Others teach through the Afterlife. ⚙️*