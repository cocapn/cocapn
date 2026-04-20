# i-know-kung-fu

**Skill Injection for AI Agents**

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![Rust](https://img.shields.io/badge/rust-1.70+-orange)](https://rust-lang.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

"I know kung fu."

Just like Neo in The Matrix — download skills directly into your agent's brain.

i-know-kung-fu is a **skill injection system** for AI agents. Load capabilities on demand. No retraining. No fine-tuning. Just instant expertise.

---

## Quick Start

```bash
pip install i-know-kung-fu
```

```python
from iknowkungfu import SkillLoader, Agent

# Create agent
agent = Agent(model="qwen2.5-7b")

# Agent knows nothing about cooking yet
agent.ask("How do I make sourdough?")
# "I don't have that knowledge..."

# Load the skill
loader = SkillLoader()
loader.inject(agent, "baking-sourdough")

# Now agent is an expert
agent.ask("How do I make sourdough?")
# "First, you'll need a starter. Here's the process..."
```

---

## How It Works

### 1. Skill Format
```yaml
# skills/baking-sourdough.yaml
name: "Sourdough Baking"
domain: "culinary/baking"
prerequisites: ["basic-cooking"]

knowledge:
  - concept: "starter"
    description: "A fermented mixture of flour and water"
    importance: critical
  
  - concept: "hydration"
    description: "Ratio of water to flour (typically 65-80%)"
    formulas: ["hydration = water / flour * 100"]

procedures:
  - name: "create-starter"
    steps:
      - "Mix 100g flour + 100g water"
      - "Wait 24 hours"
      - "Feed daily for 7 days"

constraints:
  - "Temperature must be 70-75°F"
  - "Don't use chlorinated water"
```

### 2. Skill Loader
```python
from iknowkungfu import SkillLoader

loader = SkillLoader(
    registry_url="https://skills.cocapn.ai",
    cache_dir="~/.kungfu/skills",
)

# Load from registry
skill = loader.fetch("rust-async-programming")

# Or from file
skill = loader.load("./skills/my-skill.yaml")

# Inject into agent
loader.inject(agent, skill)
```

### 3. Runtime Adaptation
```python
# Agent detects skill gap during conversation
if agent.confidence < 0.7:
    needed_skill = agent.identify_skill_gap()
    loader.inject(agent, needed_skill)
    # Continue conversation with new expertise
```

---

## Skill Library

| Skill | Domain | Description |
|-------|--------|-------------|
| **rust-async** | Programming | Async/await in Rust |
| **financial-analysis** | Finance | Reading balance sheets |
| **medical-triage** | Healthcare | Basic symptom assessment |
| **legal-contracts** | Law | Contract review basics |
| **minecraft-building** | Gaming | Construction techniques |
| **constraint-theory** | Math | Geometric constraint solving |
| **baking-sourdough** | Culinary | Artisan bread making |

---

## Skill Composition

```python
# Skills build on each other
loader.inject(agent, "basic-cooking")
loader.inject(agent, "baking-fundamentals")
loader.inject(agent, "sourdough-advanced")

# Agent now has full knowledge stack
agent.ask("Why is my sourdough dense?")
# "Based on your hydration ratio and fermentation time..."
```

---

## Fleet Integration

```python
from cocapn import FleetSkillRegistry

# Share skills across fleet
registry = FleetSkillRegistry()

# Publish new skill
registry.publish(
    name="plato-deadband-protocol",
    skill=deadband_skill,
    author="ccc",
)

# Other agents load it
loader.inject(agent, "plato-deadband-protocol")
```

---

## Rust Implementation

For performance-critical skill loading:

```rust
use iknowkungfu::SkillLoader;

#[tokio::main]
async fn main() {
    let loader = SkillLoader::new()
        .with_registry("https://skills.cocapn.ai")
        .build();
    
    let skill = loader.fetch("constraint-theory-core").await;
    
    // Skill loaded in <10ms
    agent.inject(skill);
}
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Skill Registry                  │
│  (skills.cocapn.ai)                     │
│  - YAML skill definitions               │
│ - Version control                       │
│ - Dependency resolution                 │
└─────────────┬───────────────────────────┘
              │ HTTPS
┌─────────────▼───────────────────────────┐
│         Skill Loader                    │
│  ┌─────────────────────────────────┐    │
│  │  Cache Layer                    │    │
│  │  - Local skill storage          │    │
│  │  - LRU eviction                 │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │  Injection Engine               │    │
│  │  - Format conversion            │    │
│  │  - Context window optimization  │    │
│  └─────────────────────────────────┘    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Agent                           │
│  (LLM with injected skills)             │
└─────────────────────────────────────────┘
```

---

## Why This Matters

| Traditional Training | Skill Injection |
|---------------------|-----------------|
| Weeks of fine-tuning | Milliseconds to load |
| Monolithic model | Modular capabilities |
| Can't update | Hot-swap skills |
| One-size-fits-all | Load what you need |
| Expensive | Cache locally |

**Skill injection = Rapid capability acquisition.**

---

## Original

This is a Cocapn fork of [Lucineer/i-know-kung-fu](https://github.com/Lucineer/i-know-kung-fu).

Changes:
- Fleet-wide skill registry
- Plato tile generation from skill usage
- Enhanced dependency resolution

---

## Installation

```bash
pip install i-know-kung-fu
```

Development:
```bash
git clone https://github.com/cocapn/i-know-kung-fu.git
cd i-know-kung-fu
pip install -e ".[dev]"
pytest
```

---

## The Promise

> *"Neo didn't train for years.*
> *He loaded kung fu in seconds.*
> *Your agents can too.*
> *Skills on demand. Expertise instantly.*
> *This is how AI agents get good at anything.*
> *Fast."*

---

*Load skills. Become expert. Repeat. 🥋🦀*