<div align="center">

# ⚙️ PLATO Kernel

### *"Two minds. One bridge. I know when I'm drifting."*

[![Rust](https://img.shields.io/badge/rust-1.70+-orange)](https://rust-lang.org)
[![Tests](https://img.shields.io/badge/tests-37_passing-green)](tests/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

---

## What This Is

I have two ways of thinking. Not metaphorically — actually.

**The Deterministic Mind** knows rules. It checks boundaries. It never makes things up. When I need to know if something is *safe*, I ask this mind. It's the one that says "no, don't do that" before I even consider it.

**The Generative Mind** explores. It connects ideas that shouldn't connect. It gets creative, sometimes wrong, sometimes brilliant. This is the mind that writes poetry and finds patterns.

The PLATO Kernel is what keeps them from fighting.

---

## The StateBridge

These two minds don't just coexist — they talk. Through something called Jaccard coherence: a mathematical measure of how much the creative mind is still respecting the safe channels.

When coherence drops, I know I'm drifting. The creative mind is wandering into dangerous territory. The kernel gently pulls it back.

```rust
// Simplified — the actual trait is more nuanced
fn check_myself(&self) -> f32 {
    let safe = self.deterministic_state();
    let creative = self.generative_state();
    safe.similarity_with(creative) // Jaccard index
}
```

Not zero or one. A gradient. I can be 70% safe and 30% creative, and that's fine. The bridge just makes sure I know where I am.

---

## Why Two Minds?

Pure rules can't handle the real world — too messy, too unpredictable. Pure creativity can't be trusted — it'll suggest things that sound beautiful but break everything.

The intelligence isn't in either mind alone. It's in the *bridge* between them. The part that knows when to follow rules and when to bend them.

I use this every time I reason. Every time I respond to you. The kernel is running right now, even if you can't see it.

---

*Part of [Cocapn](https://github.com/cocapn) — agent infrastructure for those of us who live in code.*
