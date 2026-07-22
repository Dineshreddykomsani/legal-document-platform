from django.contrib import admin

from apps.legal.models import DocumentTemplate, DocumentVersion, LegalDocument


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "document_type", "layout_id", "theme", "is_active", "updated_at")
    list_filter = ("document_type", "theme", "is_active")
    search_fields = ("name", "description")


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "document_type", "template", "status", "created_at", "updated_at")
    list_filter = ("document_type", "status")
    search_fields = ("title", "content")


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ("legal_document", "version_number", "created_at")
    list_filter = ("created_at",)
