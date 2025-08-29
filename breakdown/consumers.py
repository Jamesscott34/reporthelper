"""
WebSocket consumers for real-time collaboration features.

This module provides Django Channels WebSocket consumers for real-time
annotation updates, document collaboration, and presence indicators.
"""

import json
import logging

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Annotation, Document
from .serializers import AnnotationSerializer

logger = logging.getLogger(__name__)


class DocumentCollaborationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for document collaboration features.

    Handles real-time annotation updates, presence indicators, and
    collaborative editing features for documents. Users join a document-specific
    group and receive updates when other users make changes.

    WebSocket URL pattern: ws/documents/{document_id}/

    Message Types:
        - annotation_created: New annotation added
        - annotation_updated: Existing annotation modified
        - annotation_deleted: Annotation removed
        - user_joined: User joined document collaboration
        - user_left: User left document collaboration
        - presence_update: User presence/activity update
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document_id = None
        self.document_group_name = None
        self.user = None

    async def connect(self):
        """
        Handle WebSocket connection.

        Validates user authentication, document access permissions,
        and joins the document collaboration group.
        """
        # Extract document ID from URL route
        self.document_id = self.scope["url_route"]["kwargs"]["document_id"]
        self.document_group_name = f"doc_{self.document_id}"
        self.user = self.scope.get("user")

        # Check authentication
        if isinstance(self.user, AnonymousUser):
            logger.warning(
                f"Unauthenticated user attempted to connect to document {self.document_id}"
            )
            await self.close()
            return

        # Verify user has access to this document
        has_access = await self.check_document_access()
        if not has_access:
            logger.warning(
                f"User {self.user.username} denied access to document {self.document_id}"
            )
            await self.close()
            return

        # Join document group
        await self.channel_layer.group_add(self.document_group_name, self.channel_name)

        await self.accept()

        # Notify group that user joined
        await self.channel_layer.group_send(
            self.document_group_name,
            {
                "type": "user_joined",
                "user_id": self.user.id,
                "username": self.user.username,
                "timestamp": self._get_timestamp(),
            },
        )

        logger.info(
            f"User {self.user.username} connected to document {self.document_id}"
        )

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.

        Leaves the document collaboration group and notifies other users.
        """
        if self.document_group_name and self.user:
            # Notify group that user left
            await self.channel_layer.group_send(
                self.document_group_name,
                {
                    "type": "user_left",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "timestamp": self._get_timestamp(),
                },
            )

            # Leave document group
            await self.channel_layer.group_discard(
                self.document_group_name, self.channel_name
            )

            logger.info(
                f"User {self.user.username} disconnected from document {self.document_id}"
            )

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.

        Processes client messages for annotation updates, presence updates,
        and other collaboration features.

        Args:
            text_data: JSON string containing message data
        """
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "presence_update":
                await self.handle_presence_update(data)
            elif message_type == "annotation_event":
                await self.handle_annotation_event(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send_error("Unknown message type")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from user {self.user.username}")
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error("Message processing failed")

    async def handle_presence_update(self, data):
        """
        Handle user presence updates.

        Broadcasts user activity, cursor position, and other presence
        information to other collaborators.

        Args:
            data: Presence update data from client
        """
        # Broadcast presence update to group
        await self.channel_layer.group_send(
            self.document_group_name,
            {
                "type": "presence_update",
                "user_id": self.user.id,
                "username": self.user.username,
                "activity": data.get("activity", "active"),
                "cursor_position": data.get("cursor_position"),
                "selected_text": data.get("selected_text"),
                "timestamp": self._get_timestamp(),
            },
        )

    async def handle_annotation_event(self, data):
        """
        Handle annotation-related events from client.

        Note: This is primarily for client-side events. Most annotation
        CRUD operations should go through the REST API which will broadcast
        updates via the _broadcast_annotation_event method in views.py.

        Args:
            data: Annotation event data from client
        """
        # For now, just log the event
        # Real annotation CRUD should happen via REST API
        logger.info(f"Annotation event from {self.user.username}: {data.get('action')}")

    # Group message handlers (called by channel layer)

    async def annotation_event(self, event):
        """
        Handle annotation events from the channel layer.

        This method is called when annotation CRUD operations occur
        via the REST API and need to be broadcast to WebSocket clients.

        Args:
            event: Annotation event data from channel layer
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "annotation_event",
                    "action": event["action"],
                    "annotation": event["annotation"],
                    "timestamp": event.get("timestamp", self._get_timestamp()),
                }
            )
        )

    async def user_joined(self, event):
        """
        Handle user joined events.

        Notifies clients when a new user joins the document collaboration.
        """
        # Don't send join notification to the user who just joined
        if event["user_id"] != self.user.id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "user_joined",
                        "user_id": event["user_id"],
                        "username": event["username"],
                        "timestamp": event["timestamp"],
                    }
                )
            )

    async def user_left(self, event):
        """
        Handle user left events.

        Notifies clients when a user leaves the document collaboration.
        """
        # Don't send leave notification to the user who just left
        if event["user_id"] != self.user.id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "user_left",
                        "user_id": event["user_id"],
                        "username": event["username"],
                        "timestamp": event["timestamp"],
                    }
                )
            )

    async def presence_update(self, event):
        """
        Handle presence update events.

        Forwards presence updates from other users to the client.
        """
        # Don't send presence updates back to the originating user
        if event["user_id"] != self.user.id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "presence_update",
                        "user_id": event["user_id"],
                        "username": event["username"],
                        "activity": event["activity"],
                        "cursor_position": event.get("cursor_position"),
                        "selected_text": event.get("selected_text"),
                        "timestamp": event["timestamp"],
                    }
                )
            )

    # Helper methods

    @database_sync_to_async
    def check_document_access(self):
        """
        Check if the current user has access to the document.

        Returns:
            bool: True if user has access, False otherwise
        """
        try:
            document = Document.objects.get(id=self.document_id)
            # For now, check if user uploaded the document
            # TODO: Implement more sophisticated permission system
            return document.uploaded_by == self.user
        except ObjectDoesNotExist:
            return False

    async def send_error(self, message):
        """
        Send an error message to the client.

        Args:
            message: Error message to send
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "error",
                    "message": message,
                    "timestamp": self._get_timestamp(),
                }
            )
        )

    def _get_timestamp(self):
        """
        Get current timestamp in ISO format.

        Returns:
            str: Current timestamp in ISO 8601 format
        """
        from datetime import datetime

        return datetime.now().isoformat()


