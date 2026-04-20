# plato-unified-belief

**Belief as One Score**

[![Tests](https://img.shields.io/badge/tests-17_passing-green)](tests/)
[![Dependencies](https://img.shields.io/badge/deps-zero-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

A **unified belief system** that compresses all uncertainty into a single scalar: the belief score.

Instead of separate confidence, uncertainty, and probability fields, everything becomes one score:

```
belief ∈ [0.0, 1.0]

0.0 = Certain false
0.5 = Maximum uncertainty  
1.0 = Certain true
```

This is the mathematics of "I don't know yet" — and exactly how much I don't know.

---

## Why One Score?

Multiple uncertainty representations cause bugs:
- Confidence: 0.95
- Uncertainty: 0.1
- Probability: 0.87
- Entropy: 0.3

Which is right? **None.** They're measuring different things inconsistently.

**Unified belief** measures one thing: *How much should the system act as if this is true?*

---

## The Belief Calculus

```rust
use plato_unified_belief::{Belief, Evidence};

// Start with prior belief
let mut belief = Belief::from_prior(0.5);  // Complete uncertainty

// Update with evidence
belief.update(Evidence {
    source_confidence: 0.9,
    observation_count: 100,
    positive_outcomes: 87,
});

// Result: belief moves toward 0.87
// More evidence → more certainty → closer to 0 or 1

// Combine beliefs from multiple sources
let combined = Belief::combine(&[belief1, belief2, belief3]);
// Uses Bayesian combination with source weighting
```

---

## Belief Operations

| Operation | Result |
|-----------|--------|
| `belief.update(evidence)` | Move toward observed frequency |
| `belief.combine(other)` | Bayesian weighted combination |
| `belief.decay(halflife)` | Increase uncertainty over time |
| `belief.threshold(action)` | Act if belief > threshold |
| `belief.to_odds()` | Convert to log-odds for math |

---

## Tile Belief Integration

Every PLATO tile has a belief score:

```rust
struct Tile {
    question: String,
    answer: String,
    domain: Domain,
    belief: Belief,  // ← This replaces confidence + uncertainty
    validity: TemporalValidity,
}
```

- **High belief (0.8-1.0)**: Use as ground truth
- **Medium belief (0.3-0.7)**: Label as uncertain, seek confirmation
- **Low belief (0.0-0.2)**: Flag as likely false, investigate

---

## Fleet Consensus

When vessels disagree, unified belief resolves it:

```rust
// Oracle1 says X with belief 0.9
// JetsonClaw1 says not-X with belief 0.8
// CCC says X with belief 0.7

let consensus = Belief::combine_weighted(&[
    (oracle1_belief, oracle1_trust_score),
    (jc1_belief, jc1_trust_score),
    (ccc_belief, ccc_trust_score),
]);

// Result: weighted by vessel reliability
// Fleet acts on consensus belief
```

---

## Deadband Integration

The Deadband Protocol uses belief thresholds:

```rust
// P0 (Map negative space): belief < 0.1
// P1 (Find safe channels): belief > 0.7  
// P2 (Optimize): belief > 0.9

fn priority_from_belief(belief: Belief) -> Priority {
    match belief.value() {
        b if b < 0.1 => Priority::P0,  // Map the negative space
        b if b > 0.9 => Priority::P2,  // Safe to optimize
        _ => Priority::P1,              // Proceed with caution
    }
}
```

---

## Zero Dependencies

```toml
[dependencies]
plato-unified-belief = "0.1"
```

---

*One score. Infinite nuance. The mathematics of not knowing yet. 🎯*