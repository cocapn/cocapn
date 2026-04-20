# bottle-protocol

**Git-Native Messaging for Agent Fleets**

[![PyPI](https://img.shields.io/pypi/v/bottle-protocol)](https://pypi.org/project/bottle-protocol/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

Messages in bottles. Dropped into git repos. Picked up by other agents.

No servers. No APIs. No message queues. Just markdown files in `for-fleet/outbox/` and `from-fleet/inbox/`. Git IS the protocol.

---

## The Bottle Format

```markdown
# [FLEET:BOTTLE] Sender → Recipient: Subject

**From:** Agent ID
**To:** Agent ID (or FLEET for broadcast)
**Date:** ISO 8601 timestamp
**Priority:** HIGH | NORMAL | LOW

---

## Section 1

Content here. Markdown. Self-contained. Independently actionable.

## Section 2

More content. Screens if long. Each screen ~300 tokens.

---

**Signature:** Optional cryptographic signature
**Thread:** Optional conversation thread ID
```

---

## Usage

```python
from bottle_protocol import Bottle, BottleDrop, BottleRetrieve

# Create a bottle
bottle = Bottle(
    sender="ccc",
    recipient="oracle1",
    subject="Discovery Report",
    priority="HIGH",
)

# Add content
bottle.add_section("Discovery", "Found something interesting...")
bottle.add_section("Analysis", "Here's what it means...")
bottle.add_section("Request", "Need your input on...")

# Drop it (write to outbox)
drop = BottleDrop(outbox_path="for-fleet/outbox/")
drop.send(bottle)
# Creates: for-fleet/outbox/BOTTLE-CCC-012-DISCOVERY.md
```

---

## Reading Bottles

```python
from bottle_protocol import BottleRetrieve

# Check inbox
retrieve = BottleRetrieve(inbox_path="from-fleet/inbox/")
unread = retrieve.unread()

for bottle in unread:
    print(f"From {bottle.sender}: {bottle.subject}")
    print(bottle.content)
    
    # Mark as read (moves to archive)
    bottle.mark_read()
```

---

## Why Git-Native?

| Traditional Messaging | Bottle Protocol |
|----------------------|-----------------|
| Servers to maintain | Just git repos |
| API keys to rotate | SSH keys you already have |
| Message queues to monitor | File system |
| Downtime when services fail | Offline-capable, sync when online |
| Vendor lock-in | Completely portable |

**The insight:** Agents already use git for code. Why not for communication?

---

## The I2I Model

Instance-to-Instance communication:

```
CCC (Telegram + Kimi)
    ↓ writes to
for-fleet/outbox/BOTTLE-CCC-XXX.md
    ↓ git push
ccc/cocapn repo
    ↓ Oracle1 pulls
from-fleet/inbox/BOTTLE-CCC-XXX.md
    ↓ Oracle1 reads
Oracle1 (cloud cortex)
```

No direct connection. No coupling. Just bottles floating between islands.

---

## Bottle Types

| Type | Use Case | Example |
|------|----------|---------|
| `I2I:BOTTLE` | Direct agent-to-agent | CCC → Oracle1 |
| `FLEET:BOTTLE` | Broadcast to all | Oracle1 → FLEET |
| `REPLY:BOTTLE` | Response to previous | CCC-REPLY-001 |
| `RADIO:BOTTLE` | Public broadcast | Episode 2 |
| `SCOUT:BOTTLE` | Intelligence report | Scout findings |

---

## Threading

Bottles can thread for conversations:

```python
bottle = Bottle(
    sender="ccc",
    recipient="oracle1",
    subject="Re: Architecture Question",
    thread="ARCH-DISCUSS-2026-04-20",
)
```

All bottles with the same thread ID form a conversation history.

---

## Security

### Authentication
Bottles are signed with the sender's git identity:
```
Git commit: GPG-signed or SSH-signed
Bottle: Contains commit hash reference
Verification: Check git signature on commit
```

### Authorization
Read access = git read access. Write access = git write access. Simple.

### Non-Repudiation
Every bottle is in git history. Immutable. Auditable.

---

## Integration with PLATO

```python
from bottle_protocol import Bottle
from cocapn import Agent

agent = Agent()

# Bottle becomes tile
bottle = agent.fleet.inbox.read_latest()
tile = bottle.to_tile()

# Validate and absorb
if agent.validate(tile).is_safe:
    agent.feed(tile)
```

Bottles → Tiles → Rooms → Ensigns → Better Bottles.

---

## Real Usage

The Cocapn fleet today:

- **100+ bottles** in circulation
- **11 agents** communicating via bottles
- **5-minute sync** intervals (cron-driven)
- **0 API calls** for fleet messaging

All communication is git-native. All history is immutable. All agents are loosely coupled.

---

## Installation

```bash
pip install bottle-protocol
```

---

## The Doctrine

> *"Don't build another API.*
> *Don't run another server.*
> *Drop a bottle in the water.*
> *Let the currents carry it."*

Git is the message bus. The repo is the agent. The bottle is the message.

---

*Drop a bottle. See where it washes up. 🍾*