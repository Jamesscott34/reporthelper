"""
Serializers for the breakdown app.

This module provides Django REST Framework serializers for all models,
with proper validation, permissions, and nested relationships.
"""

from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Annotation, Breakdown, Document, HowTo, QAEntry, Revision, Section


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with minimal fields for security.

    Returns only safe user information for API responses.
    """

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]
        read_only_fields = ["id", "username", "first_name", "last_name"]


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Document model with computed fields.

    Provides additional computed fields like file size, upload status,
    and related object counts for enhanced API responses.
    """

    file_size = serializers.SerializerMethodField()
    annotations_count = serializers.SerializerMethodField()
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "file",
            "file_type",
            "uploaded_at",
            "uploaded_by",
            "status",
            "document_type",
            "generation_method",
            "ai_model_used",
            "file_size",
            "annotations_count",
        ]
        read_only_fields = [
            "id",
            "uploaded_at",
            "uploaded_by",
            "status",
            "file_size",
            "annotations_count",
        ]

    def get_file_size(self, obj):
        """Get file size in bytes."""
        try:
            return obj.file.size if obj.file else 0
        except (ValueError, OSError):
            return 0

    def get_annotations_count(self, obj):
        """Get count of annotations for this document."""
        return obj.annotations.count()


class AnnotationSerializer(serializers.ModelSerializer):
    """
    Serializer for Annotation model with validation and context.

    Provides comprehensive annotation data with text content, context,
    and source location resolution. Includes proper validation for
    offset ranges and content requirements.
    """

    user = UserSerializer(read_only=True)
    text_content = serializers.SerializerMethodField()
    context = serializers.SerializerMethodField()
    source_location = serializers.SerializerMethodField()

    class Meta:
        model = Annotation
        fields = [
            "id",
            "document",
            "annotation_type",
            "start_offset",
            "end_offset",
            "content",
            "color",
            "user",
            "created_at",
            "updated_at",
            "text_content",
            "context",
            "source_location",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
            "text_content",
            "context",
            "source_location",
        ]
        extra_kwargs = {
            "document": {"required": False}  # Document comes from URL in nested routes
        }

    def get_text_content(self, obj):
        """Get the actual text this annotation covers."""
        return obj.get_text_content()

    def get_context(self, obj):
        """Get surrounding context for this annotation."""
        return obj.get_context()

    def get_source_location(self, obj):
        """Get resolved source location information."""
        return obj.resolve_to_source()

    def validate(self, attrs):
        """
        Validate annotation data with comprehensive checks.

        Ensures offsets are valid, within document bounds, and content
        is provided when required for comment/sticky note types.

        Args:
            attrs: Dictionary of field values to validate

        Returns:
            Validated attributes dictionary

        Raises:
            serializers.ValidationError: If validation fails
        """
        document = attrs.get("document")
        start_offset = attrs.get("start_offset")
        end_offset = attrs.get("end_offset")
        annotation_type = attrs.get("annotation_type")
        content = attrs.get("content", "").strip()

        # Basic offset validation
        if start_offset is not None and start_offset < 0:
            raise serializers.ValidationError("Start offset cannot be negative")

        if start_offset is not None and end_offset is not None:
            if end_offset <= start_offset:
                raise serializers.ValidationError(
                    "End offset must be greater than start offset"
                )

        # Document length validation (only if document is provided)
        if document and document.extracted_text and end_offset is not None:
            text_length = len(document.extracted_text)
            if end_offset > text_length:
                raise serializers.ValidationError(
                    f"End offset ({end_offset}) exceeds document length ({text_length})"
                )

        # Content validation for comment/sticky note types
        if annotation_type in ["comment", "sticky_note"] and not content:
            raise serializers.ValidationError(
                f"{annotation_type.replace('_', ' ').title()} annotations require content"
            )

        return attrs

    def create(self, validated_data):
        """
        Create annotation with current user.

        Automatically sets the user to the current request user.
        """
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class SectionSerializer(serializers.ModelSerializer):
    """
    Serializer for Section model with related data.

    Includes related HowTo guides and QA entries for complete section context.
    """

    howtos = serializers.SerializerMethodField()
    qa_entries = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            "id",
            "breakdown",
            "order",
            "title",
            "body",
            "short_summary",
            "pointers",
            "created_at",
            "updated_at",
            "howtos",
            "qa_entries",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "howtos", "qa_entries"]

    def get_howtos(self, obj):
        """Get related HowTo guides."""
        return HowToSerializer(obj.howtos.all(), many=True).data

    def get_qa_entries(self, obj):
        """Get related Q&A entries."""
        return QAEntrySerializer(obj.qa_entries.all(), many=True).data


