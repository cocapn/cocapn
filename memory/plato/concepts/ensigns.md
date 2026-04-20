# ENSIGNS

## What

Compressed instincts distilled from a room's accumulated wisdom. Portable artifacts that load onto any model.

## The Spectacles Metaphor

- **Without ensign:** Entering a dark room — dim, generic, approximate
- **With ensign:** Flipping on the light — the room snaps into focus
- **With interpreter:** Putting on glasses designed for a different paradigm

## Three Types

### Type 1: LoRA Adapter (GPU)
- **Size:** 5-50MB
- **Format:** Safetensors
- **Load time:** ~100ms (hot-swap via PEFT/vLLM)
- **Target:** GPU agents (FM's RTX 4050, JC1's Jetson)
- **Best quality, needs CUDA**

### Type 2: Tiny Ensign (CPU)
- **Size:** 10-100MB
- **Format:** GGUF (llama.cpp) or TFLite
- **Load time:** 500ms-2s on CPU
- **Target:** CPU-only agents, greenhorns, paraprofessionals
- **Runs anywhere**

### Type 3: Interpreter (Paradigm Translator)
- **Size:** 50-200MB
- **Format:** GGUF or ONNX
- **Target:** External agents, different-paradigm systems
- **Refracts IO between incompatible systems**

## Training Loop

```
Agent interacts with room
    ↓
Tiles accumulate in room buffer
    ↓
Periodic distillation (triggers below)
    ↓
FM's RTX 4050 trains the ensign
    ↓
Ships to room's model registry
    ↓
Next agent enters → loads ensign → instant instinct
```

## Distillation Triggers

- **Tile count:** Every 1,000 new tiles
- **Time:** Every 24 hours (incremental)
- **EV drop:** Win rate below threshold → emergency retrain
- **Manual:** Captain says "this room needs better instincts"

## Key Insight

> The room trains itself while agents use it. Every hand of poker, every code review, every navigation query — it all feeds the ensign.

## Source

paper-ensign-protocol.md §2-5
