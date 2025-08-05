"""
Views for the comparison_ai app.

This module handles AI-powered document comparisons and analysis.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
import os

from .models import Comparison, ComparisonDocument, ComparisonAnalysis, ComparisonComment, ComparisonPrompt
from breakdown.models import Document
from breakdown.ai_breakdown import AIBreakdownService


def home(request):
    """
    Home view - displays the comparison interface.
    """
    comparisons = Comparison.objects.all().order_by('-created_at')[:10]
    documents = Document.objects.all().order_by('-uploaded_at')[:20]
    
    return render(request, 'comparison_ai/home.html', {
        'comparisons': comparisons,
        'documents': documents
    })


def create_comparison(request):
    """
    Create a new document comparison.
    """
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        document_ids = request.POST.getlist('documents')
        
        if not title:
            messages.error(request, 'Please provide a title for the comparison.')
            return redirect('comparison_ai:home')
        
        if len(document_ids) < 2:
            messages.error(request, 'Please select at least 2 documents to compare.')
            return redirect('comparison_ai:home')
        
        try:
            # Create comparison
            comparison = Comparison.objects.create(
                title=title,
                description=description,
                created_by=request.user if request.user.is_authenticated else None,
                status='draft'
            )
            
            # Add documents to comparison
            for i, doc_id in enumerate(document_ids):
                document = get_object_or_404(Document, id=doc_id)
                ComparisonDocument.objects.create(
                    comparison=comparison,
                    document=document,
                    order=i
                )
            
            messages.success(request, f'Comparison "{title}" created successfully!')
            return redirect('comparison_ai:comparison_detail', comparison_id=comparison.id)
            
        except Exception as e:
            messages.error(request, f'Error creating comparison: {str(e)}')
            return redirect('comparison_ai:home')
    
    documents = Document.objects.all().order_by('-uploaded_at')
    return render(request, 'comparison_ai/create_comparison.html', {
        'documents': documents
    })


def comparison_detail(request, comparison_id):
    """
    Display the detailed comparison analysis.
    """
    comparison = get_object_or_404(Comparison, id=comparison_id)
    analyses = comparison.analyses.all().order_by('-created_at')
    
    return render(request, 'comparison_ai/comparison_detail.html', {
        'comparison': comparison,
        'analyses': analyses
    })


def comparison_viewer(request, comparison_id):
    """
    Display the full comparison viewer with interactive analysis.
    """
    comparison = get_object_or_404(Comparison, id=comparison_id)
    analyses = comparison.analyses.all().order_by('-created_at')
    
    return render(request, 'comparison_ai/comparison_viewer.html', {
        'comparison': comparison,
        'analyses': analyses
    })


@csrf_exempt
@require_http_methods(["POST"])
def run_analysis(request, comparison_id):
    """
    Run AI analysis on the comparison.
    """
    comparison = get_object_or_404(Comparison, id=comparison_id)
    
    try:
        data = json.loads(request.body)
        analysis_type = data.get('analysis_type', 'similarity')
        custom_prompt = data.get('custom_prompt', '')
        
        # Get documents for comparison
        comparison_docs = comparison.documents.all().order_by('order')
        if comparison_docs.count() < 2:
            return JsonResponse({
                'success': False,
                'error': 'At least 2 documents are required for comparison'
            }, status=400)
        
        # Prepare documents for analysis
        documents_text = []
        for comp_doc in comparison_docs:
            doc = comp_doc.document
            if doc.extracted_text:
                documents_text.append(f"Document {comp_doc.order + 1}: {doc.title}\n{doc.extracted_text}")
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Document {doc.title} has no extracted text'
                }, status=400)
        
        # Create analysis prompt
        if analysis_type == 'similarity':
            prompt = f"""
Please analyze the similarities between the following documents:

{' '.join(documents_text)}

Focus on:
- Common themes and topics
- Similar arguments or points
- Shared methodologies or approaches
- Overlapping conclusions or recommendations

Provide a structured analysis with clear sections.
"""
        elif analysis_type == 'differences':
            prompt = f"""
Please analyze the differences between the following documents:

{' '.join(documents_text)}

Focus on:
- Unique arguments or perspectives
- Different methodologies or approaches
- Conflicting conclusions or recommendations
- Distinct themes or topics

Provide a structured analysis with clear sections.
"""
        elif analysis_type == 'summary':
            prompt = f"""
Please provide a comprehensive summary comparison of the following documents:

{' '.join(documents_text)}

Focus on:
- Key points from each document
- Overall themes and patterns
- Main conclusions or recommendations
- Comparative insights

Provide a structured summary with clear sections.
"""
        elif analysis_type == 'key_points':
            prompt = f"""
Please extract and compare the key points from the following documents:

{' '.join(documents_text)}

Focus on:
- Main arguments or claims
- Key findings or results
- Important recommendations
- Critical insights

Provide a structured comparison with clear sections.
"""
        elif analysis_type == 'custom':
            if not custom_prompt:
                return JsonResponse({
                    'success': False,
                    'error': 'Custom prompt is required for custom analysis'
                }, status=400)
            prompt = f"""
{custom_prompt}

Documents to analyze:

{' '.join(documents_text)}
"""
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unknown analysis type: {analysis_type}'
            }, status=400)
        
        # Run AI analysis
        ai_service = AIBreakdownService()
        analysis_result = ai_service.breakdown_document(prompt)
        
        if analysis_result['success']:
            # Create analysis record
            analysis = ComparisonAnalysis.objects.create(
                comparison=comparison,
                analysis_type=analysis_type,
                content=analysis_result['breakdown'],
                raw_analysis=analysis_result['raw_response'],
                ai_model_used=analysis_result['model_used'],
                status='completed'
            )
            
            return JsonResponse({
                'success': True,
                'analysis': analysis_result['breakdown'],
                'analysis_id': analysis.id,
                'message': f'{analysis_type.replace("_", " ").title()} completed successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': analysis_result['error']
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_comment(request, comparison_id):
    """
    Add a comment to a comparison or analysis.
    """
    comparison = get_object_or_404(Comparison, id=comparison_id)
    
    try:
        data = json.loads(request.body)
        comment_text = data.get('comment', '').strip()
        analysis_id = data.get('analysis_id')
        section_reference = data.get('section_reference', '')
        
        if not comment_text:
            return JsonResponse({
                'success': False,
                'error': 'Comment text is required'
            }, status=400)
        
        analysis = None
        if analysis_id:
            analysis = get_object_or_404(ComparisonAnalysis, id=analysis_id, comparison=comparison)
        
        comment = ComparisonComment.objects.create(
            comparison=comparison,
            analysis=analysis,
            user=request.user if request.user.is_authenticated else None,
            comment=comment_text,
            section_reference=section_reference
        )
        
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'message': 'Comment added successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def comparison_list(request):
    """
    Display a list of all comparisons.
    """
    comparisons = Comparison.objects.all().order_by('-created_at')
    return render(request, 'comparison_ai/comparison_list.html', {
        'comparisons': comparisons
    })


def delete_comparison(request, comparison_id):
    """
    Delete a comparison and its associated data.
    """
    comparison = get_object_or_404(Comparison, id=comparison_id)
    
    if request.method == 'POST':
        comparison.delete()
        messages.success(request, 'Comparison deleted successfully.')
        return redirect('comparison_ai:comparison_list')
    
    return render(request, 'comparison_ai/delete_confirm.html', {
        'comparison': comparison
    })
