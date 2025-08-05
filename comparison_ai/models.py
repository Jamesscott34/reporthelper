"""
Models for the comparison_ai app.

This app handles AI-powered document comparisons and analysis.
"""

from django.db import models
from django.contrib.auth.models import User
from breakdown.models import Document, Breakdown
import json


class Comparison(models.Model):
    """
    Model to store document comparisons and their analysis.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='draft')

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ['-created_at']


class ComparisonDocument(models.Model):
    """
    Model to store documents that are part of a comparison.
    """
    comparison = models.ForeignKey(Comparison, on_delete=models.CASCADE, related_name='documents')
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document.title} (Order: {self.order})"

    class Meta:
        ordering = ['order']


class ComparisonAnalysis(models.Model):
    """
    Model to store AI analysis results for document comparisons.
    """
    comparison = models.ForeignKey(Comparison, on_delete=models.CASCADE, related_name='analyses')
    analysis_type = models.CharField(max_length=50, choices=[
        ('similarity', 'Similarity Analysis'),
        ('differences', 'Differences Analysis'),
        ('summary', 'Summary Comparison'),
        ('key_points', 'Key Points Comparison'),
        ('custom', 'Custom Analysis'),
    ])
    content = models.JSONField(default=dict)
    raw_analysis = models.TextField()
    ai_model_used = models.CharField(max_length=100, default='deepseek-r1')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='processing')

    def __str__(self):
        return f"{self.comparison.title} - {self.analysis_type}"

    def get_formatted_content(self):
        """
        Returns the analysis content in a formatted way.
        """
        if isinstance(self.content, str):
            try:
                return json.loads(self.content)
            except json.JSONDecodeError:
                return {'sections': [self.content]}
        return self.content

    class Meta:
        ordering = ['-created_at']


class ComparisonComment(models.Model):
    """
    Model to store user comments and feedback on comparisons.
    """
    comparison = models.ForeignKey(Comparison, on_delete=models.CASCADE, related_name='comments')
    analysis = models.ForeignKey(ComparisonAnalysis, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField()
    section_reference = models.CharField(max_length=100, blank=True)  # e.g., "similarity_analysis", "section_1"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment on {self.comparison.title} by {self.user.username if self.user else 'Anonymous'}"

    class Meta:
        ordering = ['-created_at']


class ComparisonPrompt(models.Model):
    """
    Model to store custom prompts used for comparison analysis.
    """
    comparison = models.ForeignKey(Comparison, on_delete=models.CASCADE, related_name='prompts')
    prompt_type = models.CharField(max_length=50, choices=[
        ('similarity', 'Similarity Analysis'),
        ('differences', 'Differences Analysis'),
        ('summary', 'Summary Comparison'),
        ('key_points', 'Key Points Comparison'),
        ('custom', 'Custom Analysis'),
    ])
    prompt_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    used_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.comparison.title} - {self.prompt_type} Prompt"

    class Meta:
        ordering = ['-created_at']
