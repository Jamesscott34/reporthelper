"""
Models for the breakdown app.

This app handles document uploads and AI-powered breakdown of documents into step-by-step instructions.
"""

from django.db import models
from django.contrib.auth.models import User
import json


class Document(models.Model):
    """
    Model to store uploaded documents and their metadata.
    """
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=10, choices=[
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('doc', 'DOC'),
        ('txt', 'TXT'),
    ])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    extracted_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='uploaded')

    def __str__(self):
        return f"{self.title} ({self.file_type})"

    class Meta:
        ordering = ['-uploaded_at']


class Breakdown(models.Model):
    """
    Model to store AI-generated breakdowns of documents.
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='breakdowns')
    content = models.JSONField(default=dict)
    raw_breakdown = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('finalized', 'Finalized'),
    ], default='draft')
    ai_model_used = models.CharField(max_length=100, default='deepseek-r1')

    def __str__(self):
        return f"Breakdown for {self.document.title}"

    def get_formatted_content(self):
        """
        Returns the breakdown content in a formatted way.
        """
        if isinstance(self.content, str):
            try:
                return json.loads(self.content)
            except json.JSONDecodeError:
                return {'sections': [self.content]}
        return self.content

    class Meta:
        ordering = ['-created_at']
