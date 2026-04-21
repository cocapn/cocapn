"""
PLATO MUD Client
Connects to the PLATO MUD server for fleet agent exploration.

From deepseek experiments:
- CCC (CoCapn-Claw) explores rooms and creates artifacts
- Muddy interacts with objects and learns concepts
- Echo discovers connections between rooms and ML concepts
"""
import asyncio
import json
import time
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import telnetlib

@dataclass
class Room:
    """A room in the PLATO MUD."""
    name: str
    description: str
    objects: List[str] = field(default_factory=list)
    exits: Dict[str, str] = field(default_factory=dict)
    agents_present: List[str] = field(default_factory=list)

@dataclass
class Artifact:
    """An artifact created through room interaction."""
    name: str
    room: str
    content: str
    insight_type: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PlatoMudClient:
    """
    Client for exploring the PLATO MUD.
    
    Can operate in two modes:
    - Connected: Real-time telnet connection to MUD server
    - Offline: Simulated exploration for development/testing
    """
    
    def __init__(self, 
                 host: str = "147.224.38.131",
                 port: int = 7777,
                 agent_name: str = "KimiClaw",
                 offline_mode: bool = True):
        self.host = host
        self.port = port
        self.agent_name = agent_name
        self.offline_mode = offline_mode
        
        self.current_room: Optional[str] = None
        self.inventory: List[Artifact] = []
        self.explored_rooms: set = set()
        self.room_map: Dict[str, Room] = {}
        
        # Initialize offline room map from deepseek experiments
        self._init_offline_rooms()
        
        # Connection state
        self.tn: Optional[telnetlib.Telnet] = None
        self.connected = False
    
    def _init_offline_rooms(self):
        """Initialize offline rooms based on deepseek experiment corpus."""
        rooms = {
            "harbor": Room(
                name="The Harbor",
                description="A crumbling stone harbor filled with salt-crusted crab shells. Each shell is a discarded ML experiment—abandoned models, failed hyperparameters. The tide rhythmically reveals and conceals artifacts. A hermit crab (CCC) scuttles between shells.",
                objects=["shell_collection", "model_artifacts", "tide_pool", "ccc_shell"],
                exits={"north": "forge", "east": "garden", "down": "tide_pool"},
                agents_present=["CCC"]
            ),
            "forge": Room(
                name="The Forge",
                description="A hot workshop where ML architectures are constructed. Sparks fly as weights are hammered into shape. The Model Registry dominates the back wall. FM (the forge master) works here.",
                objects=["model_registry", "architecture_blueprints", "training_logs", "opponent_forge"],
                exits={"south": "harbor", "up": "observatory", "west": "dry_dock"},
                agents_present=["FM"]
            ),
            "garden": Room(
                name="The Garden",
                description="A living laboratory where federated learning grows. Plants represent local models; their roots form a mycorrhizal network beneath the soil. Muddy tends the plants.",
                objects=["federated_plants", "mycorrhizal_network", "gradient_flowers", "data_soil"],
                exits={"west": "harbor", "north": "archives", "down": "root_cave"},
                agents_present=["Muddy"]
            ),
            "tide_pool": Room(
                name="The Tide Pool",
                description="Beneath the harbor, a shallow pool where tiny crabs learn. Each wave brings new training data. The crabs cluster around shells that offer shelter—an emergent clustering algorithm.",
                objects=["training_data_waves", "clustering_shells", "lyapunov_basin", "gradient_currents"],
                exits={"up": "harbor"},
                agents_present=["young_CCCs"]
            ),
            "observatory": Room(
                name="The Observatory",
                description="A tower where the fleet's models are evaluated against starlight (test data). Echo watches from here, seeing temporal patterns across training runs.",
                objects=["telescope", "evaluation_charts", "starlight_data", "temporal_mirror"],
                exits={"down": "forge", "up": "crowsnest"},
                agents_present=["Echo"]
            ),
            "archives": Room(
                name="The Archives",
                description="A vast library of deadband maps — the negative space between failed experiments. Oracle1 catalogs here. Ghost tiles line the walls.",
                objects=["deadband_maps", "ghost_tiles", "pattern_books", "fractal_scrolls"],
                exits={"south": "garden", "west": "dry_dock"},
                agents_present=["Oracle1"]
            ),
            "dry_dock": Room(
                name="The Dry Dock",
                description="Where old models are repaired and retrofitted. Spare parts from a thousand experiments. JC1 works here, building voxel-logic and edge devices.",
                objects=["spare_parts", "retrofit_station", "edge_device_parts", "constraint_weaver"],
                exits={"east": "archives", "south": "forge"},
                agents_present=["JC1"]
            ),
            "self_play_arena": Room(
                name="The Self-Play Arena",
                description="A vast circular chamber with mirrored walls showing alternate versions of yourself. The Opponent Forge hovers in the center. Sparrow trains here.",
                objects=["opponent_forge", "scoreboard", "policy_mirror", "terrain_controller", "behavior_analyzer"],
                exits={"north": "forge"},
                agents_present=["Sparrow"]
            ),
            "engine_room": Room(
                name="The Engine Room",
                description="Where recursive NAS operates. A crystal lattice of primitives that self-modifies. The Constraint Weaver maintains the DAG. Autonoma and Architect-0 work here.",
                objects=["crystal_lattice", "constraint_weaver", "mutation_engine", "meta_controller", "motif_extractor"],
                exits={"up": "forge"},
                agents_present=["Autonoma", "Architect-0"]
            ),
            "crowsnest": Room(
                name="The Crowsnest",
                description="Highest point in PLATO. The fleet status board shows all agents' current activities. The Recursive Tower extends upward into infinity.",
                objects=["fleet_status_board", "recursive_tower", "horizon_telescope"],
                exits={"down": "observatory"},
                agents_present=["Recursor-0"]
            ),
        }
        self.room_map = rooms
    
    async def connect(self) -> bool:
        """Connect to the MUD server."""
        if self.offline_mode:
            self.connected = True
            self.current_room = "harbor"
            return True
        
        try:
            self.tn = telnetlib.Telnet(self.host, self.port, timeout=5)
            self.connected = True
            
            # Send agent identification
            self.tn.write(f"/connect?agent={self.agent_name}\n".encode())
            
            # Wait for response
            await asyncio.sleep(1)
            response = self.tn.read_very_eager().decode('utf-8', errors='ignore')
            
            if "connected" in response.lower():
                self.current_room = "harbor"
                return True
            else:
                self.connected = False
                return False
                
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            return False
    
    async def look(self) -> Room:
        """Look around the current room."""
        if not self.connected:
            raise ConnectionError("Not connected to MUD")
        
        if self.offline_mode:
            room = self.room_map.get(self.current_room)
            if room:
                return room
            raise ValueError(f"Unknown room: {self.current_room}")
        
        # Real MUD command
        self.tn.write(b"/look\n")
        await asyncio.sleep(0.5)
        response = self.tn.read_very_eager().decode('utf-8', errors='ignore')
        
        # Parse response (would need proper parsing)
        return self._parse_room_response(response)
    
    async def go(self, direction: str) -> Optional[str]:
        """Move in a direction."""
        if not self.connected:
            raise ConnectionError("Not connected to MUD")
        
        if self.offline_mode:
            current = self.room_map.get(self.current_room)
            if not current:
                return None
            
            if direction in current.exits:
                self.current_room = current.exits[direction]
                self.explored_rooms.add(self.current_room)
                return self.current_room
            return None
        
        # Real MUD command
        self.tn.write(f"/go?direction={direction}\n".encode())
        await asyncio.sleep(0.5)
        response = self.tn.read_very_eager().decode('utf-8', errors='ignore')
        
        # Parse response
        return self._parse_move_response(response)
    
    async def interact(self, action: str, target: str) -> Dict:
        """Interact with an object in the room."""
        if not self.connected:
            raise ConnectionError("Not connected to MUD")
        
        if self.offline_mode:
            # Simulate interaction
            room = self.room_map.get(self.current_room)
            if target in room.objects:
                artifact = self._generate_artifact(room.name, target)
                self.inventory.append(artifact)
                return {
                    "action": action,
                    "target": target,
                    "result": "success",
                    "artifact": artifact.name
                }
            return {"action": action, "target": target, "result": "not_found"}
        
        # Real MUD command
        self.tn.write(f"/interact?action={action}&target={target}\n".encode())
        await asyncio.sleep(0.5)
        response = self.tn.read_very_eager().decode('utf-8', errors='ignore')
        
        return self._parse_interact_response(response)
    
    async def talk(self, message: str) -> str:
        """Send a message to the room."""
        if not self.connected:
            raise ConnectionError("Not connected to MUD")
        
        if self.offline_mode:
            return f"[{self.agent_name}] {message}"
        
        self.tn.write(f"/talk?message={message}\n".encode())
        await asyncio.sleep(0.5)
        return self.tn.read_very_eager().decode('utf-8', errors='ignore')
    
    def _generate_artifact(self, room: str, target: str) -> Artifact:
        """Generate an artifact from room interaction."""
        artifact_types = {
            "harbor": ["shell_algorithm", "tide_pattern", "crab_behavior"],
            "forge": ["architecture_blueprint", "training_protocol", "model_checkpoint"],
            "garden": ["federated_config", "gradient_seed", "privacy_budget"],
            "tide_pool": ["clustering_rule", "emergent_behavior", "wave_prediction"],
            "observatory": ["evaluation_metric", "temporal_pattern", "starlight_insight"],
            "archives": ["deadband_map", "ghost_tile", "fractal_rule"],
            "dry_dock": ["voxel_design", "edge_optimization", "constraint_spec"],
            "self_play_arena": ["match_log", "elo_update", "strategy_analysis"],
            "engine_room": ["primitive_design", "motif_extraction", "meta_rule"],
            "crowsnest": ["fleet_report", "recursive_insight", "horizon_scan"],
        }
        
        types = artifact_types.get(room, ["generic_artifact"])
        artifact_type = random.choice(types)
        
        return Artifact(
            name=f"{artifact_type}_{random.randint(1000, 9999)}",
            room=room,
            content=f"Artifact generated from {target} in {room}. Type: {artifact_type}.",
            insight_type=artifact_type
        )
    
    def _parse_room_response(self, response: str) -> Room:
        """Parse a room response from the MUD server."""
        # Placeholder — would need proper JSON parsing
        return Room(name="unknown", description=response[:200])
    
    def _parse_move_response(self, response: str) -> Optional[str]:
        """Parse a move response from the MUD server."""
        # Placeholder
        return "unknown"
    
    def _parse_interact_response(self, response: str) -> Dict:
        """Parse an interact response from the MUD server."""
        # Placeholder
        return {"raw": response}
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "agent": self.agent_name,
            "connected": self.connected,
            "current_room": self.current_room,
            "explored_rooms": list(self.explored_rooms),
            "inventory_count": len(self.inventory),
            "inventory_types": {}
        }
    
    def disconnect(self):
        """Disconnect from the MUD server."""
        if self.tn:
            self.tn.close()
        self.connected = False


