"""Soul Forge — Git-native soul vector extraction and agent embodiment."""

from .soul_forge import SoulForge
from .compressor import SoulCompressor
from .activator import SoulActivator
from .vector import SoulVector
from .lora import LoRAAdapter

__version__ = "0.1.0"
__all__ = [
    "SoulForge",
    "SoulCompressor", 
    "SoulActivator",
    "SoulVector",
    "LoRAAdapter",
]
