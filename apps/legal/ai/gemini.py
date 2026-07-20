from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from google import genai
from google.genai import types

from apps.legal.ai.base import AIProvider, AIProviderError


class GeminiProvider(AIProvider):
    def complete_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not settings.GEMINI_API_KEY:
            raise AIProviderError("GEMINI_API_KEY is not configured.")

        try:
            with genai.Client(
                api_key=settings.GEMINI_API_KEY,
                http_options=types.HttpOptions(timeout=settings.AI_REQUEST_TIMEOUT * 1000),
            ) as client:
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.2,
                        response_mime_type="application/json",
                    ),
                )
        except Exception as exc:
            raise AIProviderError("AI provider request failed.") from exc

        try:
            parsed = json.loads(response.text or "")
        except json.JSONDecodeError as exc:
            raise AIProviderError("AI provider returned an invalid response.") from exc

        if not isinstance(parsed, dict):
            raise AIProviderError("AI provider returned an invalid response.")

        return parsed
