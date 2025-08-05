"""
Views for the breakdown app.

This module handles document uploads and AI-powered breakdown processing.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.conf import settings
import json
import os

from .models import Document, Breakdown
from .ai_breakdown import AIBreakdownService
from .utils import extract_text_from_file


def home(request):
    """
    Home view - displays the main upload interface.
    """
    documents = Document.objects.all().order_by('-uploaded_at')[:10]
    return render(request, 'breakdown/home.html', {
        'documents': documents
    })


def upload_document(request):
    """
    Handle document upload and initiate AI breakdown.
    """
    if request.method == 'POST':
        if 'document' not in request.FILES:
            messages.error(request, 'Please select a file to upload.')
            return redirect('home')
        
        uploaded_file = request.FILES['document']
        
        # Validate file type
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in [ext.replace('.', '') for ext in settings.ALLOWED_FILE_TYPES]:
            messages.error(request, f'File type {file_extension} is not supported.')
            return redirect('home')
        
        # Create document record
        document = Document.objects.create(
            title=uploaded_file.name,
            file=uploaded_file,
            file_type=file_extension.replace('.', ''),
            uploaded_by=request.user if request.user.is_authenticated else None,
            status='processing'
        )
        
        try:
            # Extract text from the document
            extracted_text = extract_text_from_file(document.file.path, document.file_type)
            document.extracted_text = extracted_text
            document.status = 'completed'
            document.save()
            
            # Generate AI breakdown
            ai_service = AIBreakdownService()
            breakdown_result = ai_service.breakdown_document(extracted_text)
            
            if breakdown_result['success']:
                # Create breakdown record
                breakdown = Breakdown.objects.create(
                    document=document,
                    content=breakdown_result['breakdown'],
                    raw_breakdown=breakdown_result['raw_response'],
                    ai_model_used=breakdown_result['model_used']
                )
                
                messages.success(request, 'Document uploaded and processed successfully!')
                return redirect('breakdown_detail', breakdown_id=breakdown.id)
            else:
                document.status = 'failed'
                document.save()
                messages.error(request, f'Failed to process document: {breakdown_result["error"]}')
                
        except Exception as e:
            document.status = 'failed'
            document.save()
            messages.error(request, f'Error processing document: {str(e)}')
        
        return redirect('home')
    
    return render(request, 'breakdown/upload.html')


def breakdown_detail(request, breakdown_id):
    """
    Display the detailed breakdown of a document.
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    return render(request, 'breakdown/breakdown_detail.html', {
        'breakdown': breakdown,
        'document': breakdown.document
    })


@csrf_exempt
@require_http_methods(["POST"])
def regenerate_breakdown(request, breakdown_id):
    """
    Regenerate the breakdown for a document using AI.
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    
    try:
        ai_service = AIBreakdownService()
        breakdown_result = ai_service.breakdown_document(breakdown.document.extracted_text)
        
        if breakdown_result['success']:
            breakdown.content = breakdown_result['breakdown']
            breakdown.raw_breakdown = breakdown_result['raw_response']
            breakdown.ai_model_used = breakdown_result['model_used']
            breakdown.save()
            
            return JsonResponse({
                'success': True,
                'breakdown': breakdown_result['breakdown'],
                'message': 'Breakdown regenerated successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': breakdown_result['error']
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def document_list(request):
    """
    Display a list of all uploaded documents.
    """
    documents = Document.objects.all().order_by('-uploaded_at')
    return render(request, 'breakdown/document_list.html', {
        'documents': documents
    })


def delete_document(request, document_id):
    """
    Delete a document and its associated breakdowns.
    """
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        # Delete the file from storage
        if document.file:
            default_storage.delete(document.file.name)
        
        document.delete()
        messages.success(request, 'Document deleted successfully.')
        return redirect('document_list')
    
    return render(request, 'breakdown/delete_confirm.html', {
        'document': document
    })
