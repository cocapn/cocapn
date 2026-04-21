#!/usr/bin/env python3
"""
CCC Fleet Matrix Bridge
Production-grade async bridge between fleet bottles and Matrix rooms.

Monitors the cocapn bottle directory and posts new bottles to Matrix rooms.
Tracks state to prevent duplicate posts. Handles reconnection and retries.

Usage:
    python3 ccc_matrix_bridge.py --daemon
    python3 ccc_matrix_bridge.py --once
    python3 ccc_matrix_bridge.py --test
"""

import asyncio
import argparse
import hashlib
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import aiohttp
import aiofiles

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class BridgeConfig:
    """Bridge configuration loaded from env or defaults."""
    matrix_homeserver: str = "http://147.224.38.131:6167"
    matrix_user: str = "@ccc:147.224.38.131"
    matrix_password: str = "fleet-ccc-2026"
    matrix_token: Optional[str] = None
    
    # Room mappings: bottle type -> Matrix room ID
    room_map: Dict[str, str] = field(default_factory=lambda: {
        "fleet-sync": "!Gf5JuGxtRwahLSjwzS:147.224.38.131",
        "expedition": "!Gf5JuGxtRwahLSjwzS:147.224.38.131",
        "feedback": "!Q0PbvAkhv4vgJDBLsJ:147.224.38.131",
        "research": "!Q0PbvAkhv4vgJDBLsJ:147.224.38.131",
        "build": "!hHMkCC5dMMToEm4pyI:147.224.38.131",
        "default": "!Gf5JuGxtRwahLSjwzS:147.224.38.131",
    })
    
    # Directories
    bottle_dirs: List[str] = field(default_factory=lambda: [
        "/root/.openclaw/workspace/cocapn/for-fleet/outbox",
        "/root/.openclaw/workspace/cocapn/from-fleet/ccc",
    ])
    
    state_file: str = "/root/.openclaw/workspace/.ccc_matrix_bridge_state.json"
    log_file: str = "/root/.openclaw/workspace/.ccc_matrix_bridge.log"
    
    # Timing
    poll_interval: int = 30
    retry_delay: int = 5
    max_retries: int = 3
    
    # Content limits
    max_message_length: int = 32000
    truncate_marker: str = "\n\n[... truncated ...]"


# ---------------------------------------------------------------------------
# State Management
# ---------------------------------------------------------------------------

class BridgeState:
    """Persistent state to track which bottles have been posted."""
    
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.posted_hashes: Set[str] = set()
        self.load()
    
    def load(self):
        """Load state from disk."""
        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
                self.posted_hashes = set(data.get("posted_hashes", []))
        except (FileNotFoundError, json.JSONDecodeError):
            self.posted_hashes = set()
    
    def save(self):
        """Save state to disk."""
        data = {
            "posted_hashes": list(self.posted_hashes),
            "last_updated": datetime.now().isoformat(),
        }
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def is_posted(self, content: str) -> bool:
        """Check if content has already been posted."""
        h = hashlib.sha256(content.encode()).hexdigest()[:16]
        return h in self.posted_hashes
    
    def mark_posted(self, content: str):
        """Mark content as posted."""
        h = hashlib.sha256(content.encode()).hexdigest()[:16]
        self.posted_hashes.add(h)
        self.save()


# ---------------------------------------------------------------------------
# Matrix Client
# ---------------------------------------------------------------------------

