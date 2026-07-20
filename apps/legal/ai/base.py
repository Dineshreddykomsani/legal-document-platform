from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIProviderError(RuntimeError):
    pass


class AIProvider(ABC):
    @abstractmethod
    def complete_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Return a JSON object from the configured AI provider."""
