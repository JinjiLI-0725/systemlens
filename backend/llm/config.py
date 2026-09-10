"""Environment-driven LLM execution configuration."""

import os
from dataclasses import dataclass
from enum import Enum


class ExecutionMode(str, Enum):
    """Supported operation execution modes."""

    DETERMINISTIC = "deterministic"
    LLM = "llm"


class LLMProviderName(str, Enum):
    """Supported remote LLM providers."""

    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"


@dataclass(frozen=True)
class LLMConfig:
    """Runtime settings read without retaining or exposing a secret."""

    execution_mode: ExecutionMode = ExecutionMode.DETERMINISTIC
    provider: LLMProviderName = LLMProviderName.DEEPSEEK
    deepseek_api_key: str | None = None
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"
    openrouter_api_key: str | None = None
    openrouter_model: str = "~deepseek/deepseek-v4-flash-latest"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    timeout_seconds: float = 45.0

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load conservative defaults from environment variables."""
        raw_mode = os.getenv("SYSTEMLENS_EXECUTION_MODE", "deterministic").casefold()
        try:
            mode = ExecutionMode(raw_mode)
        except ValueError:
            mode = ExecutionMode.DETERMINISTIC
        raw_provider = os.getenv("SYSTEMLENS_LLM_PROVIDER", "deepseek").casefold()
        try:
            provider = LLMProviderName(raw_provider)
        except ValueError:
            provider = LLMProviderName.DEEPSEEK
        return cls(
            execution_mode=mode,
            provider=provider,
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY") or None,
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            deepseek_base_url=os.getenv(
                "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
            ),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY") or None,
            openrouter_model=os.getenv(
                "OPENROUTER_MODEL", "~deepseek/deepseek-v4-flash-latest"
            ),
            openrouter_base_url=os.getenv(
                "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
            ),
        )

    @property
    def api_key(self) -> str | None:
        """Return credentials for the selected provider only."""
        if self.provider is LLMProviderName.OPENROUTER:
            return self.openrouter_api_key
        return self.deepseek_api_key

    @property
    def effective_mode(self) -> ExecutionMode:
        """Require credentials before enabling remote execution."""
        if self.execution_mode is ExecutionMode.LLM and self.api_key:
            return ExecutionMode.LLM
        return ExecutionMode.DETERMINISTIC
