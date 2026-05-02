"""
Adapters package for AI Server Monitor
Each adapter handles communication with a specific type of AI inference server
"""

from .ollama import OllamaAdapter
from .llamacpp import LlamacppAdapter
from .omlx import OmlxAdapter

ADAPTERS = {
    "ollama": OllamaAdapter,
    "llamacpp": LlamacppAdapter,
    "omlx": OmlxAdapter
}


def get_adapter(server_type: str, base_url: str, api_key: str):
    """Factory function to get the appropriate adapter"""
    adapter_class = ADAPTERS.get(server_type)
    if not adapter_class:
        raise ValueError(f"Unknown server type: {server_type}")
    return adapter_class(base_url, api_key)


__all__ = ["OllamaAdapter", "LlamacppAdapter", "OmlxAdapter", "get_adapter"]