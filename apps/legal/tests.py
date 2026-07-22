from __future__ import annotations

import tempfile
from io import BytesIO
from unittest.mock import patch

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.test import TestCase
from rest_framework.test import APIClient

from apps.legal.models import DocumentTemplate, DocumentVersion, LegalDocument
from apps.legal.seed_data import seed_default_document_templates


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
                    "party_one_address": "100 Market Street, New York, NY",
                    "party_two": "Beta LLC",
                    "party_two_address": "200 Lake Road, Boston, MA",
                    "effective_date": "2026-07-20",
                    "purpose": "evaluating a strategic software integration",
                    "term": "3 years",
                    "notice_email": "legal@example.com",
                    "governing_law": "New York",
                },
                "save": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(LegalDocument.objects.count(), 1)
        self.assertEqual(DocumentVersion.objects.count(), 1)
        self.assertIn("pdf_url", response.data)

    def test_generate_document_accepts_multipart_logo_upload(self):
        logo_buffer = BytesIO()
        Image.new("RGB", (120, 60), color="white").save(logo_buffer, format="PNG")
        logo = SimpleUploadedFile("logo.png", logo_buffer.getvalue(), content_type="image/png")
        template = DocumentTemplate.objects.get(document_type="offer_letter", layout_id="modern_corporate")

        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(
                "/api/legal/documents/generate/",
                {
                    "document_type": "offer_letter",
                    "template_id": str(template.id),
                    "title": "Asha Offer",
                    "fields": """{"candidate_name":"Asha Rao","candidate_address":"Bengaluru","company_name":"Grovyn Labs","company_address":"Hyderabad","role":"Product Counsel","department":"Legal","reporting_manager":"General Counsel","joining_date":"2026-08-01","work_location":"Hyderabad","compensation":"INR 24,00,000 annual CTC","probation_period":"6 months","notice_period":"60 days","offer_expiry_date":"2026-07-31","governing_law":"India"}""",
                    "branding": """{"company_name":"Grovyn Labs","email":"legal@grovyn.example"}""",
                    "save": "true",
                    "company_logo": logo,
                },
                format="multipart",
            )

            self.assertEqual(response.status_code, 201)
            document = LegalDocument.objects.get(title="Asha Offer")
            self.assertTrue(document.company_logo.name.startswith("company_logos/"))
            self.assertIn("Asha Rao", document.content)
            self.assertNotIn("governed by the laws", document.content.lower())
            self.assertTrue(response.data["pdf_url"])

            pdf_response = self.client.get(f"/api/legal/documents/{document.id}/download-pdf/")
            self.assertEqual(pdf_response.status_code, 200)
            self.assertEqual(pdf_response["Content-Type"], "application/pdf")

    def test_templates_endpoint_returns_default_templates(self):
        response = self.client.get("/api/legal/templates/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 55)
        self.assertIn("layout_id", response.data["results"][0])
        self.assertIn("color_scheme", response.data["results"][0])
        self.assertTrue(any(template["name"] == "Offer Letter" for template in response.data["results"]))

    def test_seed_command_only_inserts_missing_templates(self):
        original_count = DocumentTemplate.objects.count()
        nda = DocumentTemplate.objects.get(document_type="nda", layout_id="modern_corporate")
        nda.name = "Custom NDA"
        nda.save(update_fields=["name"])

        call_command("seed_legal_templates")

        nda.refresh_from_db()
        self.assertEqual(DocumentTemplate.objects.count(), original_count)
        self.assertEqual(nda.name, "Custom NDA")

    def test_seed_helper_recreates_missing_templates_idempotently(self):
        DocumentTemplate.objects.all().delete()

        created_count = seed_default_document_templates()

        self.assertEqual(created_count, 55)
        self.assertEqual(DocumentTemplate.objects.count(), 55)
        self.assertTrue(DocumentTemplate.objects.filter(document_type="nda").exists())

    def test_templates_endpoint_allows_vite_dev_origin(self):
        response = self.client.get("/api/legal/templates/", HTTP_ORIGIN="http://127.0.0.1:5173")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://127.0.0.1:5173")

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
