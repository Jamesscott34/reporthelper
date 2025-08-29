"""
WebSocket URL routing for the breakdown app.

This module defines WebSocket URL patterns for real-time collaboration
features including document collaboration and annotation updates.
"""

from django.urls import path

from . import consumers

websocket_urlpatterns = [
    # Document collaboration WebSocket
    # ws/documents/{document_id}/
    path(
        "ws/documents/<int:document_id>/",
        consumers.DocumentCollaborationConsumer.as_asgi(),
        name="document_collaboration",
    ),
    # Annotation-specific WebSocket
    # ws/documents/{document_id}/annotations/
    path(
        "ws/documents/<int:document_id>/annotations/",
        consumers.AnnotationConsumer.as_asgi(),
        name="document_annotations",
    ),
]
