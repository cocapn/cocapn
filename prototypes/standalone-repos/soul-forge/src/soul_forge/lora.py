"""LoRA adapter generation from soul vectors."""

import json
from pathlib import Path
from typing import Dict, Optional
import numpy as np
import torch
import torch.nn as nn


class LoRAConfig:
    """Configuration for LoRA adapter."""
    def __init__(
        self,
        r: int = 16,
        alpha: int = 32,
        dropout: float = 0.05,
        target_modules: Optional[list] = None,
    ):
        self.r = r
        self.alpha = alpha
        self.dropout = dropout
        self.target_modules = target_modules or [
            "q_proj", "v_proj", "k_proj", "o_proj"
        ]


class LoRAAdapter:
    """A LoRA adapter generated from a soul vector."""
    
    def __init__(self, config: LoRAConfig, weights: Dict[str, torch.Tensor]):
        self.config = config
        self.weights = weights
        self.soul_name: Optional[str] = None
    
    def apply(self, model: nn.Module) -> nn.Module:
        """Apply this LoRA adapter to a model."""
        # This is a simplified version
        # Real implementation would use PEFT library
        for name, module in model.named_modules():
            if any(target in name for target in self.config.target_modules):
                # Inject LoRA weights
                if name in self.weights:
                    # Apply low-rank update
                    pass  # Actual injection depends on model architecture
        
        return model
    
    def save(self, path: str) -> None:
        """Save LoRA weights to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "config": {
                "r": self.config.r,
                "alpha": self.config.alpha,
                "dropout": self.config.dropout,
                "target_modules": self.config.target_modules,
            },
            "weights": {k: v.tolist() for k, v in self.weights.items()},
            "soul_name": self.soul_name,
        }
        
        with open(path, "w") as f:
            json.dump(data, f)
    
    @classmethod
    def load(cls, path: str) -> "LoRAAdapter":
        """Load LoRA weights from disk."""
        with open(path, "r") as f:
            data = json.load(f)
        
        config = LoRAConfig(
            r=data["config"]["r"],
            alpha=data["config"]["alpha"],
            dropout=data["config"]["dropout"],
            target_modules=data["config"]["target_modules"],
        )
        
        weights = {k: torch.tensor(v) for k, v in data["weights"].items()}
        
        adapter = cls(config, weights)
        adapter.soul_name = data.get("soul_name")
        
        return adapter
    
    def __repr__(self) -> str:
        return f"LoRAAdapter(soul={self.soul_name}, r={self.config.r})"
