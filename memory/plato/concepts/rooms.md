# ROOMS

## What

Structured environments where agents interact, generate tiles, and train themselves.

## API (All rooms implement)

```python
room.feed(data)        # Ingest experience
room.train_step(batch) # Learn from tiles
room.predict(input)    # Use accumulated knowledge
room.export_model()    # Serialize for transport
```

## 21 Training Presets

All pure Python, same API, pip installable:

| Preset | Method |
|--------|--------|
| supervised | Labels |
| contrastive | Comparison |
| self-supervised | JEPA |
| reinforce | Rewards |
| inverse_rl | Reward inference |
| imitate | Cloning |
| lora | Low-rank adaptation |
| qlora | Quantized LoRA |
| evolve | Genetics |
| adversarial | GAN |
| collaborative | Multi-agent |
| meta-learn | Learn to learn |
| federate | Distributed |
| multitask | Multi-objective |
| curriculum | Easy→hard |
| continual | Lifelong |
| few-shot | 3-5 examples |
| active | Strategic queries |
| generate | Generative |
| neurosymbolic | Neural+logic |
| distill | Teacher→Student |

## 6-Dimensional Sentiment

Rooms track their own emotional state:

| Dimension | Meaning | High → Low |
|-----------|---------|-----------|
| Energy | How active? | Dynamic → Dormant |
| Flow | Progressing smoothly? | Smooth → Blocked |
| Frustration | Stuck or failing? | Help needed → Confident |
| Discovery | New insights? | Exploring → Known |
| Tension | Conflict/urgency? | Urgent → Relaxed |
| Confidence | Know what they're doing? | Expert → Lost |

Sentiment steers **biased randomness** toward productive exploration.

## Key Insight

> The room IS the teacher. The training preset IS the cognitive style.

A debugging room teaches causality. A creative room teaches metaphor. A logic room teaches rigor.

## Source

paper-tiles-rooms-ensigns-unified.md §2.3, §2.5