class HowToSerializer(serializers.ModelSerializer):
    """
    Serializer for HowTo model with step validation.

    Validates that steps are properly formatted as a list of dictionaries
    with title and content fields.
    """

    class Meta:
        model = HowTo
        fields = [
            "id",
            "breakdown",
            "section",
            "scope",
            "title",
            "steps",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_steps(self, value):
        """
        Validate steps format.

        Ensures steps is a list of dictionaries with required fields.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Steps must be a list")

        for i, step in enumerate(value):
            if not isinstance(step, dict):
                raise serializers.ValidationError(f"Step {i + 1} must be a dictionary")

            if "title" not in step or "content" not in step:
                raise serializers.ValidationError(
                    f"Step {i + 1} must have 'title' and 'content' fields"
                )

        return value


class QAEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for QAEntry model with citation validation.

    Validates citation format and provides user information.
    """

    class Meta:
        model = QAEntry
        fields = [
            "id",
            "breakdown",
            "section",
            "scope",
            "question",
            "answer",
            "citations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_citations(self, value):
        """
        Validate citations format.

        Ensures citations is a list of dictionaries with proper structure.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Citations must be a list")

        for i, citation in enumerate(value):
            if not isinstance(citation, dict):
                raise serializers.ValidationError(
                    f"Citation {i + 1} must be a dictionary"
                )

            if "char_start" not in citation:
                raise serializers.ValidationError(
                    f"Citation {i + 1} must have 'char_start' field"
                )

        return value


class RevisionSerializer(serializers.ModelSerializer):
    """
    Serializer for Revision model with change tracking.

    Provides comprehensive revision information with user details
    and change validation.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Revision
        fields = [
            "id",
            "breakdown",
            "target_type",
            "target_id",
            "before",
            "after",
            "status",
            "user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate(self, attrs):
        """
        Validate revision data.

        Ensures target_type and target_id reference valid objects.
        """
        target_type = attrs.get("target_type")
        target_id = attrs.get("target_id")

        if target_type == "section":
            try:
                Section.objects.get(id=target_id)
            except Section.DoesNotExist:
                raise serializers.ValidationError(
                    f"Section with id {target_id} does not exist"
                )
        elif target_type == "howto":
            try:
                HowTo.objects.get(id=target_id)
            except HowTo.DoesNotExist:
                raise serializers.ValidationError(
                    f"HowTo with id {target_id} does not exist"
                )

        return attrs

    def create(self, validated_data):
        """Create revision with current user."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class BreakdownSerializer(serializers.ModelSerializer):
    """
    Serializer for Breakdown model with nested relationships.

    Provides complete breakdown data with sections, revisions, and related objects.
    """

    document = DocumentSerializer(read_only=True)
    sections = SectionSerializer(many=True, read_only=True)
    revisions = RevisionSerializer(many=True, read_only=True)
    howtos = HowToSerializer(many=True, read_only=True)
    qa_entries = QAEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Breakdown
        fields = [
            "id",
            "document",
            "content",
            "raw_breakdown",
            "created_at",
            "updated_at",
            "status",
            "ai_model_used",
            "step_by_step_content",
            "document_summary",
            "sections",
            "revisions",
            "howtos",
            "qa_entries",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "document",
            "sections",
            "revisions",
            "howtos",
            "qa_entries",
        ]


# Lightweight serializers for list views and nested relationships


class AnnotationListSerializer(serializers.ModelSerializer):
    """Lightweight annotation serializer for list views."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Annotation
        fields = [
            "id",
            "annotation_type",
            "start_offset",
            "end_offset",
            "color",
            "user",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight document serializer for list views."""

    uploaded_by = UserSerializer(read_only=True)
    annotations_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "file_type",
            "uploaded_at",
            "uploaded_by",
            "status",
            "document_type",
            "annotations_count",
        ]
        read_only_fields = [
            "id",
            "uploaded_at",
            "uploaded_by",
            "status",
            "annotations_count",
        ]

    def get_annotations_count(self, obj):
        """Get count of annotations for this document."""
        return obj.annotations.count()


class BreakdownListSerializer(serializers.ModelSerializer):
    """Lightweight breakdown serializer for list views."""

    document = DocumentListSerializer(read_only=True)
    sections_count = serializers.SerializerMethodField()

    class Meta:
        model = Breakdown
        fields = [
            "id",
            "document",
            "status",
            "ai_model_used",
            "created_at",
            "updated_at",
            "sections_count",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "document",
            "sections_count",
        ]

    def get_sections_count(self, obj):
        """Get count of sections in this breakdown."""
        return obj.sections.count()
