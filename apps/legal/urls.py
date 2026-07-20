from rest_framework.routers import DefaultRouter

from apps.legal.views import DocumentTemplateViewSet, LegalDocumentViewSet

router = DefaultRouter()
router.register("templates", DocumentTemplateViewSet, basename="document-template")
router.register("documents", LegalDocumentViewSet, basename="legal-document")

urlpatterns = router.urls
