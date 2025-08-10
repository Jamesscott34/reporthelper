"""
AI Breakdown Service

This module handles the communication with OpenRoute AI for breaking down documents
into step-by-step instructions.
"""

import requests
import json
import logging
import re
from django.conf import settings
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class AIBreakdownService:
    """
    Service class for handling AI-powered document breakdown using OpenRoute AI.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the AI breakdown service.
        
        Args:
            model_name: Name of the OpenRoute AI model to use
        """
        self.host = settings.OPENROUTE_HOST
        self.model = model_name or settings.OPENROUTE_MODELS['breakdown']
        # Use OpenRoute AI's OpenAI-compatible endpoints
        self.chat_url = f"{self.host}/chat/completions"
        self.completions_url = f"{self.host}/completions"
        self.models_url = f"{self.host}/models"
        
        # Determine which API key to use based on the model
        if 'deepseek' in self.model:
            self.api_key = settings.OPENROUTE_API_KEYS['deepseek']
        elif 'tngtech' in self.model:
            self.api_key = settings.OPENROUTE_API_KEYS['tngtech']
        elif 'openrouter' in self.model:
            self.api_key = settings.OPENROUTE_API_KEYS['openrouter']
        else:
            # Default to deepseek key
            self.api_key = settings.OPENROUTE_API_KEYS['deepseek']
    
    def _make_request(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Make a request to OpenRoute AI API with retry logic.
        
        Args:
            prompt: The prompt to send to the AI model
            max_retries: Maximum number of retry attempts
            
        Returns:
            The AI response or None if failed
        """
        for attempt in range(max_retries):
            try:
                logger.debug("Attempt %s/%s", attempt + 1, max_retries)
                logger.debug("API Key present: %s", bool(self.api_key))
                
                # Use chat completions endpoint for better results
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 8000,
                    "top_p": 0.9
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "http://localhost:8000",  # Required for OpenRoute
                    "X-Title": "AI Report Writer"  # Optional but recommended
                }
                
                logger.debug("POST %s model=%s", self.chat_url, self.model)
                logger.debug("Payload size: %s chars", len(str(payload)))
                
                response = requests.post(self.chat_url, json=payload, headers=headers, timeout=120)
                logger.debug("Response status: %s", response.status_code)
                
                if not response.ok:
                    logger.warning("HTTP error %s: %s", response.status_code, response.text)
                    response.raise_for_status()
                
                result = response.json()
                logger.debug("Response JSON keys: %s", list(result.keys()))
                
                # Extract response from chat completions format
                if 'choices' in result and len(result['choices']) > 0:
                    response_text = result['choices'][0].get('message', {}).get('content', '')
                else:
                    # Fallback to completions format
                    response_text = result.get('choices', [{}])[0].get('text', '')
                
                if response_text:
                    logger.debug("Received response len=%s", len(response_text))
                    return response_text
                else:
                    logger.debug("Empty response on attempt %s", attempt + 1)
                    logger.debug("Full response: %s", result)
                    
            except requests.exceptions.RequestException as e:
                logger.warning("Request failed on attempt %s: %s", attempt + 1, e)
                if attempt == max_retries - 1:
                    logger.error(f"Failed to make request to OpenRoute AI after {max_retries} attempts: {e}")
                    return None
            except json.JSONDecodeError as e:
                logger.warning("JSON decode failed on attempt %s: %s", attempt + 1, e)
                if attempt == max_retries - 1:
                    logger.error(f"Failed to parse OpenRoute AI response after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def run_freeform_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Send a freeform prompt to the configured AI model and return the raw text response.
        
        Args:
            prompt: The complete prompt to send to the AI
        
        Returns:
            Dict with success flag, response text (if any), and model name
        """
        try:
            response_text = self._make_request(prompt)
            if response_text:
                return {
                    'success': True,
                    'response': response_text,
                    'model_used': self.model
                }
            return {
                'success': False,
                'error': 'Empty response from AI model',
                'model_used': self.model
            }
        except Exception as exc:
            logger.error("Error running freeform prompt: %s", exc)
            return {
                'success': False,
                'error': str(exc),
                'model_used': self.model
            }

    def _load_step_by_step_prompt_template(self) -> Optional[str]:
        """
        Load the detailed step-by-step prompt template from the prompts folder.
        Returns the template text or None if not found.
        """
        try:
            from django.conf import settings as dj_settings
            import os
            template_path = os.path.join(
                dj_settings.BASE_DIR, 'prompts', 'step_by_step_prompt.txt'
            )
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as exc:
            logger.warning(
                "Failed to load step-by-step prompt template: %s", str(exc)
            )
            return None
    
    def _check_models_available(self) -> bool:
        """
        Check if the required models are available in OpenRoute AI.
        
        Returns:
            True if models are available, False otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8000"
            }
            response = requests.get(self.models_url, headers=headers, timeout=10)
            if response.status_code == 200:
                models = response.json()
                available_models = [model.get('id', '') for model in models.get('data', [])]
                logger.debug("Available models: %s", available_models)
                return self.model in available_models
            return False
        except Exception as e:
            logger.warning("Error checking models: %s", e)
            return False
    
    def breakdown_document(self, text: str) -> Dict[str, Any]:
        """
        Break down a document into step-by-step instructions.
        
        Args:
            text: The extracted text from the document
            
        Returns:
            Dictionary containing the breakdown and metadata
        """
        logger.info("Starting AI breakdown: chars=%s model=%s host=%s api_key=%s",
                    len(text), self.model, self.host, bool(self.api_key))
        
        # Check if models are available
        if not self._check_models_available():
            logger.warning("Model availability check failed, proceeding anyway")
        
        # Clean and prepare the text
        cleaned_text = self._clean_text(text)
        logger.debug("Cleaned text length: %s", len(cleaned_text))
        
        # Try different prompts for better results
        prompts = self._get_breakdown_prompts(cleaned_text)
        logger.debug("Generated %s prompts", len(prompts))
        
        for i, prompt in enumerate(prompts):
            logger.debug("Trying prompt %s/%s len=%s", i + 1, len(prompts), len(prompt))
            response = self._make_request(prompt)
            
            if response:
                logger.debug("Got response from prompt %s len=%s", i + 1, len(response))
                try:
                    breakdown_data = self._parse_breakdown_response(response)
                    if breakdown_data and breakdown_data.get('sections'):
                        logger.debug("Parsed breakdown with %s sections", len(breakdown_data['sections']))
                        return {
                            'success': True,
                            'breakdown': breakdown_data,
                            'raw_response': response,
                            'model_used': self.model,
                            'prompt_used': i + 1
                        }
                except Exception as e:
                    logger.warning("Failed to parse response from prompt %s: %s", i + 1, e)
                    continue
            else:
                logger.debug("No response from prompt %s", i + 1)
        
        # If all prompts fail, return a simple breakdown
        logger.warning("All prompts failed, creating simple breakdown")
        simple_breakdown = self._create_simple_breakdown(cleaned_text)
        
        return {
            'success': True,
            'breakdown': simple_breakdown,
            'raw_response': 'Simple breakdown created due to AI failure',
            'model_used': self.model,
            'prompt_used': 'fallback'
        }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and prepare text for AI processing.
        
        Args:
            text: Raw text from document
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might confuse the AI
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]]', '', text)
        
        # Increase max length to handle longer documents
        max_length = 32000  # Increased from 8000 to handle longer documents
        if len(text) > max_length:
            # Instead of truncating, try to keep the most important parts
            # Keep the beginning and end, remove middle parts
            first_part = text[:max_length//2]
            last_part = text[-(max_length//2):]
            text = first_part + "\n\n[Content continues...]\n\n" + last_part
            logger.debug("Document was truncated; new length=%s", len(text))
        
        return text.strip()
    
    def _get_breakdown_prompts(self, text: str) -> List[str]:
        """
        Generate multiple prompts for different breakdown approaches.
        
        Args:
            text: Cleaned text from document
            
        Returns:
            List of prompts to try
        """
        prompts = []
        
        # Prompt 1: Comprehensive structured breakdown
        prompt1 = f"""You are a content breakdown assistant. Your task is to take a full document and break it down completely into clear, detailed step-by-step instructions.

IMPORTANT: Analyze the ENTIRE document content. Do not skip any sections or topics.

Requirements:
- Use clear, numbered sections (1., 2., 3., etc.)
- Include ALL main topics and subtopics
- Break down complex sections into subsections
- Highlight key points, findings, and insights
- Maintain professional tone
- Be comprehensive - cover everything in the document
- Use bullet points for detailed breakdowns within sections

Example output format:
1. Project Overview
   - Main purpose and scope
   - Key objectives
   - Target audience

2. Technical Architecture
   - System components
   - Technology stack
   - Data flow

3. Implementation Details
   - Development approach
   - Key features
   - Technical specifications

4. Results and Outcomes
   - Achievements
   - Performance metrics
   - User feedback

5. Conclusion and Recommendations
   - Summary of findings
   - Next steps
   - Future improvements

Now, analyze the following COMPLETE document and create a comprehensive, detailed breakdown:

{text}

Please provide a complete, structured breakdown covering ALL content in the document:"""

        # Prompt 2: Detailed analysis with subsections
        prompt2 = f"""Create a comprehensive, detailed breakdown of this document.

Requirements:
- Analyze the ENTIRE document content
- Use numbered sections (1., 2., 3., etc.)
- Include subsections with bullet points
- Cover all topics, features, and details mentioned
- Maintain logical flow and structure
- Be thorough and complete

Document content:
{text}

Create a detailed, comprehensive breakdown covering everything:"""

        # Prompt 3: Executive summary with full coverage
        prompt3 = f"""Create a comprehensive breakdown of this document that covers ALL content.

Format:
1. Executive Summary: Main purpose, scope, and key findings
2. Detailed Analysis: Complete breakdown of all sections
3. Technical Details: All technical aspects and specifications
4. Implementation: All implementation details and approaches
5. Results: All outcomes, metrics, and achievements
6. Recommendations: All suggestions and next steps

Document:
{text}

Provide a comprehensive breakdown that covers EVERYTHING in the document:"""

        prompts.extend([prompt1, prompt2, prompt3])
        return prompts
    
    def _parse_breakdown_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the AI response into structured data.
        
        Args:
            response: Raw AI response
            
        Returns:
            Structured breakdown data
        """
        # Try to extract numbered sections
        sections = []
        
        # Look for numbered patterns (1., 2., etc.) - more comprehensive pattern
        numbered_pattern = r'(\d+\.\s*[^\n]+(?:\n(?!\d+\.)[^\n]*)*)'
        numbered_matches = re.findall(numbered_pattern, response, re.MULTILINE | re.DOTALL)
        
        if numbered_matches:
            for match in numbered_matches:
                section_text = match.strip()
                if len(section_text) > 10:  # Minimum section length
                    sections.append(section_text)
        
        # If no numbered sections, try bullet points
        if not sections:
            bullet_pattern = r'([•\-\*]\s*[^\n]+(?:\n(?![\•\-\*])[^\n]*)*)'
            bullet_matches = re.findall(bullet_pattern, response, re.MULTILINE | re.DOTALL)
            
            for match in bullet_matches:
                section_text = match.strip()
                if len(section_text) > 10:
                    sections.append(section_text)
        
        # If still no sections, split by paragraphs or lines that look like sections
        if not sections:
            # Look for lines that start with common section indicators
            section_indicators = ['Overview', 'Introduction', 'Background', 'Methodology', 'Results', 'Conclusion', 'Summary', 'Analysis', 'Implementation', 'Features', 'Architecture', 'Design', 'Development', 'Testing', 'Deployment']
            
            lines = response.split('\n')
            current_section = ""
            
            for line in lines:
                line = line.strip()
                if any(indicator.lower() in line.lower() for indicator in section_indicators) and len(line) > 5:
                    if current_section:
                        sections.append(current_section.strip())
                    current_section = line
                elif line and current_section:
                    current_section += "\n" + line
            
            if current_section:
                sections.append(current_section.strip())
        
        # If still no sections, split by paragraphs
        if not sections:
            paragraphs = [p.strip() for p in response.split('\n\n') if p.strip() and len(p.strip()) > 20]
            sections = paragraphs[:15]  # Increased limit to 15 sections
        
        # Ensure we have at least some content
        if not sections:
            sections = [response[:1000] + "..." if len(response) > 1000 else response]
        
        return {
            'sections': sections,
            'raw_response': response,
            'total_sections': len(sections)
        }
    
    def _create_simple_breakdown(self, text: str) -> Dict[str, Any]:
        """
        Create a simple breakdown when AI fails.
        
        Args:
            text: Cleaned text from document
            
        Returns:
            Simple breakdown structure
        """
        # Split text into paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip() and len(p.strip()) > 50]
        
        # Create simple sections
        sections = []
        for i, paragraph in enumerate(paragraphs[:8]):  # Limit to 8 sections
            sections.append(f"{i+1}. {paragraph[:200]}...")
        
        return {
            'sections': sections,
            'raw_response': 'Simple breakdown created automatically',
            'total_sections': len(sections)
        }
    
    def create_step_by_step_guide(self, breakdown_content: str) -> Dict[str, Any]:
        """
        Create comprehensive step-by-step instructions using the same approach as breakdown.
        
        Args:
            breakdown_content: The breakdown content to convert to detailed steps
            
        Returns:
            A comprehensive step-by-step guide structure with subsections
        """
        # Load the detailed, link-and-command-rich template from file
        template = self._load_step_by_step_prompt_template()
        if template:
            # Enforce auto-example and output-only policy for backend generation too
            prompt = template.replace('{INPUT_TEXT}', breakdown_content)
        else:
            # Minimal fallback (kept short to satisfy linters)
            prompt = (
                'Create a beginner-friendly, step-by-step guide with numbered '
                'steps, short explanations of why, and commands for Windows '
                '(PowerShell) and Linux/macOS (bash). Include verification '
                'checks, troubleshooting tips, config snippets, and official '
                'download links when relevant. Use markdown headings.\n\n'
                f'Input:\n{breakdown_content}'
            )

        try:
            response = self._make_request(prompt)
            if response:
                return self._parse_breakdown_response(response)
            return self._create_simple_step_by_step(breakdown_content)
        except Exception as e:
            logger.error("Error creating step-by-step guide: %s", e)
            return self._create_simple_step_by_step(breakdown_content)
    
    def _create_simple_step_by_step(self, content: str) -> Dict[str, Any]:
        """
        Create simple step-by-step instructions when AI fails.
        
        Args:
            content: The content to break into steps
            
        Returns:
            Simple step-by-step structure
        """
        # Split content into logical steps
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        steps = []
        for i, sentence in enumerate(sentences[:5]):  # Limit to 5 steps
            if len(sentence) > 20:  # Only include substantial sentences
                # Make it more action-oriented
                action = sentence.split()[0] if sentence.split() else 'Review'
                steps.append({
                    'title': f'Step {i + 1}: {action.title()}',
                    'content': sentence
                })
        
        return {
            'sections': steps,
            'raw_response': 'Simple step-by-step guide created automatically',
            'total_sections': len(steps)
        }
    
    def create_detailed_report(self, extracted_text: str, 
                              breakdown_content: str) -> Dict[str, Any]:
        """
        Create a comprehensive, detailed report reviewing the extracted 
        text and breakdown.
        
        Args:
            extracted_text: The original extracted text from the document
            breakdown_content: The AI-generated breakdown content
            
        Returns:
            A detailed report structure with references and image 
            placeholders
        """
        prompt = f"""
        Create a comprehensive, detailed report based on the following 
        information:

        EXTRACTED TEXT:
        {extracted_text[:2000]}

        BREAKDOWN CONTENT:
        {breakdown_content[:2000]}

        REQUIREMENTS:
        1. Create a professional, detailed report with no fluff or 
           repetition
        2. Remove all markdown formatting (no **, *, "", etc.)
        3. Break down each part into clear, detailed sections with 
           proper numbering
        4. Add reference numbers to each major section (e.g., 1.0, 
           1.1, 1.2, 2.0, etc.)
        5. Include image placeholders where relevant with descriptive 
           names (e.g., "Figure 1.1: Process Flow Diagram", "Image 2.3: 
           Data Structure Overview")
        6. Make the report fluid and well-structured with logical flow
        7. Focus on what was accomplished and the methodology used
        8. Include a summary of findings and recommendations
        9. Add cross-references between sections where appropriate
        10. Use clear, professional language without unnecessary jargon
        11. Length requirement: If the input explicitly requests a word count, 
            meet or exceed that amount. Otherwise, produce no fewer than 500 words. 
            Do not pad with filler; expand with concrete details, reasoning, and 
            examples tied to the input.

        STRUCTURE:
        - Executive Summary (1.0)
        - Document Overview and Scope (2.0)
        - Methodology and Approach (3.0)
        - Detailed Analysis and Breakdown (4.0)
          - Section 4.1: Content Analysis
          - Section 4.2: Key Components Identified
          - Section 4.3: Process Flow Analysis
        - Key Findings and Insights (5.0)
        - Recommendations and Next Steps (6.0)
        - References and Resources (7.0)

        For each section:
        - Provide comprehensive content that explains what was done
        - Include specific examples from the document
        - Add relevant image placeholders with descriptive names
        - Use clear numbering system for easy reference
        - Ensure logical flow between sections

        Output policy:
        - Do not restate these instructions or the input headers; output only the
          final report content that satisfies all requirements.

        Format the response as a structured report with sections 
        containing title and content. Each section should be 
        comprehensive and well-detailed.
        """
        
        try:
            response = self._make_request(prompt)
            if response:
                return self._parse_report_response(response)
            else:
                return self._create_simple_report(extracted_text, 
                                                breakdown_content)
        except Exception as e:
            logger.error(f"Error creating detailed report: {e}")
            return self._create_simple_report(extracted_text, 
                                            breakdown_content)
    
    def _parse_report_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the AI-generated report response into structured format.
        
        Args:
            response: The AI response to parse
            
        Returns:
            Parsed report structure
        """
        try:
            # Clean the response
            cleaned_response = self._clean_text(response)
            
            # Split into sections based on headers
            sections = []
            current_section = None
            current_content = []
            
            lines = cleaned_response.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this is a new section header
                if re.match(r'^\d+\.\s+', line) or re.match(r'^\d+\.\d+\s+', line) or line.isupper():
                    # Save previous section if exists
                    if current_section:
                        sections.append({
                            'title': current_section,
                            'content': '\n'.join(current_content).strip()
                        })
                    
                    # Start new section
                    current_section = line
                    current_content = []
                else:
                    if current_section:
                        current_content.append(line)
            
            # Add the last section
            if current_section and current_content:
                sections.append({
                    'title': current_section,
                    'content': '\n'.join(current_content).strip()
                })
            
            # Ensure we have at least some content; do not truncate so the UI shows everything
            if not sections:
                sections = [{
                    'title': 'Report Summary',
                    'content': cleaned_response
                }]
            
            return {
                'sections': sections,
                'raw_response': cleaned_response,
                'total_sections': len(sections)
            }
            
        except Exception as e:
            logger.error(f"Error parsing report response: {e}")
            return {
                'sections': [{'title': 'Report', 'content': response}],
                'raw_response': response,
                'total_sections': 1
            }
    
    def _create_simple_report(self, extracted_text: str, breakdown_content: str) -> Dict[str, Any]:
        """
        Create a simple report when AI fails.
        
        Args:
            extracted_text: The original extracted text
            breakdown_content: The breakdown content
            
        Returns:
            Simple report structure
        """
        sections = [
            {
                'title': '1.0 Executive Summary',
                'content': f'This report summarizes the analysis of the document containing {len(extracted_text)} characters of text.'
            },
            {
                'title': '2.0 Document Analysis',
                'content': f'The document was processed and broken down into {len(breakdown_content.split())} words of structured content.'
            },
            {
                'title': '3.0 Key Findings',
                'content': 'The document contains valuable information that has been organized into actionable sections for better understanding and implementation.'
            },
            {
                'title': '4.0 Recommendations',
                'content': 'Consider implementing the structured breakdown to improve workflow efficiency and understanding of the document content.'
            }
        ]
        
        return {
            'sections': sections,
            'raw_response': 'Simple report created automatically',
            'total_sections': len(sections)
        } 