"""
Utility functions for the breakdown app.

This module contains helper functions for text extraction and file processing.
"""

import os
import PyPDF2
from docx import Document as DocxDocument
import logging
import subprocess
import tempfile
import shutil

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
        print(f"Extracting text from {file_path} (type: {file_type})")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
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
        print(f"Error extracting text from {file_path}: {e}")
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
            print(f"PDF has {len(pdf_reader.pages)} pages")
            
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {i+1} ---\n{page_text}\n"
                else:
                    print(f"Warning: No text extracted from page {i+1}")
        
        text = text.strip()
        if not text:
            raise Exception("No text could be extracted from PDF")
        
        print(f"Successfully extracted {len(text)} characters from PDF")
        return text
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
        
        # Extract text from paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text += cell.text + "\n"
        
        text = text.strip()
        if not text:
            raise Exception("No text could be extracted from DOCX")
        
        print(f"Successfully extracted {len(text)} characters from DOCX")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {e}")
        raise


def extract_text_from_doc(file_path: str) -> str:
    """
    Extract text from a DOC file using LibreOffice conversion.
    
    Args:
        file_path: Path to the DOC file
        
    Returns:
        Extracted text content
    """
    try:
        # Create a temporary directory for conversion
        temp_dir = tempfile.mkdtemp()
        temp_docx = os.path.join(temp_dir, "converted.docx")
        
        # Convert DOC to DOCX using LibreOffice
        cmd = [
            'libreoffice', '--headless', '--convert-to', 'docx',
            '--outdir', temp_dir, file_path
        ]
        
        print(f"Converting DOC to DOCX using command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise Exception(f"LibreOffice conversion failed: {result.stderr}")
        
        # Check if conversion was successful
        if not os.path.exists(temp_docx):
            # Try to find the converted file with a different name
            converted_files = [f for f in os.listdir(temp_dir) if f.endswith('.docx')]
            if converted_files:
                temp_docx = os.path.join(temp_dir, converted_files[0])
            else:
                raise Exception("DOC to DOCX conversion failed - no output file found")
        
        # Extract text from the converted DOCX
        text = extract_text_from_docx(temp_docx)
        
        # Clean up temporary files
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return text
    except subprocess.TimeoutExpired:
        raise Exception("DOC conversion timed out")
    except Exception as e:
        logger.error(f"Error extracting text from DOC {file_path}: {e}")
        # Clean up temporary files
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from a TXT file.
    
    Args:
        file_path: Path to the TXT file
        
    Returns:
        Extracted text content
    """
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    text = file.read()
                    if text.strip():
                        print(f"Successfully extracted {len(text)} characters from TXT using {encoding} encoding")
                        return text.strip()
            except UnicodeDecodeError:
                continue
        
        raise Exception("Could not decode TXT file with any supported encoding")
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