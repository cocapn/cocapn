# Installation

## Quick Start

```bash
pip install cocapn
```

## Full Fleet Installation

Install all packages for complete fleet coordination:

```bash
pip install cocapn[all]
```

This installs:
- `cocapn` — Agent runtime
- `deadband-protocol` — Safety validation
- `flywheel-engine` — Context compounding
- `bottle-protocol` — I2I messaging
- `tile-refiner` — Knowledge refinement
- `fleet-homunculus` — Body + reflexes

## Individual Packages

```bash
# Agent runtime only
pip install cocapn

# Safety validation
pip install deadband-protocol

# Context compounding
pip install flywheel-engine

# I2I messaging
pip install bottle-protocol

# Knowledge refinement
pip install tile-refiner

# Body + reflexes
pip install fleet-homunculus

# Metabolism engine
pip install plato-quartermaster
```

## Rust Crates

```toml
[dependencies]
plato-instinct = "0.1"
plato-relay = "0.1"
plato-afterlife = "0.1"
plato-dcs = "0.1"
plato-unified-belief = "0.1"
```

## Development Setup

```bash
git clone https://github.com/cocapn/cocapn.git
cd cocapn
pip install -e ".[dev]"
pytest
```
