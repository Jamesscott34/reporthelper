"""
AI Breakdown Service

This module handles the communication with Ollama for breaking down documents
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
    
    def _make_request(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Make a request to Ollama API with retry logic.
        
        Args:
            prompt: The prompt to send to the AI model
            max_retries: Maximum number of retry attempts
            
        Returns:
            The AI response or None if failed
        """
        for attempt in range(max_retries):
            try:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 4000
                    }
                }
                
                print(f"Making request to {self.base_url} with model {self.model}")
                response = requests.post(self.base_url, json=payload, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                response_text = result.get('response', '')
                
                if response_text:
                    print(f"Successfully received response ({len(response_text)} characters)")
                    return response_text
                else:
                    print(f"Empty response received on attempt {attempt + 1}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to make request to Ollama after {max_retries} attempts: {e}")
                    return None
            except json.JSONDecodeError as e:
                print(f"JSON decode failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to parse Ollama response after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def breakdown_document(self, text: str) -> Dict[str, Any]:
        """
        Break down a document into step-by-step instructions.
        
        Args:
            text: The extracted text from the document
            
        Returns:
            Dictionary containing the breakdown and metadata
        """
        print(f"Starting AI breakdown of document ({len(text)} characters)")
        
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
        
        # Limit text length to prevent token overflow
        max_length = 8000
        if len(text) > max_length:
            text = text[:max_length] + "... [truncated]"
        
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
        
        # Prompt 1: Structured breakdown
        prompt1 = f"""You are a content breakdown assistant. Your task is to take a full document and break it down clearly step-by-step.

Use numbered or bullet point format. Avoid AI tone. Keep it clear, short, and professional.

Example output format:
1. Introduction: Describes the project background
2. Methodology: Outlines data collection
3. Results: Summarizes findings
4. Conclusion: Provides final recommendations

Now, analyze the following text and create a structured breakdown:

{text}

Please provide a clear, structured breakdown with numbered sections:"""

        # Prompt 2: Detailed analysis
        prompt2 = f"""Analyze this document and create a comprehensive step-by-step breakdown.

Requirements:
- Use clear, numbered sections
- Include main topics and subtopics
- Highlight key points and findings
- Maintain professional tone
- Focus on actionable insights

Document content:
{text}

Create a detailed breakdown:"""

        # Prompt 3: Executive summary style
        prompt3 = f"""Create an executive summary breakdown of this document.

Format:
1. Overview: Main purpose and scope
2. Key Points: Important findings and insights
3. Methodology: How the work was conducted
4. Results: Main outcomes and conclusions
5. Recommendations: Suggested next steps

Document:
{text}

Provide an executive summary breakdown:"""

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
        
        # Look for numbered patterns (1., 2., etc.)
        numbered_pattern = r'(\d+\.\s*[^\n]+(?:\n(?!\d+\.)[^\n]*)*)'
        numbered_matches = re.findall(numbered_pattern, response, re.MULTILINE)
        
        if numbered_matches:
            for match in numbered_matches:
                section_text = match.strip()
                if len(section_text) > 10:  # Minimum section length
                    sections.append(section_text)
        
        # If no numbered sections, try bullet points
        if not sections:
            bullet_pattern = r'([•\-\*]\s*[^\n]+(?:\n(?![\•\-\*])[^\n]*)*)'
            bullet_matches = re.findall(bullet_pattern, response, re.MULTILINE)
            
            for match in bullet_matches:
                section_text = match.strip()
                if len(section_text) > 10:
                    sections.append(section_text)
        
        # If still no sections, split by paragraphs
        if not sections:
            paragraphs = [p.strip() for p in response.split('\n\n') if p.strip() and len(p.strip()) > 20]
            sections = paragraphs[:10]  # Limit to 10 sections
        
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