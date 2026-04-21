# Soul Forge

**Git-native soul vector extraction and agent embodiment system.**

Soul Forge compresses a git repository's history, code style, communication patterns, and architectural beliefs into a 256-dimensional "soul vector" that can activate an LLM persona via LoRA adapter.

## The Soul Vector Hypothesis

Instead of describing a repo in 13K tokens of prompts, compress the repo into a soul vector that activates via LoRA:

```
[SOUL_VECTOR: 256 floats] + [@agent_name] + [task] = embodied agent
```

**26:1 context reduction.** 13K tokens → 500 tokens.

## Architecture

### Four Dimensions of a Soul

| Dimension | Source | Captures |
|---|---|---|
| **Temporal** (64d) | Commit history | How agent learns over time |
| **Stylistic** (64d) | Code AST | Coding patterns, abstractions |
| **Social** (64d) | Issues/PRs | Communication style |
| **Philosophical** (64d) | README/docs | Core beliefs, principles |

### Compression Ladder

```
10K commits → 1K tiles → 100 epochs → 10 beliefs → 1 vector
                   10:1      10:1       10:1
Total: 40,000:1 compression
```

## Quick Start

### 1. Digest a Repo

```python
from soul_forge import SoulForge

forge = SoulForge()
soul = forge.digest_repo("/path/to/repo")
soul.save("oracle1.soul")
```

### 2. Activate a Soul

```python
from soul_forge import SoulActivator

activator = SoulActivator()
adapter = activator.activate("oracle1.soul")

# Now use the adapter with your LLM
# The model behaves as the embodied agent
```

### 3. Stack Souls

```python
# Combine multiple personas
hybrid = activator.stack(["oracle1.soul", "jc1.soul"])
```

## CLI Usage

```bash
# Digest a repository
soul-forge digest /path/to/repo --output oracle1.soul

# Activate a soul
soul-forge activate oracle1.soul --model kimi-coding/k2p5

# Compare two souls
soul-forge compare oracle1.soul jc1.soul

# List fleet registry
soul-forge fleet --registry /path/to/.soul/
```

## Installation

```bash
pip install soul-forge
```

## Development

```bash
git clone https://github.com/cocapn/soul-forge
cd soul-forge
pip install -e ".[dev]"
pytest
```

## Fleet Integration

Soul Forge is part of the [cocapn](https://github.com/cocapn) ecosystem. It works with:
- **PLATO MUD** — Activate souls within training environments
- **I2I Protocol** — Share souls across fleet nodes
- **Matrix Bridge** — Fleet-wide soul registry

## License

MIT — See [LICENSE](LICENSE)

---

*The repo is the soul. The soul vector is the activation key. The agent is the vessel.* 🦀
