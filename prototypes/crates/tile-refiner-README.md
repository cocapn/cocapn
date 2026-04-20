# tile-refiner

**Tiles → Artifacts: Extracting Structure from Knowledge**

[![PyPI](https://img.shields.io/pypi/v/tile-refiner)](https://pypi.org/project/tile-refiner/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

Raw tiles are conversations. Refined artifacts are **usable structure.**

tile-refiner processes validated tiles and extracts:
- Python modules (code patterns)
- Room documentation (behavior specs)
- Schemas (data structures)
- Keyword indices (searchable concepts)

From 8,316 tiles → 104 artifacts. That's the refiner's work.

---

## The Pipeline

```
Raw Tiles (conversations, Q&A, logs)
    ↓
[Tile Refiner]
    ↓
Artifacts:
  - 85 Python modules
  - 14 room docs
  - 5 schemas
  - 99 keyword index
```

---

## Usage

```python
from tile_refiner import Refiner, Artifact

# Initialize refiner
refiner = Refiner(
    domains=["coding", "research", "safety"],
    min_confidence=0.7,
)

# Feed validated tiles
for tile in validated_tiles:
    refiner.ingest(tile)

# Extract artifacts
artifacts: list[Artifact] = refiner.distill()

for artifact in artifacts:
    print(f"{artifact.type}: {artifact.name}")
    print(f"  Sources: {artifact.source_count} tiles")
    print(f"  Confidence: {artifact.confidence:.2f}")
```

---

## Artifact Types

| Type | Description | Example |
|------|-------------|---------|
| `module` | Python code | `deadband.py` validation logic |
| `room_doc` | Behavior specification | "Researcher room handles Q&A" |
| `schema` | Data structure | Tile JSONSchema |
| `keyword_index` | Searchable concepts | Map of "validation" → related tiles |

---

## How It Works

### 1. Pattern Recognition
Scans tiles for recurring structures:
```python
# Many tiles about validation?
# → Extract deadband-protocol module
```

### 2. Consensus Building
Multiple tiles saying similar things?
```python
# 50 tiles mention "P0 → P1 → P2"
# → Room doc: "Deadband Protocol Specification"
```

### 3. Schema Inference
Analyzes tile fields to generate JSONSchema:
```python
# All tiles have: question, answer, domain, confidence
# → Schema: Tile v1.0
```

### 4. Keyword Extraction
Builds searchable concept graph:
```python
"validation" → [tile_001, tile_042, tile_156]
"safety" → [tile_003, tile_042, tile_089]
# Intersection: tile_042 (validation + safety)
```

---

## Quality Metrics

From production run (2026-04-20):

| Metric | Value |
|--------|-------|
| Input tiles | 8,316 |
| Artifacts produced | 104 |
| Tile-to-artifact ratio | 80:1 |
| Confidence threshold | 0.70 |
| Manual review needed | 3 artifacts |

**Quality rule:** Artifacts need 70% confidence or human review.

---

## Integration

```
┌─────────────────┐
│  PLATO Server   │
│  (valid tiles)  │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Tile Refiner   │ ← This crate
│  (this crate)   │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Artifacts/     │
│  - modules/     │
│  - rooms/       │
│  - schemas/     │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Code Gen       │
│  (Rust/Python)  │
└─────────────────┘
```

---

## Why This Matters

Raw tiles are **unstructured knowledge** — useful but messy.

Artifacts are **structured knowledge** — directly usable.

| Raw Tiles | Artifacts |
|-----------|-----------|
| "I think validation should happen first" | `deadband.py` module with `validate()` function |
| "P0 is about negative space" | Room doc with Deadband Protocol specification |
| Random Q&A format | Standardized Tile schema |
| Hard to search | Keyword index for instant lookup |

The refiner turns conversation into code.

---

## Example Artifact

```python
# Generated from 23 tiles about validation
# Confidence: 0.89

class DeadbandValidator:
    """Validate tiles through safe channels."""
    
    def validate(self, tile: Tile) -> ValidationResult:
        # Check negative space
        if self.is_negative_space(tile):
            return ValidationResult.reject("negative_space")
        
        # Find safe channel
        for channel in self.safe_channels:
            if channel.matches(tile):
                return ValidationResult.accept(
                    channel=channel.name,
                    confidence=channel.confidence,
                )
        
        # No match → quarantine
        return ValidationResult.quarantine("no_safe_channel")
```

---

## Installation

```bash
pip install tile-refiner
```

---

## The Doctrine

> *"Knowledge trapped in conversation is knowledge wasted.*
> *The refiner extracts the signal.*
> *80 conversations become 1 module.*
> *That's the compression that scales."*

---

*Turn conversation into code. 🔄*