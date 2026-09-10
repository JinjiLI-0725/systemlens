"""OpenRouter adapter for its OpenAI-compatible chat completions API."""

import json
from typing import Any

import httpx
from pydantic import ValidationError

from backend.llm.base import LLMProvider, LLMProviderError, Message, StructuredModel


class OpenRouterProvider(LLMProvider):
    """Generate schema-validated JSON through OpenRouter."""

    def __init__(
        self,
        api_key: str,
        model: str = "~deepseek/deepseek-v4-flash-latest",
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: float = 45.0,
        client: httpx.Client | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = client

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def model(self) -> str:
        return self._model

    def build_request(self, messages: list[Message]) -> dict[str, Any]:
        """Build an OpenAI-compatible structured-output request body."""
        return {
            "model": self.model,
            "messages": [message.model_dump() for message in messages],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 3000,
            "stream": False,
        }

    def generate_structured(
        self, messages: list[Message], response_model: type[StructuredModel]
    ) -> StructuredModel:
        client = self._client or httpx.Client(timeout=self._timeout)
        should_close = self._client is None
        try:
            response = client.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=self.build_request(messages),
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                raise TypeError("message content is not text")
            return response_model.model_validate_json(content)
        except (
            httpx.HTTPError,
            KeyError,
            IndexError,
            TypeError,
            json.JSONDecodeError,
            ValidationError,
        ) as exc:
            raise LLMProviderError(
                "OpenRouter returned no valid structured response"
            ) from exc
        finally:
            if should_close:
                client.close()
