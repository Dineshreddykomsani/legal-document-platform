from __future__ import annotations

from django.conf import settings

from apps.legal.ai.base import AIProvider
from apps.legal.ai.gemini import GeminiProvider


def get_ai_provider() -> AIProvider:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unsupported AI_PROVIDER: {settings.AI_PROVIDER}")
