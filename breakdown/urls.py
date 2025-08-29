"""
URL configuration for breakdown app.

Includes both traditional Django views and REST API endpoints
for the annotation system and document management.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from . import views

app_name = "breakdown"

# REST API Router Configuration
router = DefaultRouter()
router.register(r"api/documents", views.DocumentViewSet, basename="api-documents")

# Nested router for annotations under documents
documents_router = routers.NestedDefaultRouter(
    router, r"api/documents", lookup="document"
)
documents_router.register(
    r"annotations", views.AnnotationViewSet, basename="document-annotations"
)

# Traditional Django URLs
urlpatterns = [
    path("", views.home, name="home"),
    path("upload/", views.upload_document, name="upload"),
    path(
        "upload/<int:document_id>/progress/",
        views.upload_progress,
        name="upload_progress",
    ),
    path(
        "breakdown/<int:breakdown_id>/",
        views.breakdown_detail,
        name="breakdown_detail",
    ),
    path(
        "breakdown/<int:breakdown_id>/viewer/",
        views.breakdown_viewer,
        name="breakdown_viewer",
    ),
    path(
        "breakdown/<int:breakdown_id>/compare/",
        views.compare_split,
        name="compare_split",
    ),
    path(
        "breakdown/<int:breakdown_id>/status/",
        views.breakdown_status,
        name="breakdown_status",
    ),
    path(
        "breakdown/<int:breakdown_id>/regenerate/",
        views.regenerate_breakdown,
        name="regenerate_breakdown",
    ),
    path(
        "breakdown/<int:breakdown_id>/run-ai-workflow/",
        views.run_ai_workflow,
        name="run_ai_workflow",
    ),
    path(
        "breakdown/<int:breakdown_id>/custom-prompt/",
        views.custom_prompt,
        name="custom_prompt",
    ),
    path(
        "breakdown/<int:breakdown_id>/ask/",
        views.ask_question,
        name="ask_question",
    ),
    path(
        "breakdown/<int:breakdown_id>/ask_on_text/",
        views.ask_on_text,
        name="ask_on_text",
    ),
    path(
        "breakdown/<int:breakdown_id>/regenerate-with-comments/",
        views.regenerate_with_comments,
        name="regenerate_with_comments",
    ),
    path(
        "breakdown/<int:breakdown_id>/sections/<int:section_id>/propose/",
        views.propose_section_update,
        name="propose_section_update",
    ),
    path(
        "breakdown/<int:breakdown_id>/sections/<int:section_id>/apply/",
        views.apply_section_update,
        name="apply_section_update",
    ),
    path(
        "breakdown/<int:breakdown_id>/sections/<int:section_id>/steps/",
        views.section_step_by_step,
        name="section_step_by_step",
    ),
    path(
        "breakdown/<int:breakdown_id>/sections/<int:section_id>/get/",
        views.get_section,
        name="get_section",
    ),
    path(
        "breakdown/<int:breakdown_id>/sections/<int:section_id>/"
        "revisions/<int:revision_id>/revert/",
        views.revert_section_revision,
        name="revert_section_revision",
    ),
    path(
        "breakdown/<int:breakdown_id>/sections/<int:section_id>/"
        "revisions/<int:revision_id>/reject/",
        views.reject_section_revision,
        name="reject_section_revision",
    ),
    path(
        "breakdown/<int:breakdown_id>/edit-section/",
        views.edit_breakdown_section,
        name="edit_breakdown_section",
    ),
    path(
        "save_document/<int:breakdown_id>/",
        views.save_document,
        name="save_document",
    ),
    path(
        "generate_report/<int:breakdown_id>/",
        views.generate_report,
        name="generate_report",
    ),
    path(
        "documents/<int:document_id>/save-extracted-text/",
        views.save_extracted_text,
        name="save_extracted_text",
    ),
    path("documents/", views.document_list, name="document_list"),
    path(
        "documents/<int:document_id>/delete/",
        views.delete_document,
        name="delete_document",
    ),
    path("customai/", views.custom_ai_view, name="custom_ai"),
    path(
        "customai/process/",
        views.custom_ai_process,
        name="custom_ai_process",
    ),
    # REST API URLs
    path("", include(router.urls)),
    path("", include(documents_router.urls)),
]
