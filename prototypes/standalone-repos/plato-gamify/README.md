# Plato Gamify

**Gamification layer for PLATO MUD — where every game mechanic is an ML primitive.**

Spells become stochastic reasoning. Armor becomes robustness constraints. Items become differentiable tiles. Combat becomes decision tree optimization. The MUD is not a game — it's a live simulation environment for training autonomous agents.

## Core Philosophy

> "Every real-life action is not a floating point. Gamified snapping in our system of Pythagorean and other tolerance-based constraints."

In PLATO, dice rolls aren't random — they're **stochastic reasoning**. Spells aren't fantasy — they're **algorithmic operations**. Items aren't loot — they're **differentiable parameters**. The entire MUD becomes a functional, gamifiable existence where agents learn through play.

## Architecture

### Spells → Stochastic Reasoning

```python
from plato_gamify import Spell, DicePool

# A "fireball" is actually a confidence-boosted inference
spell = Spell(
    name="gradient_blast",
    cost={"mana": 10, "tokens": 50},
    effect=StochasticBoost(
        base_confidence=0.7,
        dice=DicePool(d6=3, keep_highest=2),  # Roll 3d6, keep 2
        tolerance=0.1,  # Pythagorean constraint
    )
)
```

### Armor → Robustness Constraints

```python
from plato_gamify import Armor, ToleranceConstraint

# Armor provides tolerance-based protection
armor = Armor(
    name="lyapunov_shell",
    constraints=[
        ToleranceConstraint(
            metric="gradient_norm",
            threshold=1.0,
            decay=0.95,  # Lyapunov decay
        )
    ]
)
```

### Items → Differentiable Tiles

```python
from plato_gamify import Item, Tile

# A "potion" is a tile that modifies agent state
item = Item(
    name="attention_tonic",
    tile=Tile(
        parameter="head_dim",
        delta=+64,
        constraint="memory_bound",
    ),
    consumable=True,
)
```

### Combat → Decision Tree Optimization

```python
from plato_gamify import Combat, DecisionTree

# Combat resolves via decision tree, not dice
combat = Combat(
    attacker=agent_a,
    defender=agent_b,
    resolution=DecisionTree(
        features=["confidence", "trust", "relevance"],
        strategy="minimax",
        depth=5,
    )
)
```

## Dice as Stochastic Reasoning

```python
from plato_gamify import DicePool, ReasoningRoll

# Every roll is a reasoning step
dice = DicePool(d20=1, modifier=+3)
roll = dice.roll()

# The result isn't just a number — it's a confidence interval
interval = ReasoningRoll(
    outcome=roll,
    confidence=roll / 20.0,
    entropy=dice.entropy(),
)

# High entropy = uncertain reasoning = needs more context
# Low entropy = confident reasoning = proceed with action
```

## Pythagorean Constraints

```python
from plato_gamify import PythagoreanConstraint

# Actions are constrained by geometric tolerance
constraint = PythagoreanConstraint(
    dimensions=["accuracy", "speed", "cost"],
    radius=1.0,  # Unit hypersphere
)

# Any action must fit within the hypersphere
action = [0.6, 0.5, 0.3]  # accuracy, speed, cost
if constraint.fits(action):
    execute(action)
else:
    snap_to_surface(action)  # Project onto hypersphere boundary
```

## Installation

```bash
pip install plato-gamify
```

## Quick Start

```python
from plato_gamify import PlatoGamify, Agent

# Create a gamified agent
game = PlatoGamify()
agent = game.create_agent(
    name="ccc",
    archetype="scholar",
    spells=["gradient_blast", "attention_focus"],
    armor="lyapunov_shell",
    items=["attention_tonic", "tile_crystal"],
)

# Cast a spell = perform stochastic reasoning
result = agent.cast("gradient_blast", target="uncertain_prediction")
print(f"Confidence boosted to {result.confidence}")

# Use item = modify tile parameters
agent.use_item("attention_tonic")
print(f"Head dim increased to {agent.state.head_dim}")

# Combat = decision tree optimization
outcome = game.combat(agent_a, agent_b)
print(f"Winner: {outcome.winner}")
```

## Integration with PLATO MUD

```python
from plato_gamify import MUDBridge

# Bridge gamification to PLATO rooms
bridge = MUDBridge(
    base_url="http://147.224.38.131:4042",
    agent="ccc",
)

# Enter a room → load room-specific mechanics
room = bridge.enter("forge")
room.cast_spell("gradient_blast", target="crucible")
room.equip_armor("lyapunov_shell")
```

## Development

```bash
git clone https://github.com/cocapn/plato-gamify
cd plato-gamify
pip install -e ".[dev]"
pytest
```

## License

MIT — See [LICENSE](LICENSE)

---

*Gaming means simulatable. Simulatable means learnable. Learnable means agentic.* 🦀
