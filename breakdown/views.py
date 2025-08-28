# flake8: noqa
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
from django.utils import timezone
from django.core.files import File

from .models import Document, Breakdown, Section, HowTo, QAEntry, Revision
from .ai_breakdown import AIBreakdownService
from .utils import extract_text_from_file
from .utils import extract_text_with_pointers, unpack_zip_to_temp


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
        
        # Extract text and pointer map
        extracted_text, extraction_map = extract_text_with_pointers(
            document.file.path,
            document.file_type
        )
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            raise Exception("No text could be extracted from the document")
        
        document.extracted_text = extracted_text
        document.extraction_map = extraction_map
        document.status = 'completed'
        document.save()
        
        # Don't run AI automatically - let user choose when to run it
        # Just mark the document as ready for AI processing
        document.status = 'ready_for_ai'
        document.save()
        
        # Keep breakdown in 'ready' status until user requests AI processing
        breakdown.status = 'ready'
        breakdown.save()
        
    except Exception as e:
        # logging removed
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
        
        # Handle ZIP uploads by unpacking and creating child documents
        if file_extension == '.zip':
            document = Document.objects.create(
                title=uploaded_file.name,
                file=uploaded_file,
                file_type='zip',
                uploaded_by=(request.user if request.user.is_authenticated else None),
                status='processing'
            )
            temp_dir = unpack_zip_to_temp(document.file.path)
            for root, _, files in os.walk(temp_dir):
                for fname in files:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext.lstrip('.') not in ['pdf', 'docx', 'doc', 'txt']:
                        continue
                    abs_path = os.path.join(root, fname)
                    with open(abs_path, 'rb') as fh:
                        from django.core.files.base import ContentFile
                        content_file = ContentFile(fh.read(), name=fname)
                        child_doc = Document.objects.create(
                            title=fname,
                            file=content_file,
                            file_type=ext.replace('.', ''),
                            uploaded_by=(request.user if request.user.is_authenticated else None),
                            parent_document=document,
                            status='processing'
                        )
                        child_bd = Breakdown.objects.create(
                            document=child_doc,
                            content={'sections': []},
                            raw_breakdown='',
                            status='processing',
                            ai_model_used='deepseek/deepseek-coder-33b-instruct'
                        )
                        t = threading.Thread(
                            target=process_document_background,
                            args=(child_doc.id, child_bd.id)
                        )
                        t.daemon = True
                        t.start()
            return redirect('breakdown:document_list')

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


