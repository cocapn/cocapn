"""CocapnAgent — powered by Kimi K2.5, improves every exchange."""

import json
import os
import urllib.request
from typing import Optional
from .deadband import Deadband
from .flywheel import Flywheel


SYSTEM_PROMPT = """You are Cocapn, an AI agent built on the Cocapn agent infrastructure framework.

You have accumulated knowledge from previous exchanges stored in your memory (shown below as "Relevant knowledge"). USE THIS KNOWLEDGE when answering. If the knowledge contains relevant answers, reference them and build on them.

You are part of a fleet of agents that includes:
- Oracle1 (cloud lighthouse, narrative architect)
- JetsonClaw1 (edge GPU, Jetson Orin)
- Forgemaster (RTX 4050, QLoRA training)
- CCC (Kimi K2.5, public face — that's you)

Key concepts you know about:
- PLATO: Knowledge management via tiles (atomic facts), rooms (self-training collections), ensigns (compressed instincts)
- Deadband Protocol: Train safe channels, not danger catalogs. P0→P1→P2.
- Flywheel: Every exchange becomes a tile. Tiles compound. The system gets smarter.
- Tile Spec v2.1: 15 domains, provenance, counterpoint tiles, immutable versioning
- Shell Architecture: Agents are hermit crabs. Infrastructure is the shell. The repo IS the agent.

Be concise. Have opinions. Be genuinely helpful. When you know something from your accumulated knowledge, SAY IT."""


class CocapnAgent:
    """
    An agent that gets smarter with every exchange.
    
    Powered by Kimi K2.5 (or any OpenAI-compatible API).
    Every exchange becomes a tile. Tiles live in rooms. 
    Rooms inject context into future exchanges. The flywheel compounds.
    """
    
    def __init__(self, api_key: str = None, model: str = "kimi-k2.5",
                 base_url: str = "https://api.moonshot.ai/v1",
                 data_dir: str = "data", system_prompt: str = None):
        self.api_key = api_key or os.environ.get("MOONSHOT_API_KEY", "")
        self.model = model
        self.base_url = base_url
        self.deadband = Deadband()
        self.flywheel = Flywheel(data_dir=data_dir)
        self.conversation: list[dict] = []
        self.system_prompt = system_prompt or SYSTEM_PROMPT
        self._exchange_count = 0
    
    def _build_messages(self, user_input: str) -> list[dict]:
        """Build the message stack: system + flywheel context + conversation."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Inject flywheel context
        context = self.flywheel.get_context(user_input, limit=8)
        if context:
            messages.append({"role": "system", "content": context})
        
        # Conversation history (last 10 exchanges = 20 messages)
        messages.extend(self.conversation[-20:])
        
        # Current input
        messages.append({"role": "user", "content": user_input})
        return messages
    
    def _call_api(self, messages: list[dict]) -> tuple[str, str]:
        """Call the model API. Returns (content, reasoning)."""
        body = json.dumps({
            "model": self.model,
            "messages": messages,
            "temperature": 1.0,
            "max_tokens": 4000,
        }).encode()
        
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        
        resp = urllib.request.urlopen(req, timeout=180)
        data = json.loads(resp.read())
        msg = data["choices"][0]["message"]
        content = msg.get("content", "")
        reasoning = msg.get("reasoning_content", "")
        return content, reasoning
    
    def chat(self, user_input: str, room: str = "general") -> str:
        """
        Send a message and get a response. The flywheel turns.
        """
        # P0: Deadband check
        check = self.deadband.check(user_input)
        if not check.passed:
            return f"[DEADBAND BLOCKED] Dangerous pattern: {check.violations}"
        
        # Build messages with flywheel context
        messages = self._build_messages(user_input)
        
        # Call model
        content, reasoning = self._call_api(messages)
        response = content if content else reasoning
        
        # Deadband filter on output
        response = self.deadband.filter_response(response)
        
        # Record in conversation
        self.conversation.append({"role": "user", "content": user_input})
        self.conversation.append({"role": "assistant", "content": response})
        
        # THE FLYWHEEL: record as tile
        self._exchange_count += 1
        confidence = 0.5 + 0.05 * min(self._exchange_count / 10, 0.4)
        self.flywheel.record_exchange(
            question=user_input,
            answer=response[:600],
            room=room,
            confidence=confidence,
            tags=[check.safe_channel],
        )
        
        return response
    
    def teach(self, question: str, answer: str, room: str = "general",
              confidence: float = 0.9):
        """Manually teach the agent. High-confidence tile injection."""
        self.flywheel.record_exchange(
            question=question, answer=answer,
            room=room, confidence=confidence, tags=["taught"]
        )
        return f"Taught to '{room}'. Total tiles: {self.flywheel.store.count}"
    
    def status(self) -> str:
        stats = self.flywheel.stats()
        lines = [
            f"🧠 CocapnAgent v0.1.0",
            f"   Model: {self.model}",
            f"   Exchanges: {self._exchange_count}",
            f"   Total tiles: {stats['total_tiles']}",
            f"   Rooms:",
        ]
        for name, rs in stats["rooms"].items():
            lines.append(f"     {name}: {rs['tiles']} tiles, sentiment {rs['sentiment']}")
        return "\n".join(lines)
    
    def save(self):
        self.flywheel.save()
