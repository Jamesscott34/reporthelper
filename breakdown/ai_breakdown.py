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
                
                print(f"Making request to {self.chat_url} with model {self.model}")
                response = requests.post(self.chat_url, json=payload, headers=headers, timeout=120)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract response from chat completions format
                if 'choices' in result and len(result['choices']) > 0:
                    response_text = result['choices'][0].get('message', {}).get('content', '')
                else:
                    # Fallback to completions format
                    response_text = result.get('choices', [{}])[0].get('text', '')
                
                if response_text:
                    print(f"Successfully received response ({len(response_text)} characters)")
                    return response_text
                else:
                    print(f"Empty response received on attempt {attempt + 1}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to make request to OpenRoute AI after {max_retries} attempts: {e}")
                    return None
            except json.JSONDecodeError as e:
                print(f"JSON decode failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to parse OpenRoute AI response after {max_retries} attempts: {e}")
                    return None
        
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
                print(f"Available models: {available_models}")
                return self.model in available_models
            return False
        except Exception as e:
            print(f"Error checking models: {e}")
            return False
    
    def breakdown_document(self, text: str) -> Dict[str, Any]:
        """
        Break down a document into step-by-step instructions.
        
        Args:
            text: The extracted text from the document
            
        Returns:
            Dictionary containing the breakdown and metadata
        """
        print(f"Starting AI breakdown of document ({len(text)} characters)")
        
        # Check if models are available
        if not self._check_models_available():
            print("Warning: Model availability check failed, proceeding anyway...")
        
        # Clean and prepare the text
        cleaned_text = self._clean_text(text)
        
        # Try different prompts for better results
        prompts = self._get_breakdown_prompts(cleaned_text)
        
        for i, prompt in enumerate(prompts):
            print(f"Trying prompt {i+1}/{len(prompts)}")
            response = self._make_request(prompt)
            
            if response:
                try:
                    breakdown_data = self._parse_breakdown_response(response)
                    if breakdown_data and breakdown_data.get('sections'):
                        print(f"Successfully parsed breakdown with {len(breakdown_data['sections'])} sections")
                        return {
                            'success': True,
                            'breakdown': breakdown_data,
                            'raw_response': response,
                            'model_used': self.model,
                            'prompt_used': i + 1
                        }
                except Exception as e:
                    print(f"Failed to parse response from prompt {i+1}: {e}")
                    continue
        
        # If all prompts fail, return a simple breakdown
        print("All prompts failed, creating simple breakdown")
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
            print(f"Document was {len(text)} characters, truncated to {len(text)} characters")
        
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