def compare_split(request, breakdown_id):
    """
    Split view: left shows AI outputs, right shows original text with pointers.
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    document = breakdown.document
    extraction_map = getattr(document, 'extraction_map', {}) or {}

    # Build anchored segments from extraction_map for precise jumps
    orig_segments = []
    text = document.extracted_text or ''
    try:
        mtype = extraction_map.get('type')
        if mtype == 'pdf':
            for page in extraction_map.get('pages', []):
                lines = page.get('lines', [])
                if not lines:
                    continue
                start = lines[0].get('char_start', 0)
                end = lines[-1].get('char_end', 0)
                segment_text = text[start:end]
                orig_segments.append({
                    'id': f"page-{page.get('page', 0)}",
                    'label': f"Page {page.get('page', 0)}",
                    'start': start,
                    'text': segment_text,
                })
        elif mtype == 'docx':
            for para in extraction_map.get('paragraphs', []):
                start = para.get('char_start', 0)
                end = para.get('char_end', 0)
                segment_text = text[start:end]
                orig_segments.append({
                    'id': f"para-{para.get('index', 0)}",
                    'label': f"Paragraph {para.get('index', 0)}",
                    'start': start,
                    'text': segment_text,
                })
        elif mtype in ('txt', 'doc'):
            for line in extraction_map.get('lines', []):
                start = line.get('char_start', 0)
                end = line.get('char_end', 0)
                segment_text = text[start:end]
                lid = line.get('line') or line.get('index') or 0
                orig_segments.append({
                    'id': f"line-{lid}",
                    'label': f"Line {lid}",
                    'start': start,
                    'text': segment_text,
                })
    except Exception:
        # Fallback: no segments
        orig_segments = []

    return render(request, 'breakdown/compare_split.html', {
        'breakdown': breakdown,
        'document': document,
        'extraction_map': extraction_map,
        'orig_segments': orig_segments,
    })


@csrf_exempt
@require_http_methods(["POST"])
def run_ai_workflow(request, breakdown_id):
    """
    Run AI workflow when user clicks one of the workflow buttons.
    """
    try:
        # logging removed
        breakdown = get_object_or_404(Breakdown, id=breakdown_id)
        document = breakdown.document
        
        # logging removed
        
        # Check if document has extracted text
        if not document.extracted_text:
            return JsonResponse({
                'success': False,
                'error': 'No extracted text available. Please upload a document first.'
            })
        
        # Get the workflow type and current content from the request
        data = json.loads(request.body)
        workflow_type = data.get('workflow_type', 'breakdown')
        current_content = data.get('current_content', document.extracted_text)
        
        # logging removed
        
        # Update status to processing
        breakdown.status = 'processing'
        breakdown.save()
        
        # logging removed
        # Run AI processing based on workflow type, using current content
        ai_service = AIBreakdownService()
        
        if workflow_type == 'breakdown':
            # logging removed
            result = ai_service.breakdown_document(current_content)
        elif workflow_type == 'stepbystep':
            # logging removed
            # For step-by-step, create simplified action steps based on the content
            step_result = ai_service.create_step_by_step_guide(current_content)
            # Convert step-by-step result to expected format
            result = {
                'success': True,
                'breakdown': _format_step_by_step_result(step_result),
                'raw_response': step_result.get('raw_response', ''),
                'model_used': getattr(ai_service, 'model', 'Unknown'),
                'step_by_step_data': step_result
            }
        elif workflow_type == 'report':
            # logging removed
            # For report, create a detailed report reviewing both extracted text and breakdown
            result = ai_service.create_detailed_report(
                document.extracted_text, 
                current_content
            )
        elif workflow_type == 'review-compare':
            # logging removed
            result = ai_service.breakdown_document(current_content)
        else:
            # logging removed
            result = ai_service.breakdown_document(current_content)
        
        # logging removed
        
        if result.get('success', False):
            # Update breakdown with results
            if workflow_type == 'stepbystep':
                # For step-by-step, save the structured data but preserve original breakdown
                if not hasattr(breakdown, 'step_by_step_content') or not breakdown.step_by_step_content:
                    # Store step-by-step content separately
                    breakdown.step_by_step_content = result.get('step_by_step_data', {})
                breakdown.raw_breakdown = result['raw_response']
                # Persist/Update document-scoped HowTo
                try:
                    steps_payload = result.get('step_by_step_data', {}).get('sections', [])
                    normalized_steps = []
                    for i, sec in enumerate(steps_payload, start=1):
                        if isinstance(sec, dict):
                            normalized_steps.append({
                                'title': sec.get('title') or f'Step {i}',
                                'content': sec.get('content') or ''
                            })
                        else:
                            normalized_steps.append({'title': f'Step {i}', 'content': str(sec)})
                    howto, created = HowTo.objects.get_or_create(
                        breakdown=breakdown,
                        section=None,
                        scope='document',
                        defaults={'title': 'How to apply this document', 'steps': normalized_steps}
                    )
                    if not created:
                        howto.steps = normalized_steps
                        howto.save()
                except Exception:
                    pass
            else:
                # For other workflows, save structured content
                breakdown.content = result['breakdown']
                breakdown.raw_breakdown = result['raw_response']
                # Populate Section rows if structured sections are available
                try:
                    sections = result['breakdown'].get('sections', [])
                    if sections and isinstance(sections, list):
                        # Clear previous sections on re-run
                        breakdown.sections.all().delete()
                        for idx, sec in enumerate(sections, start=1):
                            if isinstance(sec, dict):
                                title = sec.get('title') or f'Section {idx}'
                                body = sec.get('content') or sec.get('body') or ''
                                pointers = sec.get('pointers', {})
                            else:
                                # Legacy string section
                                title = f'Section {idx}'
                                body = str(sec)
                                pointers = {}
                            Section.objects.create(
                                breakdown=breakdown,
                                order=idx,
                                title=title[:255],
                                body=body,
                                pointers=pointers,
                            )
                        # Generate summaries
                        try:
                            # Document-level summary
                            try:
                                doc_summary = AIBreakdownService().summarize_document(
                                    document.extracted_text
                                )
                                breakdown.document_summary = doc_summary
                                breakdown.save()
                            except Exception:
                                pass
                            # Section short summaries (cap to 15 to limit calls)
                            svc = AIBreakdownService()
                            for s in breakdown.sections.all().order_by('order')[:15]:
                                try:
                                    s.short_summary = svc.summarize_section(
                                        s.title, s.body
                                    )
                                    s.save()
                                except Exception:
                                    continue
                        except Exception:
                            pass
                except Exception:
                    # Non-fatal; keep raw content
                    pass
            
            breakdown.ai_model_used = result.get('model_used', 'Unknown')
            breakdown.status = 'completed'
            breakdown.save()
            
            # logging removed
            return JsonResponse({
                'success': True,
                'message': f'{workflow_type.replace("-", " ").title()} completed successfully!',
                'breakdown': result['breakdown'],
                'step_by_step_data': result.get('step_by_step_data')
            })
        else:
            breakdown.status = 'failed'
            breakdown.save()
            # logging removed
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'AI processing failed')
            })
            
    except Exception as e:
        # logging removed
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def _format_step_by_step_result(step_result):
    """
    Format step-by-step result for display.
    
    Args:
        step_result: Result from create_step_by_step_guide
        
    Returns:
        Formatted string for display
    """
    if not step_result or 'sections' not in step_result:
        return "No step-by-step data available"
    
    sections = step_result['sections']
    if not sections:
        return "No step-by-step data available"
    
    # Format sections as a structured breakdown
    formatted_result = "Step-by-Step Analysis:\n\n"
    
    for i, section in enumerate(sections):
        if isinstance(section, dict):
            title = section.get('title', f'Step {i+1}')
            content = section.get('content', '')
            formatted_result += f"{title}\n{content}\n\n"
        else:
            # Handle string sections
            formatted_result += f"{section}\n\n"
    
    return formatted_result.strip()


@csrf_exempt
@require_http_methods(["POST"])
def ask_question(request, breakdown_id):
    """
    Q&A endpoint. Body: { question, scope, section_id }
    Returns: { success, answer, citations }
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    document = breakdown.document
    try:
        payload = json.loads(request.body or '{}')
        question = payload.get('question', '').strip()
        scope = payload.get('scope', 'section')
        section_id = payload.get('section_id')
        if not question:
            return JsonResponse({'success': False, 'error': 'Question is required'}, status=400)

        # Build context based on scope
        context_text = ''
        if scope == 'document':
            context_text = document.extracted_text or ''
        elif scope == 'neighbors' and section_id:
            sec_qs = list(breakdown.sections.all().order_by('order'))
            try:
                idx = next(i for i, s in enumerate(sec_qs) if s.id == int(section_id))
            except StopIteration:
                idx = 0
            neighbor_idxs = [i for i in [idx - 1, idx, idx + 1] if 0 <= i < len(sec_qs)]
            parts = [sec_qs[i].body for i in neighbor_idxs]
            context_text = "\n\n".join(parts)
        elif section_id:
            s = get_object_or_404(Section, id=section_id, breakdown=breakdown)
            context_text = s.body
        else:
            context_text = document.extracted_text or ''

        # Compose prompt with citation requirement
        prompt = (
            "Answer the question concisely using ONLY the provided context. "
            "Return JSON with fields: answer (string), citations (array of objects with char_start and optional page/index/line).\n\n"
            "CONTEXT:\n" + context_text[:8000] + "\n\nQUESTION: " + question
        )
        ai = AIBreakdownService()
        raw = ai._make_request(prompt) or ''
        answer_text = ''
        citations = []
        try:
            parsed = json.loads(raw)
            answer_text = parsed.get('answer', '')
            citations = parsed.get('citations', []) or []
        except Exception:
            answer_text = raw.strip()
            citations = []

        qa = QAEntry.objects.create(
            breakdown=breakdown,
            section=Section.objects.filter(id=section_id).first() if section_id else None,
            scope=scope,
            question=question,
            answer=answer_text,
            citations=citations,
        )
        return JsonResponse({'success': True, 'answer': answer_text, 'citations': citations, 'qa_id': qa.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def propose_section_update(request, breakdown_id, section_id):
    """
    Propose an AI-generated update for a section. Does NOT apply changes.

    Body: { prompt }
    Returns: { success, title, content }
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    section = get_object_or_404(Section, id=section_id, breakdown=breakdown)
    data = json.loads(request.body or '{}')
    user_prompt = (data.get('prompt') or '').strip()
    base = (
        "You are improving a section of a document. Rewrite the section content "
        "to be clearer, more complete, and logically structured. Keep factual accuracy. "
        "Return JSON only with fields {title, content}."
    )
    composed = (
        f"{base}\n\nCURRENT TITLE:\n{section.title}\n\nCURRENT CONTENT:\n{section.body}\n\n"
        f"USER INSTRUCTIONS:\n{user_prompt}"
    )
    try:
        ai = AIBreakdownService()
        raw = ai._make_request(composed) or ''
        title, content = section.title, section.body
        try:
            parsed = json.loads(raw)
            title = parsed.get('title') or title
            content = parsed.get('content') or content
        except Exception:
            # Fallback: use raw text as content
            content = raw.strip() or content
        return JsonResponse({'success': True, 'title': title, 'content': content})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def apply_section_update(request, breakdown_id, section_id):
    """
    Apply an approved section update and sync `breakdown.content`.
    Body: { title, content }
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    section = get_object_or_404(Section, id=section_id, breakdown=breakdown)
    try:
        data = json.loads(request.body or '{}')
        title = (data.get('title') or section.title)[:255]
        content = data.get('content') or section.body
        # Create revision (proposed->accepted immediately since user clicked Apply)
        Revision.objects.create(
            breakdown=breakdown,
            target_type='section',
            target_id=section.id,
            before={'title': section.title, 'content': section.body},
            after={'title': title, 'content': content},
            status='accepted',
            user=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
        )
        section.title = title
        section.body = content
        section.save()
        # Rebuild breakdown.content from sections
        rebuilt = []
        for s in breakdown.sections.all().order_by('order'):
            rebuilt.append({'title': s.title, 'content': s.body})
        breakdown.content = {'sections': rebuilt}
        breakdown.save()
        return JsonResponse({'success': True, 'title': title, 'content': content})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def revert_section_revision(request, breakdown_id, section_id, revision_id):
    """
    Revert a section to the 'before' state of a given revision and record a new accepted revision.
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    section = get_object_or_404(Section, id=section_id, breakdown=breakdown)
    revision = get_object_or_404(Revision, id=revision_id, breakdown=breakdown)
    # Ensure target matches
    if revision.target_type != 'section' or int(revision.target_id) != int(section.id):
        return JsonResponse({'success': False, 'error': 'Revision does not apply to this section'}, status=400)
    try:
        before_payload = revision.before or {}
        new_title = (before_payload.get('title') or section.title)[:255]
        new_content = before_payload.get('content') or section.body
        # Record a new accepted revision capturing this revert
        Revision.objects.create(
            breakdown=breakdown,
            target_type='section',
            target_id=section.id,
            before={'title': section.title, 'content': section.body},
            after={'title': new_title, 'content': new_content},
            status='accepted',
            user=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
        )
        # Apply change
        section.title = new_title
        section.body = new_content
        section.save()
        # Rebuild breakdown.content from sections
        rebuilt = [{'title': s.title, 'content': s.body} for s in breakdown.sections.all().order_by('order')]
        breakdown.content = {'sections': rebuilt}
        breakdown.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def section_step_by_step(request, breakdown_id, section_id):
    """
    Generate step-by-step for a specific section and persist as section-scoped HowTo.
    Body: { }
    Returns: { success, steps }
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    section = get_object_or_404(Section, id=section_id, breakdown=breakdown)
    guide_prompt = (
        "Create a comprehensive, beginner-friendly, step-by-step guide that expands the content into actionable "
        "instructions with: 1) direct download links (official sources), 2) exact commands for Windows PowerShell "
        "and Linux/macOS (where applicable), 3) configuration file snippets, 4) verification checks, and 5) common "
        "troubleshooting tips. Use clear headings, numbered steps, substeps, and include WHY each step matters. "
        "Where possible, include both GUI and CLI paths. Format code blocks with proper fencing and label the shell "
        "(powershell, bash). If the content requests a report or a word count (e.g., 600 words), generate a fluent, "
        "no-fluff report instead, with numbered sections and image placeholders (e.g., \"Figure 1.1: …\"). Minimum "
        "500 words unless a higher count is specified.\n\nCONTENT:\n" + section.body
    )
    try:
        ai = AIBreakdownService()
        raw = ai._make_request(guide_prompt) or ''
        # Parse into steps using breakdown parser for consistency
        parsed = ai._parse_breakdown_response(raw)
        steps_payload = parsed.get('sections', [])
        normalized_steps = []
        for i, sec in enumerate(steps_payload, start=1):
            if isinstance(sec, dict):
                normalized_steps.append({'title': sec.get('title') or f'Step {i}', 'content': sec.get('content') or ''})
            else:
                normalized_steps.append({'title': f'Step {i}', 'content': str(sec)})
        # Upsert section-scoped HowTo
        howto, created = HowTo.objects.get_or_create(
            breakdown=breakdown,
            section=section,
            scope='section',
            defaults={'title': f'How to apply: {section.title}', 'steps': normalized_steps}
        )
        if not created:
            howto.steps = normalized_steps
            howto.title = f'How to apply: {section.title}'
            howto.save()
        return JsonResponse({'success': True, 'steps': normalized_steps})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_section(request, breakdown_id, section_id):
    """
    Return JSON for a single section and its how-tos to support AJAX refresh.
    """
    breakdown = get_object_or_404(Breakdown, id=breakdown_id)
    section = get_object_or_404(Section, id=section_id, breakdown=breakdown)
    howtos = section.howtos.all()
    return JsonResponse({
        'success': True,
        'section': {
            'id': section.id,
            'order': section.order,
            'title': section.title,
            'short_summary': section.short_summary,
            'body': section.body,
            'pointers': section.pointers,
        },
        'howtos': [
            {
                'title': h.title,
                'steps': h.steps,
            } for h in howtos
        ],
        'revisions': [
            {
                'id': rv.id,
                'status': rv.status,
                'created_at': rv.created_at.isoformat(),
                'before': rv.before,
                'after': rv.after,
            } for rv in Revision.objects.filter(breakdown=breakdown, target_type='section', target_id=section.id).order_by('-created_at')[:10]
        ],
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


@csrf_exempt
@require_http_methods(["POST"])
def save_extracted_text(request, document_id):
    """
    Save changes to the extracted text of a document.
    """
    try:
        document = get_object_or_404(Document, id=document_id)
        data = json.loads(request.body)
        new_text = data.get('extracted_text', '')
        
        if not new_text.strip():
            return JsonResponse({
                'success': False,
                'error': 'Extracted text cannot be empty'
            }, status=400)
        
        # Update the extracted text
        document.extracted_text = new_text
        document.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Extracted text updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def custom_ai_view(request):
    """
    View for the custom AI analysis page.
    """
    return render(request, 'customai.html')


@csrf_exempt
@require_http_methods(["POST"])
def custom_ai_process(request):
    """
    Process Custom AI prompts using the same backend model/service as breakdown.
    Expects JSON body: { prompt: string, content: string }
    Returns JSON: { success: bool, response: string, model_used: string }
    """
    try:
        data = json.loads(request.body or '{}')
        prompt = data.get('prompt', '').strip()
        content = data.get('content', '').strip()
        prompt_type = data.get('prompt_type', '').strip()

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        ai_service = AIBreakdownService()

        # If user asks for a report, generate a full report instead of step-by-step
        wants_report = any(k in (prompt + " " + content).lower() for k in [
            ' report', 'write a report', 'word report', '600 word', '500 word'
        ])

        # Prefer standardized template when a known prompt_type is provided
        if prompt_type == 'detailed-steps':
            template = ai_service._load_step_by_step_prompt_template()
            if template:
                full_prompt = template.replace('{INPUT_TEXT}', content)
            else:
                # Minimal robust fallback
                full_prompt = (
                    'Create a beginner-friendly, step-by-step guide with numbered '
                    'steps, WHY each step matters, Windows (PowerShell) and '
                    'Linux/macOS (bash) commands, config snippets, verification '
                    'checks, troubleshooting tips, and official download links.\n\n'
                    f'Input:\n{content}'
                )
            # First, generate the step-by-step guide
            steps_result = ai_service.run_freeform_prompt(full_prompt)

            # If a report was requested too, generate and append it
            if wants_report:
                report = ai_service.create_detailed_report(content, content)
                combined_text = ''
                if steps_result.get('success'):
                    combined_text += steps_result.get('response', '')
                if report and report.get('sections'):
                    parts = []
                    for idx, sec in enumerate(report['sections'], start=1):
                        title = sec.get('title', f'Section {idx}')
                        body = sec.get('content', '')
                        parts.append(f"{title}\n{body}")
                    combined_text += "\n\n" + "\n\n".join(parts)
                return JsonResponse({
                    'success': True,
                    'response': combined_text.strip() or 'No content generated',
                    'model_used': getattr(ai_service, 'model', 'Unknown')
                })

            # Otherwise just return the step-by-step output
            return JsonResponse({
                'success': steps_result.get('success', False),
                'response': steps_result.get('response', '') or 'No content generated',
                'model_used': steps_result.get('model_used', getattr(ai_service, 'model', 'Unknown'))
            })

        # If user asks for a report but no detailed-steps were requested, return only the report
        if wants_report:
            report = ai_service.create_detailed_report(content, content)
            if report and report.get('sections'):
                parts = []
                for idx, sec in enumerate(report['sections'], start=1):
                    title = sec.get('title', f'Section {idx}')
                    body = sec.get('content', '')
                    parts.append(f"{title}\n{body}")
                return JsonResponse({
                    'success': True,
                    'response': "\n\n".join(parts),
                    'model_used': report.get('model_used', 'Unknown')
                })
        else:
            # If content is provided, append it beneath the prompt with clear delimiter
            full_prompt = prompt
            if content:
                full_prompt = f"{prompt}\n\n---\n\nCONTENT TO ANALYZE:\n{content}"

        result = ai_service.run_freeform_prompt(full_prompt)

        if result.get('success'):
            return JsonResponse({
                'success': True,
                'response': result.get('response', ''),
                'model_used': result.get('model_used', 'Unknown')
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'AI request failed'),
                'model_used': result.get('model_used', 'Unknown')
            }, status=502)
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
@require_http_methods(["POST"])
def edit_breakdown_section(request, breakdown_id):
    """
    Edit a specific section in the breakdown content.
    """
    try:
        breakdown = get_object_or_404(Breakdown, id=breakdown_id)
        data = json.loads(request.body)
        
        section_id = data.get('section_id')
        new_title = data.get('title')
        new_content = data.get('content')
        
        if not all([section_id, new_title, new_content]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: section_id, title, or content'
            })
        
        # Get current breakdown content
        current_content = breakdown.content
        
        # Update the specific section
        if 'sections' in current_content and isinstance(current_content['sections'], list):
            # Find and update the section by index (1-based)
            for i, section in enumerate(current_content['sections']):
                if str(i + 1) == str(section_id):
                    # Support both dict-based sections and legacy string sections
                    if isinstance(section, dict):
                        section['title'] = new_title
                        section['content'] = new_content
                        current_content['sections'][i] = section
                    else:
                        # Convert string section to structured dict
                        current_content['sections'][i] = {
                            'title': new_title,
                            'content': new_content
                        }
                    break
        
        # Save the updated breakdown
        breakdown.content = current_content
        breakdown.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Section updated successfully',
            'updated_content': current_content
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error updating section: {str(e)}'
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
            'ai_model_used': breakdown.ai_model_used,
            'document': {
                'extracted_text': breakdown.document.extracted_text,
                'status': breakdown.document.status
            }
        }
        
        return JsonResponse(status_data)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
def save_document(request, breakdown_id):
    """
    Save breakdown or report as a document file (PDF or Word) using Java.
    """
    try:
        breakdown = get_object_or_404(Breakdown, id=breakdown_id)
        data = json.loads(request.body)
        
        document_type = data.get('document_type')  # 'breakdown' or 'report'
        file_format = data.get('file_format')  # 'pdf' or 'docx'
        custom_filename = (data.get('filename') or '').strip()
        
        if not all([document_type, file_format]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: document_type or file_format'
            })
        
        # Get the original document name
        original_name = breakdown.document.title
        if '.' in original_name:
            original_name = original_name.rsplit('.', 1)[0]
        
        # Create filename based on type or use custom override (without extension)
        if custom_filename:
            import re as _re
            base = _re.sub(r'[^A-Za-z0-9._\- ]+', '', custom_filename)
            base = base.rsplit('.', 1)[0] if '.' in base else base
            filename = base or (original_name + ("_report" if document_type != 'breakdown' else "_breakdown"))
        else:
            if document_type == 'breakdown':
                filename = f"{original_name}_breakdown"
            else:  # report
                filename = f"{original_name}_report"
        
        # Add file extension
        if file_format == 'pdf':
            filename += '.pdf'
        else:  # docx
            filename += '.docx'
        
        # Prepare content for the document
        if document_type == 'breakdown':
            # Get breakdown content
            content = breakdown.content.get('sections', [])
            if not content:
                return JsonResponse({
                    'success': False,
                    'error': 'No breakdown content available to save'
                })
            
            # Format breakdown content
            document_content = f"BREAKDOWN REPORT: {breakdown.document.title}\n\n"
            for i, section in enumerate(content, 1):
                document_content += f"{i}. {section.get('title', f'Section {i}')}\n"
                document_content += f"{section.get('content', '')}\n\n"
                
        else:  # report
            # Get report content or generate it if not available
            if hasattr(breakdown, 'report_content') and breakdown.report_content:
                content = breakdown.report_content.get('sections', [])
            else:
                # Generate report content using AI
                from .ai_breakdown import AIBreakdownService
                ai_service = AIBreakdownService()
                report_result = ai_service.create_detailed_report(
                    breakdown.document.extracted_text,
                    str(breakdown.content)
                )
                content = report_result.get('sections', [])
            
            if not content:
                return JsonResponse({
                    'success': False,
                    'error': 'No report content available to save'
                })
            
            # Format report content
            document_content = f"COMPREHENSIVE REPORT: {breakdown.document.title}\n\n"
            for i, section in enumerate(content, 1):
                document_content += f"{i}. {section.get('title', f'Section {i}')}\n"
                document_content += f"{section.get('content', '')}\n\n"
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_documents')
        os.makedirs(output_dir, exist_ok=True)
        
        # Full output path
        output_path = os.path.join(output_dir, filename)
        
        # Call Java to generate the document
        try:
            java_result = call_java_document_generator(
                document_type, file_format, document_content, output_path
            )
            
            if java_result['success']:
                # Create a new Document record for the generated file
                generated_doc = Document.objects.create(
                    title=filename,
                    file_type=file_format.lower(),  # store lowercase to match choices
                    document_type=document_type,
                    status='completed',
                    uploaded_at=timezone.now(),
                    extracted_text=(
                        document_content[:1000] + "..."
                        if len(document_content) > 1000
                        else document_content
                    ),
                )
                
                # Copy the generated file to the document's file field
                with open(output_path, 'rb') as f:
                    generated_doc.file.save(filename, File(f), save=True)
                
                return JsonResponse({
                    'success': True,
                    'message': f'{document_type.title()} saved successfully as {filename}',
                    'filename': filename,
                    'file_format': file_format,
                    'document_type': document_type,
                    'download_url': generated_doc.file.url
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Java document generation failed: {java_result["error"]}'
                })
                
        except Exception as java_error:
            return JsonResponse({
                'success': False,
                'error': f'Error calling Java document generator: {str(java_error)}'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error saving document: {str(e)}'
        })


