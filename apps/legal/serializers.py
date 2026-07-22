from __future__ import annotations

from rest_framework import serializers

from apps.legal.models import DocumentStatus, DocumentTemplate, DocumentVersion, LegalDocument


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = [
            "id",
            "name",
            "document_type",
            "description",
            "required_fields",
            "preview_image",
            "theme",
            "layout_id",
            "header_style",
            "footer_style",
            "color_scheme",
            "font",
        ]


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ["id", "version_number", "content", "created_at"]


class LegalDocumentListSerializer(serializers.ModelSerializer):
    version_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = LegalDocument
        fields = ["id", "title", "document_type", "status", "created_at", "updated_at", "version_count"]


class LegalDocumentDetailSerializer(serializers.ModelSerializer):
    versions = DocumentVersionSerializer(many=True, read_only=True)

    class Meta:
        model = LegalDocument
        fields = [
            "id",
            "title",
            "document_type",
            "template",
            "content",
            "branding",
            "company_logo",
            "status",
            "created_at",
            "updated_at",
            "versions",
        ]


class LegalDocumentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = ["title", "document_type", "template", "content", "branding", "company_logo", "status"]

    def validate_content(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Document content cannot be empty.")
        return value


class GenerateDocumentSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=DocumentTemplate._meta.get_field("document_type").choices)
    template_id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255)
    fields = serializers.DictField(child=serializers.CharField(allow_blank=True), allow_empty=False)
    branding = serializers.DictField(child=serializers.CharField(allow_blank=True), required=False)
    company_logo = serializers.ImageField(required=False, allow_empty_file=False)
    save = serializers.BooleanField(default=True)


class ExplainClauseSerializer(serializers.Serializer):
    clause = serializers.CharField(trim_whitespace=True)


class AnalyzeRiskSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, allow_blank=True)


class CompareDocumentsSerializer(serializers.Serializer):
    base_version_id = serializers.IntegerField()
    target_version_id = serializers.IntegerField()


class AIExplainResponseSerializer(serializers.Serializer):
    plain_english_explanation = serializers.CharField()
    purpose = serializers.CharField()
    business_impact = serializers.CharField()


class AIRiskResponseSerializer(serializers.Serializer):
    missing_clauses = serializers.ListField(child=serializers.CharField())
    potential_legal_risks = serializers.ListField(child=serializers.CharField())
    recommendations = serializers.ListField(child=serializers.CharField())
    overall_risk_level = serializers.ChoiceField(choices=["low", "medium", "high"])
