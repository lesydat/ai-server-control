"""
Adapter for Ollama server
Ollama API docs: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

from typing import Optional

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
    
    async def _get_model_show(self, client: httpx.AsyncClient, model_id: str) -> Optional[dict]:
        """
        Get detailed model info from /api/show including capabilities.
        Returns dict with capabilities list (vision, tools, thinking, etc).
        """
        try:
            resp = await client.post(
                f"{self.base_url}/api/show",
                headers=self.get_headers(),
                json={"model": model_id, "verbose": False},
                timeout=15
            )
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 404:
                return None
            # Other errors - might be auth issue, return None
            return None
        except Exception as e:
            logger.error(f"Ollama /api/show error for {model_id}: {e}")
            return None

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
                    
                    # Check if cloud/remote model
                    is_cloud = bool(m.get("remote_model"))
                    
                    # Model is loaded only if it's in /api/ps
                    load_status = "loaded" if name in loaded_names else "unloaded"
                    
                    # Use loaded info if available
                    info = loaded_info.get(name, {})
                    
                    # Determine VRAM and model size
                    # VRAM from /api/ps (actual memory used) - only for loaded models
                    # model_size from /api/tags - for local models it's file size; for cloud models it's not meaningful
                    vram = info.get("memory")
                    model_size = None if is_cloud else m.get("size")
                    
                    # Get capabilities from /api/show (also works for cloud models)
                    capabilities = None
                    model_show = await self._get_model_show(client, name)
                    if model_show:
                        caps = model_show.get("capabilities", [])
                        if caps:
                            supports = []
                            cap_map = {
                                "vision": "Vision",
                                "tools": "Tools",
                                "thinking": "Thinking",
                                "completion": "Text",
                                "embedding": "Embedding",
                            }
                            for c in caps:
                                label = cap_map.get(c)
                                if label:
                                    supports.append(label)
                            if is_cloud:
                                supports.append("Cloud")
                            capabilities = supports if supports else None
                    elif is_cloud:
                        # Cloud model but couldn't get capabilities
                        capabilities = ["Cloud"]
                    
                    models.append({
                        "id": name,
                        "name": name,
                        "load_status": load_status,
                        "activity_status": None,  # Ollama doesn't expose this
                        "vram": vram,
                        "model_size": model_size,
                        "context_window": info.get("context_length") or (
                            m.get("model", {}).get("context_length")
                            if isinstance(m.get("model"), dict) else None
                        ),
                        "supports": capabilities
                    })
        except Exception as e:
            logger.error(f"Ollama /api/tags error: {e}")
        
        return models
    
    async def load_model(self, client: httpx.AsyncClient, model_id: str) -> dict:
        """
        Load a model into memory by sending an empty prompt.
        Ollama loads the model when a request is made.
        """
        try:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                headers=self.get_headers(),
                json={"model": model_id, "prompt": "", "stream": False},
                timeout=30
            )
            if resp.status_code == 200:
                return {"success": True, "error": None}
            # Try to extract error message from response
            try:
                err_data = resp.json()
                err_msg = err_data.get("error", f"HTTP {resp.status_code}")
            except:
                err_msg = f"HTTP {resp.status_code}"
            return {"success": False, "error": err_msg}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def unload_model(self, client: httpx.AsyncClient, model_id: str) -> dict:
        """
        Unload a model from memory using POST /api/generate with empty prompt + keep_alive: 0
        """
        try:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                headers=self.get_headers(),
                json={"model": model_id, "prompt": "", "stream": False, "keep_alive": 0},
                timeout=30
            )
            if resp.status_code == 200:
                return {"success": True, "error": None}
            # Try to extract error message from response
            try:
                err_data = resp.json()
                err_msg = err_data.get("error", f"HTTP {resp.status_code}")
            except:
                err_msg = f"HTTP {resp.status_code}"
            return {"success": False, "error": err_msg}
        except Exception as e:
            return {"success": False, "error": str(e)}