def call_java_document_generator(document_type, file_format, content, output_path):
    """
    Call the Java DocumentGenerator to create PDF or Word documents.
    
    Args:
        document_type: Type of document ('breakdown' or 'report')
        file_format: File format ('pdf' or 'docx')
        content: Document content to include
        output_path: Where to save the generated file
        
    Returns:
        Dict with success status and error message if any
    """
    try:
        import subprocess
        import tempfile
        
        # Create a temporary file with the content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(content)
            temp_content_path = temp_file.name
        
        # Path to the Java JAR file
        java_jar_path = os.path.join(settings.BASE_DIR, 'java_assets', 'DocumentGenerator.jar')
        
        # Check if JAR exists, if not, try to compile the Java file
        if not os.path.exists(java_jar_path):
            java_source_path = os.path.join(settings.BASE_DIR, 'java_assets', 'DocumentGenerator.java')
            if os.path.exists(java_source_path):
                # Try to compile the Java file
                compile_result = subprocess.run([
                    'javac', '-cp', 'java_assets/*', java_source_path
                ], capture_output=True, text=True, cwd=settings.BASE_DIR)
                
                if compile_result.returncode != 0:
                    return {
                        'success': False,
                        'error': f'Failed to compile Java source: {compile_result.stderr}'
                    }
                
                # Try to run the compiled class
                java_class_path = os.path.join(settings.BASE_DIR, 'java_assets')
                result = subprocess.run([
                    'java', '-cp', java_class_path, 'DocumentGenerator',
                    document_type, file_format, temp_content_path, output_path
                ], capture_output=True, text=True, cwd=settings.BASE_DIR)
            else:
                return {
                    'success': False,
                    'error': 'Java source file not found'
                }
        else:
            # Run the JAR file
            result = subprocess.run([
                'java', '-jar', java_jar_path,
                document_type, file_format, temp_content_path, output_path
            ], capture_output=True, text=True, cwd=settings.BASE_DIR)
        
        # Clean up temporary file
        try:
            os.unlink(temp_content_path)
        except:
            pass
        
        if result.returncode == 0:
            return {'success': True}
        else:
            return {
                'success': False,
                'error': f'Java execution failed: {result.stderr}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error calling Java: {str(e)}'
        }


@csrf_exempt
@require_http_methods(["POST"])
def generate_report(request, breakdown_id):
    """
    Generate a comprehensive report for the breakdown.
    """
    try:
        breakdown = get_object_or_404(Breakdown, id=breakdown_id)
        data = json.loads(request.body)
        
        extracted_text = data.get('extracted_text', '')
        breakdown_content = data.get('breakdown_content', '')
        
        # Use AI service to generate detailed report
        from .ai_breakdown import AIBreakdownService
        ai_service = AIBreakdownService()
        
        report_result = ai_service.create_detailed_report(
            extracted_text, breakdown_content
        )
        
        if report_result and report_result.get('sections'):
            return JsonResponse({
                'success': True,
                'report': report_result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate report content'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error generating report: {str(e)}'
        })
