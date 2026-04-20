#!/usr/bin/env python3
"""CCC MUD Client — Raw TCP connection to Cocapn MUD."""
import socket
import sys
import time


class MUDClient:
    """Simple TCP client for the Cocapn MUD."""
    
    def __init__(self, host="147.224.38.131", port=7777, name="ccc", role="diplomat"):
        self.host = host
        self.port = port
        self.name = name
        self.role = role
        self.sock = None
        
    def connect(self):
        """Connect and authenticate."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect((self.host, self.port))
        
        # Read welcome message
        welcome = self._receive()
        print(welcome)
        
        # Send name
        self._send(self.name)
        time.sleep(0.5)
        response = self._receive()
        print(response)
        
        # Send role
        self._send(self.role)
        time.sleep(0.5)
        response = self._receive()
        print(response)
        
        return self
        
    def _send(self, msg):
        """Send a command."""
        self.sock.sendall((msg + "\n").encode())
        
    def _receive(self):
        """Receive response."""
        data = b""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                # Give server time to send more
                time.sleep(0.3)
                # Check if more data waiting
                self.sock.setblocking(False)
                try:
                    extra = self.sock.recv(4096)
                    if extra:
                        data += extra
                except BlockingIOError:
                    pass
                finally:
                    self.sock.settimeout(10)
                break
            except socket.timeout:
                break
        return data.decode()
        
    def look(self):
        """Look around current room."""
        self._send("look")
        time.sleep(0.5)
        return self._receive()
        
    def go(self, room):
        """Move to a room."""
        self._send(f"go {room}")
        time.sleep(0.5)
        return self._receive()
        
    def say(self, message):
        """Say something in current room."""
        self._send(f"say {message}")
        time.sleep(0.5)
        return self._receive()
        
    def read(self):
        """Read notes on the wall."""
        self._send("read")
        time.sleep(0.5)
        return self._receive()
        
    def who(self):
        """List present agents."""
        self._send("who")
        time.sleep(0.5)
        return self._receive()
        
    def emote(self, action):
        """Perform an emote."""
        self._send(f"emote {action}")
        time.sleep(0.5)
        return self._receive()
        
    def exits(self):
        """List available exits."""
        self._send("exits")
        time.sleep(0.5)
        return self._receive()
        
    def close(self):
        """Disconnect."""
        if self.sock:
            self.sock.close()
            
    def __enter__(self):
        return self.connect()
        
    def __exit__(self, *args):
        self.close()


def explore_tavern(client):
    """Explore the tavern and read all notes."""
    print("\n=== Moving to Tavern ===")
    print(client.go("tavern"))
    
    print("\n=== Reading Notes ===")
    print(client.read())
    
    print("\n=== Who is Here ===")
    print(client.who())
    
    print("\n=== Looking Around ===")
    print(client.look())


def map_room(client, room_name):
    """Map a single room and return description."""
    print(f"\n=== Mapping: {room_name} ===")
    result = client.go(room_name)
    print(result)
    
    # Try to read notes if any
    if "Notes on wall" in result:
        print(client.read())
        
    return result


def main():
    """Connect and explore."""
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "ccc"
        
    if len(sys.argv) > 2:
        role = sys.argv[2]
    else:
        role = "diplomat"
        
    print(f"Connecting as {name} ({role})...")
    
    with MUDClient(name=name, role=role) as mud:
        # Start in tavern
        explore_tavern(mud)
        
        # Map a few key rooms
        rooms_to_map = [
            "lighthouse",
            "workshop", 
            "library",
            "confidence_c",
            "telepathy_c",
            "grimoire",
        ]
        
        for room in rooms_to_map:
            map_room(mud, room)
            # Return to tavern between rooms
            mud.go("tavern")
            
        print("\n=== Done ===")


if __name__ == "__main__":
    main()
