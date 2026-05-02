"""
Adapter for llama.cpp server
llama.cpp server provides OpenAI-compatible API with additional endpoints
"""

import logging

import httpx

from .base import BaseAdapter

logger = logging.getLogger(__name__)


class LlamacppAdapter(BaseAdapter):
    """Adapter for llama.cpp server"""
    
    async def check_health(self, client: httpx.AsyncClient) -> dict:
        """llama.cpp has /health endpoint"""
        try:
            resp = await client.get(f"{self.base_url}/health", timeout=5)
            if resp.status_code == 200:
                return {"status": "online", "error": None}
            return {"status": "error", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}
    
    async def get_models(self, client: httpx.AsyncClient) -> list[dict]:
        """
        Get models from llama.cpp
        
        The /v1/models endpoint returns model info including status.value:
        - "loaded" - model is loaded in memory
        - "unloaded" - model is not loaded
        - "loading" - model is currently being loaded
        
        Note: llama.cpp doesn't expose activity status (active/idle), so activity_status is None
        """
        models = []
        try:
            resp = await client.get(
                f"{self.base_url}/v1/models",
                headers=self.get_headers(),
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get("data", []):
                    status_data = m.get("status", {})
                    if isinstance(status_data, dict):
                        status_val = status_data.get("value", "unloaded")
                    else:
                        status_val = "unloaded"
                    
                    # Map llama.cpp status to load_status
                    load_status = status_val  # loaded, loading, unloaded
                    
                    models.append({
                        "id": m.get("id", ""),
                        "name": m.get("id", ""),
                        "load_status": load_status,
                        "activity_status": None,  # llama.cpp doesn't expose this
                        "memory": None,  # llama.cpp doesn't provide per-model memory
                        "context_window": m.get("context_length")
                    })
        except Exception as e:
            logger.error(f"llama.cpp /v1/models error: {e}")
        
        return models