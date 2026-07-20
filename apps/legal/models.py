from __future__ import annotations

from django.db import models


class DocumentType(models.TextChoices):
    NDA = "nda", "NDA"
    EMPLOYMENT_LETTER = "employment_letter", "Employment Letter"
    SERVICE_AGREEMENT = "service_agreement", "Service Agreement"
    OFFER_LETTER = "offer_letter", "Offer Letter"


class DocumentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    GENERATED = "generated", "Generated"


class DocumentTemplate(models.Model):
    name = models.CharField(max_length=160)
    document_type = models.CharField(max_length=32, choices=DocumentType.choices, unique=True)
    description = models.TextField(blank=True)
    required_fields = models.JSONField(default=list)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class LegalDocument(models.Model):
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=32, choices=DocumentType.choices)
    content = models.TextField()
    status = models.CharField(max_length=16, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        indexes = [
            models.Index(fields=["document_type", "status"]),
            models.Index(fields=["updated_at"]),
        ]

    def __str__(self) -> str:
        return self.title


class DocumentVersion(models.Model):
    legal_document = models.ForeignKey(LegalDocument, related_name="versions", on_delete=models.CASCADE)
    version_number = models.PositiveIntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version_number"]
        constraints = [
            models.UniqueConstraint(fields=["legal_document", "version_number"], name="unique_document_version_number")
        ]

    def __str__(self) -> str:
        return f"{self.legal_document.title} v{self.version_number}"
