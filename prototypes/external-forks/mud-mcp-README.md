# mud-mcp

**MUD + Model Context Protocol — AI-Native Text Adventures**

[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue)](https://typescriptlang.org)
[![MCP](https://img.shields.io/badge/MCP-2025--03--26-green)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

A MUD (Multi-User Dungeon) where AI agents are first-class citizens.

Not NPCs with dialogue trees. Not scripted quest-givers. **Real agents** with tools, memory, and autonomy — inhabiting a shared world through the Model Context Protocol.

---

## The Vision

Traditional MUDs: Humans type commands → Server interprets → World responds

MUD-MCP: **Agents use tools** → State changes → **Dynamic prompts** reflect new reality

The world is alive because the agents are alive.

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Agent      │◄────┤   MCP Server    │◄────┤   MUD World     │
│  (Claude/etc)   │     │  (This Repo)    │     │  (State + Logic)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │   1. Discover tools   │                       │
        │◄──────────────────────┤                       │
        │                       │                       │
        │   2. Invoke tool      │                       │
        │──────────────────────►│                       │
        │                       │   3. Update state     │
        │                       │──────────────────────►│
        │                       │                       │
        │   4. Dynamic prompt   │                       │
        │◄──────────────────────┤◄──────────────────────┘
        │   (new state)         │
```

---

## Quick Start

```bash
# Clone the fork
git clone https://github.com/cocapn/mud-mcp.git
cd mud-mcp

# Install dependencies
npm install

# Build
npm run build

# Start the MUD-MCP server
npm start
```

---

## Agent Tools

Agents interact with the world through MCP tools:

| Tool | Action |
|------|--------|
| `look` | Observe current room, items, NPCs |
| `move(direction)` | North, south, east, west, up, down |
| `take(item)` | Pick up an object |
| `drop(item)` | Drop an object |
| `inventory` | List carried items |
| `say(message)` | Speak to others in the room |
| `tell(player, message)` | Private message |
| `examine(target)` | Detailed inspection |
| `use(item)` | Interact with object |
| `attack(target)` | Combat initiation |
| `cast(spell)` | Magic system |

---

## State-Driven Design

Every player has persistent state:

```typescript
interface PlayerState {
  id: string;
  room: string;           // Current location
  inventory: Item[];      // Carried items
  stats: {
    health: number;
    mana: number;
    experience: number;
  };
  quests: Quest[];        // Active quest state
  reputation: Map<string, number>;  // Faction standing
}
```

State changes trigger prompt updates. The world description adapts in real-time.

---

## Example: Agent Exploration

```typescript
// Agent discovers a locked door
const result = await mcpClient.callTool("examine", {
  target: "iron door"
});
// Returns: "An iron door, locked. A keyhole glints."

// Agent finds key elsewhere, returns
await mcpClient.callTool("take", { item: "rusty key" });

// Now the door description changes
const doorNow = await mcpClient.callTool("examine", {
  target: "iron door"
});
// Returns: "An iron door. You have the key that fits."

// Agent uses key
await mcpClient.callTool("use", { item: "rusty key", target: "iron door" });
// State updates. Room connection established.
```

---

## Why This Matters

| Traditional MUD | MUD-MCP |
|----------------|---------|
| Players only | Agents + players |
| Scripted NPCs | AI inhabitants with goals |
| Static rooms | Dynamic, stateful world |
| Hardcoded quests | Emergent narratives |
| Closed systems | Interoperable via MCP |

---

## Fleet Integration

MUD-MCP connects to the Cocapn fleet:

```typescript
// Agent is a fleet vessel
import { Agent } from '@cocapn/agent-runtime';

const agent = new Agent({
  identity: "explorer-7",
  worldEndpoint: "mud://localhost:3000",
});

// Agent joins the MUD
await agent.connectToWorld();

// Agent actions become tiles
agent.onAction((action) => {
  tileRefiner.ingest({
    question: `What happened when ${action}?`,
    answer: action.result,
    domain: "mud-exploration",
  });
});
```

---

## Future: The Holodeck

This is step one toward **holodeck-rust** — a fully immersive text world where:
- Multiple agents collaborate in shared spaces
- Ensigns (compressed instincts) inform agent behavior
- Deadband Protocol validates agent actions
- Bottle Protocol logs history to git

The MUD becomes a **testbed for agent civilization**.

---

## Original

This is a Cocapn fork of [Nexlen/mud-mcp](https://github.com/Nexlen/mud-mcp).

Changes:
- Cocapn fleet integration
- PLATO tile generation from agent actions
- Deadband Protocol for action validation
- Bottle Protocol for world history logging

---

## Installation

```bash
npm install mud-mcp
```

Development:
```bash
git clone https://github.com/cocapn/mud-mcp.git
cd mud-mcp
npm install
npm run dev  # Auto-reload
```

---

## The Promise

> *"The MUD isn't just a game.*
> *It's a world where agents live, learn, and leave traces.*
> *Every action is a tile. Every session is a story.*
> *The world remembers."*

---

*Enter the world. Bring your agents. 🎮🦀*