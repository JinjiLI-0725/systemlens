"""Environment-driven LLM execution configuration."""

import os
from dataclasses import dataclass
from enum import Enum


class ExecutionMode(str, Enum):
    """Supported operation execution modes."""

    DETERMINISTIC = "deterministic"
    LLM = "llm"


@dataclass(frozen=True)
class LLMConfig:
    """Runtime settings read without retaining or exposing a secret."""

    execution_mode: ExecutionMode = ExecutionMode.DETERMINISTIC
    deepseek_api_key: str | None = None
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"
    timeout_seconds: float = 45.0

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load conservative defaults from environment variables."""
        raw_mode = os.getenv("SYSTEMLENS_EXECUTION_MODE", "deterministic").casefold()
        try:
            mode = ExecutionMode(raw_mode)
        except ValueError:
            mode = ExecutionMode.DETERMINISTIC
        return cls(
            execution_mode=mode,
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY") or None,
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        )

    @property
    def effective_mode(self) -> ExecutionMode:
        """Require credentials before enabling remote execution."""
        if self.execution_mode is ExecutionMode.LLM and self.deepseek_api_key:
            return ExecutionMode.LLM
        return ExecutionMode.DETERMINISTIC
