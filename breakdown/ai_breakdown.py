"""
AI Breakdown Service

This module handles the communication with Ollama for breaking down documents
into step-by-step instructions.
"""

import requests
import json
import logging
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AIBreakdownService:
    """
    Service class for handling AI-powered document breakdown.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the AI breakdown service.
        
        Args:
            model_name: Name of the Ollama model to use
        """
        self.host = settings.OLLAMA_HOST
        self.model = model_name or settings.OLLAMA_MODELS['breakdown']
        self.base_url = f"{self.host}/api/generate"
    
    def _make_request(self, prompt: str) -> Optional[str]:
        """
        Make a request to Ollama API.
        
        Args:
            prompt: The prompt to send to the AI model
            
        Returns:
            The AI response or None if failed
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to make request to Ollama: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Ollama response: {e}")
            return None
    
    def breakdown_document(self, text: str) -> Dict[str, Any]:
        """
        Break down a document into step-by-step instructions.
        
        Args:
            text: The extracted text from the document
            
        Returns:
            Dictionary containing the breakdown and metadata
        """
        prompt = self._get_breakdown_prompt(text)
        
        response = self._make_request(prompt)
        
        if not response:
            return {
                'success': False,
                'error': 'Failed to get response from AI model',
                'breakdown': None
            }
        
        # Try to parse the response as structured data
        try:
            # Look for JSON-like structure in the response
            breakdown_data = self._parse_breakdown_response(response)
        except Exception as e:
            logger.warning(f"Failed to parse structured response: {e}")
            breakdown_data = {
                'sections': [response],
                'raw_response': response
            }
        
        return {
            'success': True,
            'breakdown': breakdown_data,
            'raw_response': response,
            'model_used': self.model
        }
    
    def _get_breakdown_prompt(self, text: str) -> str:
        """
        Generate the breakdown prompt for the AI model.
        
        Args:
            text: The document text to break down
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a content breakdown assistant.

Your task is to take a full document (academic, report, project brief, etc.) and break it down clearly step-by-step. Use numbered or bullet point format.

Avoid AI tone. Keep it clear, short, and professional.

Example output:
1. Introduction: Describes the project background.
2. Methodology: Outlines data collection.
3. Results: Summarizes findings.

Now, analyze the following text:
{text}

Please provide a structured breakdown with clear sections and subsections."""
        
        return prompt
    
    def _parse_breakdown_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the AI response into structured data.
        
        Args:
            response: Raw AI response
            
        Returns:
            Structured breakdown data
        """
        # Try to extract structured sections from the response
        sections = []
        current_section = None
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for numbered or bulleted items
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or \
               line.startswith(('-', '•', '*', '→')):
                
                # Extract section title and content
                if ':' in line:
                    title, content = line.split(':', 1)
                    title = title.strip().lstrip('123456789.-•*→ ')
                    content = content.strip()
                else:
                    title = line.strip().lstrip('123456789.-•*→ ')
                    content = ""
                
                sections.append({
                    'title': title,
                    'content': content,
                    'type': 'section'
                })
            elif current_section and line:
                # Add content to current section
                if sections:
                    sections[-1]['content'] += f" {line}"
        
        return {
            'sections': sections,
            'raw_response': response
        } 