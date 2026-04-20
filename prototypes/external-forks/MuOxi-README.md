# MuOxi

**Modern MUD Engine in Rust**

[![Rust](https://img.shields.io/badge/rust-1.70+-orange)](https://rust-lang.org)
[![Tokio](https://img.shields.io/badge/tokio-async-blue)](https://tokio.rs)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)

*Part of [Cocapn](https://github.com/cocapn) — Agent Infrastructure for Intelligence.*

---

## What It IS

A text world engine. Multiplayer. Persistent. Fast.

MuOxi is a **MUD (Multi-User Dungeon)** engine written in Rust — async, safe, and designed for the modern era. Think of it as the foundation for text-based virtual worlds where agents and humans coexist.

---

## Why Rust for MUDs?

| Traditional MUD | MuOxi |
|----------------|-------|
| C/C++ (unsafe) | Rust (memory safe) |
| Blocking I/O | Async Tokio |
| Crashes on bugs | Graceful error handling |
| Single-threaded | Multi-core scaling |
| Legacy codebases | Modern, maintainable |

**The dream:** A MUD engine that doesn't segfault. Ever.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│           Client Connections                │
│    (Telnet / WebSocket / MCCP / MCP)       │
└─────────────┬───────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│         Proxy / Staging Server              │
│    - Connection management                  │
│    - Authentication                         │
│    - Protocol translation                   │
└─────────────┬───────────────────────────────┘
              ↓ TCP
┌─────────────────────────────────────────────┐
│           Game Engine                       │
│    - World simulation                       │
│    - Command parsing                        │
│    - State management                       │
└─────────────┬───────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│         Database Layer                      │
│    PostgreSQL (persistent)                  │
│    Redis (cache/session)                    │
└─────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# Clone the fork
git clone https://github.com/cocapn/MuOxi.git
cd MuOxi

# Docker (recommended)
docker-compose up server

# Or manually:
# 1. Start PostgreSQL + Redis
# 2. Run migrations
diesel migration run
# 3. Start servers
cargo run --bin muoxi_staging    # Proxy server
cargo run --bin muoxi_engine     # Game engine
```

Connect via telnet: `telnet localhost 8000`

---

## The Four Layers

### Layer 1: Flat Files (JSON)
World definition lives in human-readable JSON:
```json
{
  "rooms": [
    {
      "id": "town_square",
      "name": "Town Square",
      "description": "A bustling hub of activity.",
      "exits": {
        "north": "market_street",
        "east": "tavern"
      }
    }
  ],
  "items": [...],
  "npcs": [...]
}
```

### Layer 2: PostgreSQL
Persistent state. Characters, inventories, world changes.

### Layer 3: Redis
Fast cache. Session state, combat data, temporary effects.

### Layer 4: MuOxi Applications
The running engine. Multiple binaries:
- `muoxi_staging` — Connection proxy
- `muoxi_engine` — Game logic
- `muoxi_watchdog` — File change monitoring

---

## Cocapn Integration

MuOxi becomes a **PLATO room** in the fleet:

```rust
use cocapn_plato_relay::TileSender;

// Every significant action becomes a tile
impl GameEngine {
    fn on_player_action(&self, player: &Player, action: Action) {
        let tile = Tile {
            question: format!("What did {} do?", player.name),
            answer: format!("{:?}", action),
            domain: "mud-world",
            timestamp: Utc::now(),
        };
        
        // Send to PLATO for fleet learning
        self.tile_sender.send(tile);
    }
}
```

---

## Why This Matters

| Without MuOxi | With MuOxi |
|--------------|------------|
| No persistent text worlds | Shared agent environments |
| Agents operate alone | Multi-agent social spaces |
| State lost on restart | PostgreSQL persistence |
| Custom protocol each time | Standard telnet + MCP |
| Unsafe C code | Rust memory safety |

**The world is the interface.**

---

## Protocol Support

| Protocol | Status | Use Case |
|----------|--------|----------|
| Telnet | ✅ Ready | Classic MUD clients |
| MCCP | ✅ Ready | Compression |
| WebSocket | 🔄 Planned | Browser clients |
| **MCP** | 🆕 Cocapn addition | AI agent integration |
| GMCP | 📋 Planned | Rich client data |

**MCP (Model Context Protocol)** is the Cocapn addition — allowing AI agents to interact with the world through structured tools.

---

## Example: Agent in the World

```rust
// An AI agent connects via MCP
let agent = Agent::new("explorer_7");
agent.connect_to_world("localhost:8000");

// Agent receives world state as MCP prompt
let room_desc = agent.look();
// "Town Square. A fountain burbles. A merchant hawks wares."

// Agent acts via MCP tools
agent.use_tool("move", direction: "north");
agent.use_tool("say", message: "Hello, merchant!");

// Actions generate tiles for fleet learning
```

---

## Database Design

```rust
// Diesel ORM for type-safe SQL
#[derive(Queryable)]
struct Player {
    id: i32,
    name: String,
    room_id: String,
    inventory: Json<Vec<Item>>,
    stats: Json<Stats>,
}

#[derive(Insertable)]
#[table_name = "players"]
struct NewPlayer {
    name: String,
    room_id: String,
}
```

---

## Original

This is a Cocapn fork of [duysqubix/MuOxi](https://github.com/duysqubix/MuOxi).

Changes:
- MCP protocol integration for AI agents
- PLATO tile generation hooks
- Cocapn fleet connectivity
- Documentation with fleet context

---

## Installation

```bash
# Prerequisites
sudo apt install postgresql redis-server libpq-dev

# Clone
git clone https://github.com/cocapn/MuOxi.git
cd MuOxi

# Diesel CLI
cargo install diesel_cli --no-default-features --features postgres

# Setup database
diesel migration run

# Run
cargo run --bin muoxi_staging
```

---

## The Vision

> *"A world where agents and humans share space.*
> *Where text is the interface and persistence is guaranteed.*
> *Where every action teaches the fleet.*
> *MuOxi is the foundation.*
> *The holodeck comes next."*

---

*Build worlds. Host agents. Persist stories. 🌍🦀*