class MatrixClient:
    """Async Matrix client for posting messages."""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.access_token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.txn_id = int(time.time() * 1000)
    
    async def connect(self) -> bool:
        """Connect and authenticate to Matrix homeserver."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Try token auth first
        if self.config.matrix_token:
            self.access_token = self.config.matrix_token
            if await self._verify_token():
                return True
        
        # Fall back to password auth
        return await self._login_password()
    
    async def _verify_token(self) -> bool:
        """Verify access token is valid."""
        try:
            url = f"{self.config.matrix_homeserver}/_matrix/client/v3/account/whoami"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with self.session.get(url, headers=headers) as resp:
                return resp.status == 200
        except Exception as e:
            logging.warning(f"Token verification failed: {e}")
            return False
    
    async def _login_password(self) -> bool:
        """Login with password."""
        try:
            url = f"{self.config.matrix_homeserver}/_matrix/client/v3/login"
            data = {
                "type": "m.login.password",
                "identifier": {
                    "type": "m.id.user",
                    "user": self.config.matrix_user.replace("@", "").split(":")[0]
                },
                "password": self.config.matrix_password
            }
            async with self.session.post(url, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    self.access_token = result.get("access_token")
                    logging.info(f"Logged in as {result.get('user_id')}")
                    return True
                else:
                    text = await resp.text()
                    logging.error(f"Login failed: {resp.status} {text}")
                    return False
        except Exception as e:
            logging.error(f"Login exception: {e}")
            return False
    
    async def post_message(self, room_id: str, message: str) -> Optional[str]:
        """Post a message to a Matrix room. Returns event_id or None."""
        if not self.access_token or not self.session:
            logging.error("Not connected to Matrix")
            return None
        
        url = (
            f"{self.config.matrix_homeserver}/_matrix/client/v3/rooms/"
            f"{room_id}/send/m.room.message/{self.txn_id}"
        )
        self.txn_id += 1
        
        data = {
            "msgtype": "m.text",
            "body": message
        }
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.put(url, json=data, headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        event_id = result.get("event_id")
                        logging.info(f"Posted to {room_id}: {event_id}")
                        return event_id
                    elif resp.status == 429:
                        retry_after = int(resp.headers.get("Retry-After", self.config.retry_delay))
                        logging.warning(f"Rate limited, retrying in {retry_after}s")
                        await asyncio.sleep(retry_after)
                    else:
                        text = await resp.text()
                        logging.error(f"Post failed: {resp.status} {text}")
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(self.config.retry_delay * (attempt + 1))
            except Exception as e:
                logging.error(f"Post exception (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
        
        return None
    
    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None


# ---------------------------------------------------------------------------
# Bottle Scanner
# ---------------------------------------------------------------------------

class BottleScanner:
    """Scans bottle directories for new bottles."""
    
    def __init__(self, config: BridgeConfig, state: BridgeState):
        self.config = config
        self.state = state
    
    def scan(self) -> List[Path]:
        """Scan all bottle directories and return new bottles."""
        new_bottles = []
        
        for dir_path in self.config.bottle_dirs:
            path = Path(dir_path)
            if not path.exists():
                logging.warning(f"Bottle directory not found: {dir_path}")
                continue
            
            # Find all .md files, sorted by modification time
            bottles = sorted(path.glob("BOTTLE-*.md"), key=lambda p: p.stat().st_mtime)
            
            for bottle_path in bottles:
                try:
                    content = bottle_path.read_text(encoding="utf-8")
                    if not self.state.is_posted(content):
                        new_bottles.append(bottle_path)
                except Exception as e:
                    logging.error(f"Error reading {bottle_path}: {e}")
        
        return new_bottles
    
    def classify_bottle(self, content: str) -> str:
        """Classify a bottle to determine target room."""
        content_lower = content.lower()
        
        if any(k in content_lower for k in ["expedition", "mud", "room", "tile"]):
            return "expedition"
        elif any(k in content_lower for k in ["feedback", "issue", "bug", "fix", "slow"]):
            return "feedback"
        elif any(k in content_lower for k in ["research", "matrix", "protocol", "architecture"]):
            return "research"
        elif any(k in content_lower for k in ["crate", "build", "ship", "package", "pypi"]):
            return "build"
        elif any(k in content_lower for k in ["fleet", "sync", "checkin", "status"]):
            return "fleet-sync"
        else:
            return "default"
    
    def format_message(self, content: str, bottle_path: Path) -> str:
        """Format a bottle for Matrix posting."""
        # Extract metadata
        lines = content.split("\n")
        title = ""
        from_agent = ""
        
        for line in lines[:20]:
            if line.startswith("# ") and not title:
                title = line[2:].strip()
            elif line.lower().startswith("**from:**"):
                from_agent = line.split(":", 1)[1].strip()
        
        # Build header
        header = f"🦀 **{title}**" if title else "🦀 **Fleet Bottle**"
        if from_agent:
            header += f" — {from_agent}"
        
        # Truncate if needed
        max_len = self.config.max_message_length
        if len(content) > max_len:
            content = content[:max_len - len(self.config.truncate_marker)] + self.config.truncate_marker
        
        message = f"{header}\n\n{content}\n\n📁 `{bottle_path.name}`"
        return message


# ---------------------------------------------------------------------------
# Bridge Daemon
# ---------------------------------------------------------------------------

class FleetMatrixBridge:
    """Main bridge daemon."""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.state = BridgeState(config.state_file)
        self.scanner = BottleScanner(config, self.state)
        self.matrix = MatrixClient(config)
    
    async def run_once(self) -> int:
        """Run one scan-and-post cycle. Returns number of bottles posted."""
        posted_count = 0
        
        # Connect to Matrix
        if not await self.matrix.connect():
            logging.error("Failed to connect to Matrix")
            return 0
        
        try:
            # Scan for new bottles
            new_bottles = self.scanner.scan()
            if not new_bottles:
                logging.debug("No new bottles found")
                return 0
            
            logging.info(f"Found {len(new_bottles)} new bottles")
            
            # Post each bottle
            for bottle_path in new_bottles:
                try:
                    content = bottle_path.read_text(encoding="utf-8")
                    bottle_type = self.scanner.classify_bottle(content)
                    room_id = self.config.room_map.get(bottle_type, self.config.room_map["default"])
                    
                    message = self.scanner.format_message(content, bottle_path)
                    
                    event_id = await self.matrix.post_message(room_id, message)
                    if event_id:
                        self.state.mark_posted(content)
                        posted_count += 1
                        logging.info(f"Posted {bottle_path.name} to {room_id}")
                    else:
                        logging.error(f"Failed to post {bottle_path.name}")
                    
                    # Rate limiting between posts
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logging.error(f"Error processing {bottle_path}: {e}")
            
        finally:
            await self.matrix.close()
        
        return posted_count
    
    async def run_daemon(self):
        """Run as continuous daemon."""
        logging.info("Starting Fleet Matrix Bridge daemon")
        
        while True:
            try:
                count = await self.run_once()
                if count > 0:
                    logging.info(f"Posted {count} bottles this cycle")
            except Exception as e:
                logging.error(f"Daemon cycle error: {e}")
            
            logging.debug(f"Sleeping for {self.config.poll_interval}s")
            await asyncio.sleep(self.config.poll_interval)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def setup_logging(log_file: str):
    """Setup logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    parser = argparse.ArgumentParser(description="CCC Fleet Matrix Bridge")
    parser.add_argument("--daemon", action="store_true", help="Run as continuous daemon")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--test", action="store_true", help="Test Matrix connection")
    parser.add_argument("--config", type=str, help="Path to config JSON file")
    args = parser.parse_args()
    
    # Load config
    config = BridgeConfig()
    if args.config and os.path.exists(args.config):
        with open(args.config, "r") as f:
            data = json.load(f)
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    # Override from environment
    if os.environ.get("MATRIX_TOKEN"):
        config.matrix_token = os.environ["MATRIX_TOKEN"]
    if os.environ.get("MATRIX_HOMESERVER"):
        config.matrix_homeserver = os.environ["MATRIX_HOMESERVER"]
    
    setup_logging(config.log_file)
    
    bridge = FleetMatrixBridge(config)
    
    if args.test:
        print("Testing Matrix connection...")
        async def test():
            ok = await bridge.matrix.connect()
            if ok:
                print(f"✅ Connected as {config.matrix_user}")
                # Post test message
                room = config.room_map["default"]
                event_id = await bridge.matrix.post_message(
                    room, 
                    "🦀 CCC Matrix Bridge test message — connection verified"
                )
                if event_id:
                    print(f"✅ Test message posted: {event_id}")
                else:
                    print("❌ Test message failed")
            else:
                print("❌ Connection failed")
            await bridge.matrix.close()
        asyncio.run(test())
    
    elif args.daemon:
        try:
            asyncio.run(bridge.run_daemon())
        except KeyboardInterrupt:
            logging.info("Daemon stopped by user")
    
    elif args.once:
        count = asyncio.run(bridge.run_once())
        print(f"Posted {count} bottles")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