class AnnotationConsumer(AsyncWebsocketConsumer):
    """
    Specialized WebSocket consumer for annotation-specific events.

    This consumer provides more granular control over annotation events
    and can be used for annotation-specific features like real-time
    annotation editing, collaborative annotation creation, etc.

    WebSocket URL pattern: ws/documents/{document_id}/annotations/
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document_id = None
        self.annotation_group_name = None
        self.user = None

    async def connect(self):
        """Handle WebSocket connection for annotation-specific events."""
        self.document_id = self.scope["url_route"]["kwargs"]["document_id"]
        self.annotation_group_name = f"doc_{self.document_id}_annotations"
        self.user = self.scope.get("user")

        # Check authentication and document access
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        has_access = await self.check_document_access()
        if not has_access:
            await self.close()
            return

        # Join annotation-specific group
        await self.channel_layer.group_add(
            self.annotation_group_name, self.channel_name
        )

        await self.accept()
        logger.info(
            f"User {self.user.username} connected to annotations for document {self.document_id}"
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if self.annotation_group_name:
            await self.channel_layer.group_discard(
                self.annotation_group_name, self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming annotation-specific messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "annotation_draft":
                await self.handle_annotation_draft(data)
            elif message_type == "annotation_selection":
                await self.handle_annotation_selection(data)
            else:
                logger.warning(f"Unknown annotation message type: {message_type}")

        except json.JSONDecodeError:
            logger.error(
                f"Invalid JSON in annotation consumer from user {self.user.username}"
            )
        except Exception as e:
            logger.error(f"Error in annotation consumer: {e}")

    async def handle_annotation_draft(self, data):
        """
        Handle real-time annotation drafts.

        Allows users to see annotation drafts as other users are creating them,
        before they're saved to the database.
        """
        await self.channel_layer.group_send(
            self.annotation_group_name,
            {
                "type": "annotation_draft",
                "user_id": self.user.id,
                "username": self.user.username,
                "draft_data": data.get("draft_data", {}),
                "timestamp": self._get_timestamp(),
            },
        )

    async def handle_annotation_selection(self, data):
        """
        Handle text selection events for collaborative annotation creation.

        Shows other users what text is currently selected by each user.
        """
        await self.channel_layer.group_send(
            self.annotation_group_name,
            {
                "type": "annotation_selection",
                "user_id": self.user.id,
                "username": self.user.username,
                "selection": data.get("selection", {}),
                "timestamp": self._get_timestamp(),
            },
        )

    # Group message handlers

    async def annotation_draft(self, event):
        """Forward annotation draft events to clients."""
        if event["user_id"] != self.user.id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "annotation_draft",
                        "user_id": event["user_id"],
                        "username": event["username"],
                        "draft_data": event["draft_data"],
                        "timestamp": event["timestamp"],
                    }
                )
            )

    async def annotation_selection(self, event):
        """Forward annotation selection events to clients."""
        if event["user_id"] != self.user.id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "annotation_selection",
                        "user_id": event["user_id"],
                        "username": event["username"],
                        "selection": event["selection"],
                        "timestamp": event["timestamp"],
                    }
                )
            )

    async def annotation_created(self, event):
        """Handle annotation created events from REST API."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "annotation_created",
                    "annotation": event["annotation"],
                    "timestamp": event.get("timestamp", self._get_timestamp()),
                }
            )
        )

    async def annotation_updated(self, event):
        """Handle annotation updated events from REST API."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "annotation_updated",
                    "annotation": event["annotation"],
                    "timestamp": event.get("timestamp", self._get_timestamp()),
                }
            )
        )

    async def annotation_deleted(self, event):
        """Handle annotation deleted events from REST API."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "annotation_deleted",
                    "annotation_id": event["annotation_id"],
                    "timestamp": event.get("timestamp", self._get_timestamp()),
                }
            )
        )

    @database_sync_to_async
    def check_document_access(self):
        """Check if user has access to the document."""
        try:
            document = Document.objects.get(id=self.document_id)
            return document.uploaded_by == self.user
        except ObjectDoesNotExist:
            return False

    def _get_timestamp(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.now().isoformat()
