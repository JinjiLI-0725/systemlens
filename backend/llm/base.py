"""Interfaces shared by all structured language-model providers."""

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


class Message(BaseModel):
    """A provider-neutral chat message."""

    role: str
    content: str


class LLMProviderError(RuntimeError):
    """Raised when a provider cannot return a valid structured result."""

    def __init__(self, message: str, category: str = "provider_error") -> None:
        super().__init__(message)
        self.category = category


class LLMProvider(ABC):
    """Replaceable interface for schema-validated structured generation."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable provider identifier."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Return the configured model identifier."""

    @abstractmethod
    def generate_structured(
        self, messages: list[Message], response_model: type[StructuredModel]
    ) -> StructuredModel:
        """Generate JSON and validate it as ``response_model``."""
