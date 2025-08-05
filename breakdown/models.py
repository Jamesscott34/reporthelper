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
    
    # New fields for tracking relationships
    parent_document = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='generated_files')
    document_type = models.CharField(max_length=20, choices=[
        ('original', 'Original Upload'),
        ('breakdown', 'AI Breakdown'),
        ('report', 'Generated Report'),
        ('comparison', 'Comparison Analysis'),
        ('export', 'Exported File'),
    ], default='original')
    
    # Additional metadata for generated files
    generation_method = models.CharField(max_length=50, blank=True)  # e.g., 'AI Breakdown', 'Comparison Analysis'
    ai_model_used = models.CharField(max_length=100, blank=True)  # AI model used for generation

    def __str__(self):
        if self.document_type == 'original':
            return f"{self.title} ({self.file_type}) - Original"
        else:
            return f"{self.title} ({self.file_type}) - {self.document_type.title()}"
    
    def is_original(self):
        """Check if this is an original uploaded document."""
        return self.document_type == 'original' and self.parent_document is None
    
    def is_generated(self):
        """Check if this is a generated file."""
        return self.document_type != 'original'
    
    def get_original_document(self):
        """Get the original document that this file was generated from."""
        if self.is_original():
            return self
        elif self.parent_document:
            return self.parent_document.get_original_document()
        return None
    
    def get_generated_files(self):
        """Get all files generated from this document."""
        return self.generated_files.all()

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
