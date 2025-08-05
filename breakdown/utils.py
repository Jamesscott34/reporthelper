"""
Utility functions for the breakdown app.

This module contains helper functions for text extraction and file processing.
"""

import os
import PyPDF2
from docx import Document as DocxDocument
import logging

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: str, file_type: str) -> str:
    """
    Extract text from a file based on its type.
    
    Args:
        file_path: Path to the file
        file_type: Type of the file (pdf, docx, doc, txt)
        
    Returns:
        Extracted text content
    """
    try:
        if file_type.lower() == 'pdf':
            return extract_text_from_pdf(file_path)
        elif file_type.lower() == 'docx':
            return extract_text_from_docx(file_path)
        elif file_type.lower() == 'doc':
            return extract_text_from_doc(file_path)
        elif file_type.lower() == 'txt':
            return extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        raise


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {e}")
        raise


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text content
    """
    try:
        doc = DocxDocument(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {e}")
        raise


def extract_text_from_doc(file_path: str) -> str:
    """
    Extract text from a DOC file.
    
    Args:
        file_path: Path to the DOC file
        
    Returns:
        Extracted text content
    """
    # For DOC files, we'll need to use a different approach
    # This is a placeholder - you might want to use python-docx2txt or similar
    try:
        # Try to convert DOC to DOCX first, then extract
        # This is a simplified approach - you might want to use a more robust solution
        import subprocess
        import tempfile
        
        # Create a temporary file for the converted DOCX
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            tmp_docx_path = tmp_file.name
        
        try:
            # Use LibreOffice to convert DOC to DOCX
            subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'docx',
                '--outdir', os.path.dirname(tmp_docx_path),
                file_path
            ], check=True)
            
            # Extract text from the converted DOCX
            text = extract_text_from_docx(tmp_docx_path)
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_docx_path):
                os.unlink(tmp_docx_path)
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOC {file_path}: {e}")
        # Fallback: return a message about DOC conversion
        return f"[DOC file detected - conversion failed: {str(e)}]"


def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from a TXT file.
    
    Args:
        file_path: Path to the TXT file
        
    Returns:
        Extracted text content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error extracting text from TXT {file_path}: {e}")
            raise
    except Exception as e:
        logger.error(f"Error extracting text from TXT {file_path}: {e}")
        raise


def validate_file_type(file_name: str) -> bool:
    """
    Validate if the file type is supported.
    
    Args:
        file_name: Name of the file
        
    Returns:
        True if file type is supported, False otherwise
    """
    allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
    file_extension = os.path.splitext(file_name)[1].lower()
    return file_extension in allowed_extensions


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in MB
    """
    return os.path.getsize(file_path) / (1024 * 1024) 