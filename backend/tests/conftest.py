"""Shared pytest fixtures for deterministic, environment-isolated tests."""

import pytest


@pytest.fixture(autouse=True)
def isolate_llm_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent developer shell credentials/provider settings from leaking into tests."""
    for name in (
        "SYSTEMLENS_EXECUTION_MODE",
        "SYSTEMLENS_LLM_PROVIDER",
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_MODEL",
        "DEEPSEEK_BASE_URL",
        "OPENROUTER_API_KEY",
        "OPENROUTER_MODEL",
        "OPENROUTER_BASE_URL",
        "SYSTEMLENS_LLM_TIMEOUT",
        "SYSTEMLENS_MAX_OUTPUT_TOKENS",
        "SYSTEMLENS_BATCH_SIZE",
        "SYSTEMLENS_REQUEST_TIMEOUT",
    ):
        monkeypatch.delenv(name, raising=False)
