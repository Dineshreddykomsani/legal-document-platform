from __future__ import annotations

from django.conf import settings

from apps.legal.ai.base import AIProvider, AIProviderError


def get_ai_provider() -> AIProvider:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        try:
            from apps.legal.ai.gemini import GeminiProvider
        except ImportError as exc:
            raise AIProviderError("Gemini provider dependency is not installed.") from exc
        return GeminiProvider()
    raise ValueError(f"Unsupported AI_PROVIDER: {settings.AI_PROVIDER}")
