from __future__ import annotations

import difflib
from typing import Any

from apps.legal.ai.factory import get_ai_provider
from apps.legal.models import DocumentVersion


LEGAL_SYSTEM_PROMPT = (
    "You are a legal document assistant. Provide practical business-oriented analysis. "
    "Return strict JSON only. Do not provide legal advice disclaimers unless asked."
)


class LegalAIService:
    def __init__(self) -> None:
        self.provider = get_ai_provider()

    def explain_clause(self, clause: str) -> dict[str, Any]:
        return self.provider.complete_json(
            system_prompt=LEGAL_SYSTEM_PROMPT,
            user_prompt=(
                "Explain this clause as JSON with keys plain_english_explanation, purpose, "
                f"business_impact:\n\n{clause}"
            ),
        )

    def analyze_risks(self, content: str) -> dict[str, Any]:
        return self.provider.complete_json(
            system_prompt=LEGAL_SYSTEM_PROMPT,
            user_prompt=(
                "Analyze this legal document as JSON with keys missing_clauses, potential_legal_risks, "
                "recommendations, overall_risk_level where overall_risk_level is low, medium, or high:\n\n"
                f"{content}"
            ),
        )

    def compare_versions(self, base: DocumentVersion, target: DocumentVersion) -> dict[str, Any]:
        diff = list(
            difflib.unified_diff(
                base.content.splitlines(),
                target.content.splitlines(),
                fromfile=f"version-{base.version_number}",
                tofile=f"version-{target.version_number}",
                lineterm="",
            )
        )
        ai_summary = self.provider.complete_json(
            system_prompt=LEGAL_SYSTEM_PROMPT,
            user_prompt=(
                "Summarize this document diff as JSON with keys summary, material_changes, risk_notes:\n\n"
                + "\n".join(diff[:400])
            ),
        )
        return {
            "base_version": base.version_number,
            "target_version": target.version_number,
            "added_content": [line[1:] for line in diff if line.startswith("+") and not line.startswith("+++")],
            "removed_content": [line[1:] for line in diff if line.startswith("-") and not line.startswith("---")],
            "modified_content": diff,
            "ai_summary": ai_summary,
        }
