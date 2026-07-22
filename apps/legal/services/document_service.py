from __future__ import annotations

import re
from dataclasses import dataclass

from django.db import transaction
from django.db.models import Count

from apps.legal.models import DocumentStatus, DocumentTemplate, DocumentVersion, LegalDocument


TOKEN_RE = re.compile(r"{{\s*(?P<name>[a-zA-Z0-9_]+)\s*}}")


@dataclass(frozen=True)
class GeneratedDocument:
    title: str
    document_type: str
    content: str
    document: LegalDocument | None = None


class DocumentService:
    @staticmethod
    def list_documents():
        return LegalDocument.objects.annotate(version_count=Count("versions"))

    @staticmethod
    @transaction.atomic
    def create_document(
        *,
        title: str,
        document_type: str,
        content: str,
        status: str = DocumentStatus.DRAFT,
        template: DocumentTemplate | None = None,
        branding: dict | None = None,
        company_logo=None,
    ) -> LegalDocument:
        document = LegalDocument.objects.create(
            title=title,
            document_type=document_type,
            template=template,
            content=content,
            branding=branding or {},
            company_logo=company_logo,
            status=status,
        )
        DocumentService._create_version(document)
        return document

    @staticmethod
    @transaction.atomic
    def update_document(
        document: LegalDocument,
        *,
        title: str,
        document_type: str,
        content: str,
        status: str,
        template: DocumentTemplate | None = None,
        branding: dict | None = None,
        company_logo=None,
    ) -> LegalDocument:
        content_changed = document.content != content
        document.title = title
        document.document_type = document_type
        if template is not None:
            document.template = template
        document.content = content
        if branding is not None:
            document.branding = branding
        if company_logo:
            document.company_logo = company_logo
        document.status = status
        document.save(
            update_fields=[
                "title",
                "document_type",
                "template",
                "content",
                "branding",
                "company_logo",
                "status",
                "updated_at",
            ]
        )
        if content_changed:
            DocumentService._create_version(document)
        return document

    @staticmethod
    @transaction.atomic
    def generate_document(
        *,
        document_type: str,
        title: str,
        fields: dict[str, str],
        template_id: int | None = None,
        branding: dict | None = None,
        company_logo=None,
        save: bool = True,
    ) -> GeneratedDocument:
        templates = DocumentTemplate.objects.filter(document_type=document_type, is_active=True)
        template = templates.get(id=template_id) if template_id else templates.order_by("name").first()
        if template is None:
            raise DocumentTemplate.DoesNotExist
        required_names = [field["name"] for field in template.required_fields]
        missing = [name for name in required_names if not fields.get(name)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        content = TOKEN_RE.sub(lambda match: fields.get(match.group("name"), ""), template.body)
        document = None
        if save:
            document = DocumentService.create_document(
                title=title,
                document_type=document_type,
                template=template,
                content=content,
                branding=branding or {},
                company_logo=company_logo,
                status=DocumentStatus.GENERATED,
            )
        return GeneratedDocument(title=title, document_type=document_type, content=content, document=document)

    @staticmethod
    def _create_version(document: LegalDocument) -> DocumentVersion:
        latest = (
            DocumentVersion.objects.filter(legal_document=document)
            .order_by("-version_number")
            .values_list("version_number", flat=True)
            .first()
        )
        return DocumentVersion.objects.create(
            legal_document=document,
            version_number=(latest or 0) + 1,
            content=document.content,
        )
