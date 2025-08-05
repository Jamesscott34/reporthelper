"""
Views for the breakdown app.

This module handles document uploads and AI-powered breakdown processing.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
from django.urls import reverse
import json
import os
import threading

from .models import Document, Breakdown
from .ai_breakdown import AIBreakdownService
from .utils import extract_text_from_file


def home(request):
    """
    Home view - displays the main upload interface.
    """
    # Get original documents and their generated files
    original_documents = Document.objects.filter(document_type='original').order_by('-uploaded_at')[:10]
    generated_documents = Document.objects.filter(document_type__in=['breakdown', 'report', 'comparison', 'export']).order_by('-uploaded_at')[:5]
    
    # Combine and sort by upload date
    all_documents = list(original_documents) + list(generated_documents)
    all_documents.sort(key=lambda x: x.uploaded_at, reverse=True)
    
    return render(request, 'breakdown/home.html', {
        'documents': all_documents[:15]  # Show up to 15 most recent documents
    })


def process_document_background(document_id, breakdown_id):
    """
    Background function to process document and update breakdown.
    """
    try:
        document = Document.objects.get(id=document_id)
        breakdown = Breakdown.objects.get(id=breakdown_id)
        
        # Update status to processing
        document.status = 'processing'
        document.save()
        
        # Extract text from the document
        print(f"Extracting text from {document.file.path}...")
        extracted_text = extract_text_from_file(
            document.file.path,
            document.file_type
        )
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            raise Exception("No text could be extracted from the document")
        
        document.extracted_text = extracted_text
        document.status = 'completed'
        document.save()
        
        print(f"Text extracted successfully. Length: {len(extracted_text)} characters")
        
        # Generate AI breakdown
        ai_service = AIBreakdownService()
        breakdown_result = ai_service.breakdown_document(extracted_text)
        
        if breakdown_result['success']:
            # Update breakdown with results
            breakdown.content = breakdown_result['breakdown']
            breakdown.raw_breakdown = breakdown_result['raw_response']
            breakdown.ai_model_used = breakdown_result['model_used']
            breakdown.status = 'completed'
            breakdown.save()
            
            print(f"Breakdown completed successfully for document {document.title}")
        else:
            breakdown.status = 'failed'
            breakdown.save()
            document.status = 'failed'
            document.save()
            print(f"Failed to process document: {breakdown_result['error']}")
            
    except Exception as e:
        print(f"Error processing document {document_id}: {str(e)}")
        try:
            document = Document.objects.get(id=document_id)
            document.status = 'failed'
            document.save()
            
            breakdown = Breakdown.objects.get(id=breakdown_id)
            breakdown.status = 'failed'
            breakdown.save()
        except:
            pass


def upload_document(request):
    """
    Handle document upload and initiate AI breakdown.
    """
    if request.method == 'POST':
        if 'document' not in request.FILES:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Please select a file to upload.'
                })
            messages.error(request, 'Please select a file to upload.')
            return redirect('breakdown:home')
        
        uploaded_file = request.FILES['document']
        
        # Validate file type
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        allowed_extensions = [
            ext.lower() for ext in settings.ALLOWED_FILE_TYPES
        ]
        if file_extension not in allowed_extensions:
            error_msg = (
                f'File type {file_extension} is not supported. '
                f'Allowed types: {", ".join(allowed_extensions)}'
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('breakdown:home')
        
        # Create document record
        document = Document.objects.create(
            title=uploaded_file.name,
            file=uploaded_file,
            file_type=file_extension.replace('.', ''),
            uploaded_by=request.user if request.user.is_authenticated else None,
            status='processing'
        )
        
        # Create a placeholder breakdown immediately
        placeholder_breakdown = Breakdown.objects.create(
            document=document,
            content={'sections': []},
            raw_breakdown='',
            status='processing',
            ai_model_used='deepseek/deepseek-coder-33b-instruct'
        )
        
        # Start background processing
        thread = threading.Thread(
            target=process_document_background,
            args=(document.id, placeholder_breakdown.id)
        )
        thread.daemon = True
        thread.start()
        
        # Redirect immediately to breakdown viewer
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Document uploaded successfully!',
                'redirect_url': reverse(
                    'breakdown:breakdown_viewer',
                    kwargs={'breakdown_id': placeholder_breakdown.id}
                ),
                'breakdown_id': placeholder_breakdown.id
            })
        
        # For non-AJAX requests, redirect immediately
        return redirect('breakdown:breakdown_viewer', breakdown_id=placeholder_breakdown.id)
    
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


def breakdown_viewer(request, breakdown_id):
    """
    Display the full breakdown viewer with markers and comments.
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    return render(request, 'breakdown/breakdown_viewer.html', {
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


@csrf_exempt
@require_http_methods(["POST"])
def custom_prompt(request, breakdown_id):
    """
    Handle custom AI prompts for breakdown improvement.
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        markers = data.get('markers', [])
        comments = data.get('comments', {})
        
        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'No prompt provided'
            }, status=400)
        
        # Create enhanced prompt with user feedback
        enhanced_prompt = f"""
{prompt}

Original Breakdown:
{breakdown.raw_breakdown}

User Markers:
{json.dumps(markers, indent=2)}

User Comments:
{json.dumps(comments, indent=2)}

Please review and improve the breakdown based on the user's feedback.
"""
        
        # Send to AI
        ai_service = AIBreakdownService()
        breakdown_result = ai_service.breakdown_document(enhanced_prompt)
        
        if breakdown_result['success']:
            # Create new breakdown or update existing
            breakdown.content = breakdown_result['breakdown']
            breakdown.raw_breakdown = breakdown_result['raw_response']
            breakdown.ai_model_used = breakdown_result['model_used']
            breakdown.save()
            
            return JsonResponse({
                'success': True,
                'breakdown': breakdown_result['breakdown'],
                'message': 'Breakdown updated with custom prompt'
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


@csrf_exempt
@require_http_methods(["POST"])
def regenerate_with_comments(request, breakdown_id):
    """
    Regenerate the breakdown taking into account user comments and markers.
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    
    try:
        data = json.loads(request.body)
        comments = data.get('comments', '')
        markers = data.get('markers', [])
        
        # Create enhanced prompt with comments
        enhanced_prompt = f"""
Please regenerate the following breakdown taking into account the user's comments and feedback:

Original Breakdown:
{breakdown.raw_breakdown}

User Comments:
{comments}

User Markers:
{json.dumps(markers, indent=2)}

Please improve the breakdown based on the user's feedback while maintaining the original structure and content.
"""
        
        # Send to AI
        ai_service = AIBreakdownService()
        breakdown_result = ai_service.breakdown_document(enhanced_prompt)
        
        if breakdown_result['success']:
            breakdown.content = breakdown_result['breakdown']
            breakdown.raw_breakdown = breakdown_result['raw_response']
            breakdown.ai_model_used = breakdown_result['model_used']
            breakdown.save()
            
            return JsonResponse({
                'success': True,
                'breakdown': breakdown_result['breakdown'],
                'message': 'Breakdown regenerated with comments'
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
    Delete a document and its associated files.
    """
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        try:
            # If this is an original document, delete all generated files first
            if document.is_original():
                generated_files = document.get_generated_files()
                for generated_file in generated_files:
                    # Delete the generated file from storage
                    if generated_file.file:
                        default_storage.delete(generated_file.file.name)
                    generated_file.delete()
                messages.success(request, f'Document "{document.title}" and {generated_files.count()} generated files deleted successfully.')
            else:
                # This is a generated file, just delete it
                if document.file:
                    default_storage.delete(document.file.name)
                messages.success(request, f'Generated file "{document.title}" deleted successfully.')
            
            # Delete the original document file from storage
            if document.file:
                default_storage.delete(document.file.name)
            
            document.delete()
            
        except Exception as e:
            messages.error(request, f'Error deleting document: {str(e)}')
            return redirect('breakdown:document_list')
        
        return redirect('breakdown:home')
    
    return render(request, 'breakdown/delete_confirm.html', {
        'document': document
    })


@csrf_exempt
@require_http_methods(["GET"])
def upload_progress(request, document_id):
    """
    Get the progress of document processing.
    """
    try:
        document = get_object_or_404(Document, id=document_id)
        
        progress_data = {
            'status': document.status,
            'progress': 0,
            'message': ''
        }
        
        if document.status == 'uploaded':
            progress_data.update({
                'progress': 25,
                'message': 'Document uploaded, extracting text...'
            })
        elif document.status == 'processing':
            progress_data.update({
                'progress': 50,
                'message': 'Extracting text from document...'
            })
        elif document.status == 'completed':
            progress_data.update({
                'progress': 75,
                'message': 'Generating AI breakdown...'
            })
        elif document.status == 'failed':
            progress_data.update({
                'progress': 0,
                'message': 'Processing failed'
            })
        
        return JsonResponse(progress_data)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'progress': 0,
            'message': str(e)
        })


@csrf_exempt
@require_http_methods(["GET"])
def breakdown_status(request, breakdown_id):
    """
    Check the status of a breakdown.
    """
    try:
        breakdown = get_object_or_404(Breakdown, id=breakdown_id)
        
        status_data = {
            'status': breakdown.status,
            'has_content': bool(breakdown.content.get('sections', [])),
            'has_raw_breakdown': bool(breakdown.raw_breakdown),
            'document_status': breakdown.document.status,
            'ai_model_used': breakdown.ai_model_used
        }
        
        return JsonResponse(status_data)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        })
