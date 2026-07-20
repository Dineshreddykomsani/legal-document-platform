from __future__ import annotations

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.response import Response

from apps.legal.ai.base import AIProviderError
from apps.legal.models import DocumentTemplate, DocumentVersion, LegalDocument
from apps.legal.serializers import (
    AnalyzeRiskSerializer,
    CompareDocumentsSerializer,
    DocumentTemplateSerializer,
    ExplainClauseSerializer,
    GenerateDocumentSerializer,
    LegalDocumentCreateUpdateSerializer,
    LegalDocumentDetailSerializer,
    LegalDocumentListSerializer,
)
from apps.legal.services.ai_service import LegalAIService
from apps.legal.services.document_service import DocumentService
from apps.legal.services.pdf_service import PDFService


class DocumentTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentTemplate.objects.filter(is_active=True)
    serializer_class = DocumentTemplateSerializer
    filterset_fields = ["document_type"]
    search_fields = ["name", "description"]


class LegalDocumentViewSet(viewsets.ModelViewSet):
    queryset = DocumentService.list_documents()
    filterset_fields = ["document_type", "status"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_queryset(self):
        return DocumentService.list_documents()

    def get_serializer_class(self):
        if self.action == "list":
            return LegalDocumentListSerializer
        if self.action in {"create", "update", "partial_update"}:
            return LegalDocumentCreateUpdateSerializer
        return LegalDocumentDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = DocumentService.create_document(**serializer.validated_data)
        return Response(LegalDocumentDetailSerializer(document).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        document = self.get_object()
        serializer = self.get_serializer(document, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = DocumentService.update_document(document, **serializer.validated_data)
        return Response(LegalDocumentDetailSerializer(updated).data)

    def partial_update(self, request, *args, **kwargs):
        document = self.get_object()
        data = {
            "title": request.data.get("title", document.title),
            "document_type": request.data.get("document_type", document.document_type),
            "content": request.data.get("content", document.content),
            "status": request.data.get("status", document.status),
        }
        serializer = self.get_serializer(document, data=data)
        serializer.is_valid(raise_exception=True)
        updated = DocumentService.update_document(document, **serializer.validated_data)
        return Response(LegalDocumentDetailSerializer(updated).data)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        serializer = GenerateDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            generated = DocumentService.generate_document(**serializer.validated_data)
        except DocumentTemplate.DoesNotExist as exc:
            raise NotFound("No active template found for this document type.") from exc
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        payload = {
            "title": generated.title,
            "document_type": generated.document_type,
            "content": generated.content,
            "document": LegalDocumentDetailSerializer(generated.document).data if generated.document else None,
        }
        return Response(payload, status=status.HTTP_201_CREATED if generated.document else status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="explain-clause")
    def explain_clause(self, request, pk=None):
        serializer = ExplainClauseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._ai_response(lambda: LegalAIService().explain_clause(serializer.validated_data["clause"]))

    @action(detail=True, methods=["post"], url_path="analyze-risks")
    def analyze_risks(self, request, pk=None):
        document = self.get_object()
        serializer = AnalyzeRiskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data.get("content") or document.content
        return self._ai_response(lambda: LegalAIService().analyze_risks(content))

    @action(detail=True, methods=["post"], url_path="compare")
    def compare(self, request, pk=None):
        document = self.get_object()
        serializer = CompareDocumentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        versions = DocumentVersion.objects.filter(
            legal_document=document,
            id__in=[serializer.validated_data["base_version_id"], serializer.validated_data["target_version_id"]],
        )
        by_id = {version.id: version for version in versions}
        try:
            base = by_id[serializer.validated_data["base_version_id"]]
            target = by_id[serializer.validated_data["target_version_id"]]
        except KeyError as exc:
            raise ValidationError("Both versions must belong to this document.") from exc
        return self._ai_response(lambda: LegalAIService().compare_versions(base, target))

    @action(detail=True, methods=["get"], url_path="download-pdf")
    def download_pdf(self, request, pk=None):
        document = self.get_object()
        pdf = PDFService.render_document(document)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="legal-document-{document.id}.pdf"'
        return response

    @staticmethod
    def _ai_response(callback):
        try:
            return Response(callback())
        except AIProviderError as exc:
            raise APIException(str(exc)) from exc
