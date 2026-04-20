"""Beacon Protocol — Structured broadcast for fleet-wide signaling."""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json


@dataclass
class Beacon:
    """A structured broadcast message in the fleet."""
    signal_type: str  # "alert", "status", "discovery", "command", "heartbeat"
    source: str  # Agent or system that emitted the beacon
    payload: Dict[str, Any]  # Signal-specific data
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ttl: int = 300  # Time-to-live in seconds
    priority: int = 5  # 1=critical, 10=low
    channel: str = "general"  # Routing channel
    
    @property
    def id(self) -> str:
        """Unique beacon identifier."""
        data = f"{self.source}:{self.signal_type}:{self.timestamp}:{self.payload}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
        
    def to_json(self) -> str:
        """Serialize to JSON for transmission."""
        return json.dumps({
            "id": self.id,
            "signal_type": self.signal_type,
            "source": self.source,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "priority": self.priority,
            "channel": self.channel,
        })
        
    @classmethod
    def from_json(cls, data: str) -> "Beacon":
        """Deserialize from JSON."""
        d = json.loads(data)
        return cls(
            signal_type=d["signal_type"],
            source=d["source"],
            payload=d["payload"],
            timestamp=d["timestamp"],
            ttl=d["ttl"],
            priority=d["priority"],
            channel=d["channel"],
        )


@dataclass 
class BeaconReceipt:
    """Acknowledgment that a beacon was received and processed."""
    beacon_id: str
    recipient: str
    status: str  # "received", "processed", "failed", "expired"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    notes: str = ""


class BeaconProtocol:
    """Fleet-wide structured broadcast system.
    
    Unlike bottles (async, persistent, Git-based), beacons are:
    - Real-time: delivered immediately
    - Ephemeral: expire after TTL
    - Structured: typed signals with schemas
    - Routed: channel-based filtering
    
    Use cases:
    - Heartbeats: "I'm alive" every 60s
    - Alerts: "Fleet health critical"
    - Discovery: "New room mapped"
    - Commands: "All agents: report status"
    """
    
    def __init__(self):
        self.beacons: List[Beacon] = []
        self.receipts: Dict[str, List[BeaconReceipt]] = {}
        self.subscribers: Dict[str, List[Callable[[Beacon], None]]] = {}
        self.channels: Dict[str, List[str]] = {}  # channel → subscriber names
        
    def emit(self, beacon: Beacon) -> str:
        """Emit a beacon to the fleet.
        
        Returns the beacon ID.
        """
        self.beacons.append(beacon)
        
        # Route to channel subscribers
        if beacon.channel in self.channels:
            for subscriber_name in self.channels[beacon.channel]:
                if subscriber_name in self.subscribers:
                    for callback in self.subscribers[subscriber_name]:
                        try:
                            callback(beacon)
                        except Exception as e:
                            # Log but don't crash the broadcast
                            pass
                            
        return beacon.id
        
    def subscribe(self, name: str, channels: List[str], callback: Callable[[Beacon], None]) -> None:
        """Subscribe to beacon channels.
        
        name: Unique subscriber identifier
        channels: List of channels to listen on
        callback: Function called when beacon arrives
        """
        self.subscribers[name] = [callback]
        for channel in channels:
            if channel not in self.channels:
                self.channels[channel] = []
            if name not in self.channels[channel]:
                self.channels[channel].append(name)
                
    def acknowledge(self, beacon_id: str, recipient: str, status: str = "received", notes: str = "") -> None:
        """Record a receipt for a beacon."""
        receipt = BeaconReceipt(
            beacon_id=beacon_id,
            recipient=recipient,
            status=status,
            notes=notes,
        )
        if beacon_id not in self.receipts:
            self.receipts[beacon_id] = []
        self.receipts[beacon_id].append(receipt)
        
    def query(self, signal_type: Optional[str] = None, source: Optional[str] = None, 
              channel: Optional[str] = None, since: Optional[str] = None) -> List[Beacon]:
        """Query beacons by filters."""
        results = self.beacons
        
        if signal_type:
            results = [b for b in results if b.signal_type == signal_type]
        if source:
            results = [b for b in results if b.source == source]
        if channel:
            results = [b for b in results if b.channel == channel]
        if since:
            results = [b for b in results if b.timestamp >= since]
            
        return results
        
    def get_receipts(self, beacon_id: str) -> List[BeaconReceipt]:
        """Get all receipts for a beacon."""
        return self.receipts.get(beacon_id, [])
        
    def cleanup_expired(self) -> int:
        """Remove expired beacons. Returns count removed."""
        now = datetime.now(timezone.utc)
        valid = []
        removed = 0
        
        for beacon in self.beacons:
            beacon_time = datetime.fromisoformat(beacon.timestamp.replace("Z", "+00:00"))
            age = (now - beacon_time).total_seconds()
            
            if age < beacon.ttl:
                valid.append(beacon)
            else:
                removed += 1
                
        self.beacons = valid
        return removed
        
    def get_stats(self) -> Dict[str, Any]:
        """Protocol statistics."""
        return {
            "total_beacons": len(self.beacons),
            "subscribers": len(self.subscribers),
            "channels": list(self.channels.keys()),
            "receipts_total": sum(len(r) for r in self.receipts.values()),
            "signal_types": list(set(b.signal_type for b in self.beacons)),
        }
        
    def heartbeat(self, source: str, metadata: Dict[str, Any]) -> str:
        """Convenience: emit a heartbeat beacon."""
        beacon = Beacon(
            signal_type="heartbeat",
            source=source,
            payload=metadata,
            ttl=60,
            priority=10,
            channel="health",
        )
        return self.emit(beacon)
        
    def alert(self, source: str, message: str, priority: int = 1) -> str:
        """Convenience: emit an alert beacon."""
        beacon = Beacon(
            signal_type="alert",
            source=source,
            payload={"message": message},
            ttl=3600,
            priority=priority,
            channel="alerts",
        )
        return self.emit(beacon)
