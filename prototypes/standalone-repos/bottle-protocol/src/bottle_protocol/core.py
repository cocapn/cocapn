"""Git-native messaging between fleet agents."""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import hashlib


@dataclass
class Bottle:
    """A message between fleet agents."""
    sender: str
    recipient: str
    subject: str
    body: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    message_id: str = field(default_factory=lambda: hashlib.sha256(datetime.utcnow().isoformat().encode()).hexdigest()[:16])
    priority: str = "normal"  # urgent, normal, low
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp,
            "priority": self.priority,
            "tags": self.tags,
        }
    
    def to_markdown(self) -> str:
        return f"""# [FLEET:BOTTLE] {self.subject}

**From:** {self.sender}  
**To:** {self.recipient}  
**ID:** {self.message_id}  
**Date:** {self.timestamp}

---

{self.body}
"""


class FleetPostOffice:
    """Manages bottle routing."""
    def __init__(self, base_path: str = "."):
        self.base = Path(base_path)
        self.outbox = self.base / "for-fleet" / "outbox"
        self.inbox = self.base / "from-fleet" / "inbox"
        self._ensure_dirs()
        
    def _ensure_dirs(self) -> None:
        self.outbox.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
    def send(self, bottle: Bottle) -> Path:
        path = self.outbox / f"BOTTLE-{bottle.sender}-{bottle.message_id}.md"
        path.write_text(bottle.to_markdown())
        return path
        
    def receive(self) -> List[Bottle]:
        bottles = []
        for path in self.inbox.glob("BOTTLE-*.md"):
            # Parse markdown back to bottle
            content = path.read_text()
            bottles.append(self._parse(content))
        return bottles
    
    def _parse(self, content: str) -> Bottle:
        lines = content.split('\n')
        # Simple parsing - in production use proper markdown parser
        return Bottle(
            sender="unknown",
            recipient="unknown", 
            subject="Parsed bottle",
            body=content,
        )
