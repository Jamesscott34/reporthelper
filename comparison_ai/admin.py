"""
Admin configuration for comparison_ai app.
"""

from django.contrib import admin
from .models import Comparison, ComparisonDocument, ComparisonAnalysis, ComparisonComment, ComparisonPrompt


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    """
    Admin interface for Comparison model.
    """
    list_display = ['title', 'created_by', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(ComparisonDocument)
class ComparisonDocumentAdmin(admin.ModelAdmin):
    """
    Admin interface for ComparisonDocument model.
    """
    list_display = ['comparison', 'document', 'order', 'added_at']
    list_filter = ['added_at']
    search_fields = ['comparison__title', 'document__title']
    ordering = ['comparison', 'order']


@admin.register(ComparisonAnalysis)
class ComparisonAnalysisAdmin(admin.ModelAdmin):
    """
    Admin interface for ComparisonAnalysis model.
    """
    list_display = ['comparison', 'analysis_type', 'ai_model_used', 'status', 'created_at']
    list_filter = ['analysis_type', 'status', 'created_at', 'ai_model_used']
    search_fields = ['comparison__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(ComparisonComment)
class ComparisonCommentAdmin(admin.ModelAdmin):
    """
    Admin interface for ComparisonComment model.
    """
    list_display = ['comparison', 'user', 'section_reference', 'created_at']
    list_filter = ['created_at', 'section_reference']
    search_fields = ['comparison__title', 'comment', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(ComparisonPrompt)
class ComparisonPromptAdmin(admin.ModelAdmin):
    """
    Admin interface for ComparisonPrompt model.
    """
    list_display = ['comparison', 'prompt_type', 'used_count', 'created_at']
    list_filter = ['prompt_type', 'created_at']
    search_fields = ['comparison__title', 'prompt_text']
    readonly_fields = ['created_at', 'used_count']
    ordering = ['-created_at']
