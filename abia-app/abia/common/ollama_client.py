"""Ollama local LLM HTTP client.

Per Architecture Contract §2.3:
Ollama (latest) for on-premise AI — no cloud dependency.

No external dependency — uses urllib (built-in).
Ollama container must be running at OLLAMA_URL.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import List, Dict, Any

logger = logging.getLogger("abia.ollama")

OLLAMA_BASE_URL = "http://ollama:11434"


class OllamaClient:
    """HTTP client for Ollama REST API."""

    DEFAULT_MODEL = "llama3.1"

    @staticmethod
    def _request(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to Ollama and parse JSON."""
        url = f"{OLLAMA_BASE_URL}{path}"
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            logger.error("Ollama HTTP %s: %s", exc.code, exc.read().decode())
            raise
        except urllib.error.URLError as exc:
            logger.error("Ollama unreachable: %s", exc.reason)
            raise

    @staticmethod
    def generate(
        prompt: str,
        model: str = "",
        system: str = "",
        stream: bool = False,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The user prompt.
            model: Model name (default: llama3.1).
            system: System instruction.
            stream: If True, yield chunks (not implemented in basic client).

        Returns:
            str: Generated response text.
        """
        payload = {
            "model": model or OllamaClient.DEFAULT_MODEL,
            "prompt": prompt,
            "stream": stream,
        }
        if system:
            payload["system"] = system

        result = OllamaClient._request("/api/generate", payload)
        return result.get("response", "")

    @staticmethod
    def embed(text: str, model: str = "") -> List[float]:
        """Generate embedding vector for text.

        Args:
            text: Input text to embed.
            model: Model name (default: llama3.1).

        Returns:
            List[float]: Embedding vector.
        """
        payload = {
            "model": model or OllamaClient.DEFAULT_MODEL,
            "prompt": text,
        }
        result = OllamaClient._request("/api/embeddings", payload)
        return result.get("embedding", [])

    @staticmethod
    def list_models() -> List[str]:
        """List locally available models."""
        url = f"{OLLAMA_BASE_URL}/api/tags"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                return [m.get("name", "") for m in data.get("models", [])]
        except urllib.error.URLError as exc:
            logger.warning("Ollama unreachable: %s", exc.reason)
            return []
