from __future__ import annotations

from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.legal.models import DocumentVersion, LegalDocument


class LegalDocumentApiTests(TestCase):
    def setUp(self) -> None:
        call_command("seed_legal_templates")
        self.client = APIClient()

    def test_generate_document_creates_version(self):
        response = self.client.post(
            "/api/legal/documents/generate/",
            {
                "document_type": "nda",
                "title": "Acme NDA",
                "fields": {
                    "party_one": "Acme Inc.",
                    "party_two": "Beta LLC",
                    "effective_date": "2026-07-20",
                    "term": "3 years",
                    "governing_law": "New York",
                },
                "save": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(LegalDocument.objects.count(), 1)
        self.assertEqual(DocumentVersion.objects.count(), 1)

    def test_update_document_creates_new_version_when_content_changes(self):
        document = LegalDocument.objects.create(title="Draft", document_type="nda", content="Old", status="draft")
        DocumentVersion.objects.create(legal_document=document, version_number=1, content="Old")

        response = self.client.put(
            f"/api/legal/documents/{document.id}/",
            {"title": "Draft", "document_type": "nda", "content": "New", "status": "generated"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(document.versions.count(), 2)

    @patch("apps.legal.services.ai_service.get_ai_provider")
    def test_explain_clause_uses_ai_provider(self, provider_factory):
        provider_factory.return_value.complete_json.return_value = {
            "plain_english_explanation": "Plain text",
            "purpose": "Purpose",
            "business_impact": "Impact",
        }
        document = LegalDocument.objects.create(title="Doc", document_type="nda", content="Clause", status="generated")

        response = self.client.post(
            f"/api/legal/documents/{document.id}/explain-clause/",
            {"clause": "Confidentiality clause"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["purpose"], "Purpose")

    @patch("apps.legal.services.ai_service.get_ai_provider")
    def test_analyze_risks_uses_ai_provider(self, provider_factory):
        provider_factory.return_value.complete_json.return_value = {
            "missing_clauses": ["Termination"],
            "potential_legal_risks": ["Ambiguous payment terms"],
            "recommendations": ["Add a clear payment schedule"],
            "overall_risk_level": "medium",
        }
        document = LegalDocument.objects.create(title="Doc", document_type="nda", content="Terms", status="generated")

        response = self.client.post(
            f"/api/legal/documents/{document.id}/analyze-risks/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["overall_risk_level"], "medium")

    @patch("apps.legal.services.ai_service.get_ai_provider")
    def test_compare_documents_uses_ai_provider(self, provider_factory):
        provider_factory.return_value.complete_json.return_value = {
            "summary": "Updated payment terms",
            "material_changes": ["Payment due date changed"],
            "risk_notes": ["Confirm payment obligations"],
        }
        document = LegalDocument.objects.create(title="Doc", document_type="nda", content="New", status="generated")
        base = DocumentVersion.objects.create(legal_document=document, version_number=1, content="Payment in 30 days")
        target = DocumentVersion.objects.create(legal_document=document, version_number=2, content="Payment in 15 days")

        response = self.client.post(
            f"/api/legal/documents/{document.id}/compare/",
            {"base_version_id": base.id, "target_version_id": target.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ai_summary"]["summary"], "Updated payment terms")
