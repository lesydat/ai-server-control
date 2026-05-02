"""
Adapter for Ollama server
Ollama API docs: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

import logging

import httpx

from .base import BaseAdapter

logger = logging.getLogger(__name__)


class OllamaAdapter(BaseAdapter):
    """Adapter for Ollama server"""
    
    async def check_health(self, client: httpx.AsyncClient) -> dict:
        """
        Ollama doesn't have /health endpoint, use /api/tags instead
        """
        try:
            resp = await client.get(
                f"{self.base_url}/api/tags",
                headers=self.get_headers(),
                timeout=5
            )
            if resp.status_code == 200:
                return {"status": "online", "error": None}
            return {"status": "error", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}
    
    async def get_models(self, client: httpx.AsyncClient) -> list[dict]:
        """
        Get models from Ollama
        
        Logic:
        - /api/ps returns currently LOADED models (in VRAM)
        - /api/tags returns ALL available models (not necessarily loaded)
        - A model is "loaded" only if it appears in /api/ps
        - A model is "unloaded" if it appears in /api/tags but NOT in /api/ps
        - Cloud/remote models appear in /api/tags but NOT in /api/ps -> unloaded
        
        Note: Ollama doesn't expose activity status (active/idle), so activity_status is None
        """
        models = []
        
        # Get loaded models via /api/ps FIRST
        loaded_names = set()
        loaded_info = {}
        try:
            resp = await client.get(
                f"{self.base_url}/api/ps",
                headers=self.get_headers(),
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                for rm in data.get("models", []):
                    name = rm.get("name", "")
                    loaded_names.add(name)
                    loaded_info[name] = {
                        "memory": rm.get("size_vram", rm.get("size")),
                        "context_length": rm.get("context_length")
                    }
        except Exception as e:
            logger.error(f"Ollama /api/ps error: {e}")
        
        # Get ALL models from /api/tags
        try:
            resp = await client.get(
                f"{self.base_url}/api/tags",
                headers=self.get_headers(),
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get("models", []):
                    name = m.get("name", "")
                    
                    # Model is loaded only if it's in /api/ps
                    load_status = "loaded" if name in loaded_names else "unloaded"
                    
                    # Use loaded info if available
                    info = loaded_info.get(name, {})
                    
                    models.append({
                        "id": name,
                        "name": name,
                        "load_status": load_status,
                        "activity_status": None,  # Ollama doesn't expose this
                        "memory": info.get("memory") or m.get("size"),
                        "context_window": info.get("context_length") or (
                            m.get("model", {}).get("context_length")
                            if isinstance(m.get("model"), dict) else None
                        )
                    })
        except Exception as e:
            logger.error(f"Ollama /api/tags error: {e}")
        
        return models