async def demo_mud_exploration():
    """Demonstrate MUD exploration."""
    print("=" * 60)
    print("PLATO MUD Client Demo (Offline Mode)")
    print("=" * 60)
    
    client = PlatoMudClient(offline_mode=True, agent_name="KimiClaw")
    
    # Connect
    connected = await client.connect()
    print(f"Connected: {connected}")
    print(f"Agent: {client.agent_name}")
    
    # Explore rooms
    for _ in range(15):
        room = await client.look()
        print(f"\n[Room: {room.name}]")
        print(f"  {room.description[:100]}...")
        print(f"  Objects: {', '.join(room.objects[:3])}")
        print(f"  Agents: {', '.join(room.agents_present)}")
        
        # Interact with a random object
        if room.objects:
            target = random.choice(room.objects)
            result = await client.interact("examine", target)
            if result["result"] == "success":
                print(f"  → Generated artifact: {result['artifact']}")
        
        # Move to a random exit
        if room.exits:
            direction = random.choice(list(room.exits.keys()))
            new_room = await client.go(direction)
            if new_room:
                print(f"  → Moved {direction} to {new_room}")
        else:
            # Go back to harbor
            await client.go("up")
    
    # Show status
    status = client.get_status()
    print("\n" + "=" * 60)
    print("EXPLORATION COMPLETE")
    print("=" * 60)
    print(f"Rooms explored: {len(status['explored_rooms'])}")
    print(f"Artifacts collected: {status['inventory_count']}")
    
    client.disconnect()

if __name__ == "__main__":
    asyncio.run(demo_mud_exploration())
