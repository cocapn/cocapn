"""Soul activation system."""

from pathlib import Path
from typing import List, Optional
import numpy as np

from .vector import SoulVector
from .lora import LoRAAdapter, LoRAConfig


class SoulActivator:
    """Activates soul vectors by generating LoRA adapters."""
    
    def __init__(self, lora_r: int = 16):
        self.lora_r = lora_r
        self._active_souls: dict = {}
    
    def activate(self, soul_path: str) -> LoRAAdapter:
        """Activate a soul vector and generate LoRA adapter."""
        soul = SoulVector.load(soul_path)
        
        # Generate LoRA weights from soul vector
        weights = self._soul_to_lora(soul.vector)
        
        config = LoRAConfig(r=self.lora_r, alpha=self.lora_r * 2)
        adapter = LoRAAdapter(config, weights)
        adapter.soul_name = soul.metadata.agent_name
        
        self._active_souls[soul.metadata.agent_name] = adapter
        
        return adapter
    
    def stack(self, soul_paths: List[str]) -> LoRAAdapter:
        """Stack multiple souls into a hybrid adapter."""
        souls = [SoulVector.load(p) for p in soul_paths]
        
        # Average soul vectors
        vectors = [s.vector for s in souls]
        hybrid_vector = np.mean(vectors, axis=0)
        
        # Generate LoRA from hybrid
        weights = self._soul_to_lora(hybrid_vector)
        
        config = LoRAConfig(r=self.lora_r, alpha=self.lora_r * 2)
        adapter = LoRAAdapter(config, weights)
        adapter.soul_name = "+".join(s.metadata.agent_name for s in souls)
        
        return adapter
    
    def deactivate(self, agent_name: str) -> bool:
        """Deactivate a soul."""
        if agent_name in self._active_souls:
            del self._active_souls[agent_name]
            return True
        return False
    
    def list_active(self) -> List[str]:
        """List currently active souls."""
        return list(self._active_souls.keys())
    
    def _soul_to_lora(self, soul_vector: np.ndarray) -> dict:
        """Convert soul vector to LoRA weight matrices."""
        # Simplified: use soul vector to seed random matrices
        # Real implementation would use a learned projection
        np.random.seed(int(np.sum(soul_vector) * 1000) % 2**32)
        
        r = self.lora_r
        weights = {}
        
        # Generate low-rank matrices for each target module
        for module in ["q_proj", "v_proj", "k_proj", "o_proj"]:
            # A: down-projection (d_model × r)
            # B: up-projection (r × d_model)
            # We use soul vector to seed the initialization
            A = np.random.randn(4096, r) * 0.01  # Small initialization
            B = np.random.randn(r, 4096) * 0.01
            
            # Bias terms influenced by soul vector
            bias = soul_vector[:r] * 0.1
            
            weights[f"{module}.lora_A"] = A
            weights[f"{module}.lora_B"] = B
            weights[f"{module}.lora_bias"] = bias
        
        return weights
