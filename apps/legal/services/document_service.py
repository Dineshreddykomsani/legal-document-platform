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
    def create_document(*, title: str, document_type: str, content: str, status: str = DocumentStatus.DRAFT) -> LegalDocument:
        document = LegalDocument.objects.create(
            title=title,
            document_type=document_type,
            content=content,
            status=status,
        )
        DocumentService._create_version(document)
        return document

    @staticmethod
    @transaction.atomic
    def update_document(document: LegalDocument, *, title: str, document_type: str, content: str, status: str) -> LegalDocument:
        content_changed = document.content != content
        document.title = title
        document.document_type = document_type
        document.content = content
        document.status = status
        document.save(update_fields=["title", "document_type", "content", "status", "updated_at"])
        if content_changed:
            DocumentService._create_version(document)
        return document

    @staticmethod
    @transaction.atomic
    def generate_document(*, document_type: str, title: str, fields: dict[str, str], save: bool = True) -> GeneratedDocument:
        template = DocumentTemplate.objects.get(document_type=document_type, is_active=True)
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
                content=content,
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
