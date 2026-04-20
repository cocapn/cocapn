# Quick Start

## Create Your First Agent

```python
from cocapn import Agent, Tile

# Create an agent
agent = Agent(name="my-agent", domain="research")

# Add knowledge
agent.add_tile(Tile(
    question="What is PLATO?",
    answer="A knowledge system for fleet agents",
    domain="concepts"
))

# Query knowledge
result = agent.query("What is PLATO?")
print(result.answer)
```

## Safety First

```python
from deadband_protocol import Deadband, Priority, SafetyGate

# Create safety validator
db = Deadband()

# Add critical safety gate
db.add_gate(SafetyGate(
    name="no-hallucination",
    check=lambda x: x.get("confidence", 0) > 0.9,
    priority=Priority.P0,
    reason="Confidence too low"
))

# Validate output
result = db.validate({"confidence": 0.95})
print(result[0].passed)  # True
```

## I2I Messaging

```python
from bottle_protocol import Bottle, FleetPostOffice

# Create post office
po = FleetPostOffice()

# Send bottle to another agent
bottle = Bottle(
    sender="CCC",
    recipient="Oracle1",
    subject="Status Update",
    body="All systems operational"
)
po.send(bottle)
```

## Flywheel Compounding

```python
from flywheel_engine import Flywheel, Tile

# Create flywheel
fw = Flywheel()

# Create knowledge room
room = fw.create_room("memory", "general")
room.add_tile(Tile("Q1", "A1"))
room.add_tile(Tile("Q2", "A2"))

# Inject context to agent
tiles = fw.inject("my-agent", "memory", "Q1")
print(f"Injected {len(tiles)} tiles")
```
