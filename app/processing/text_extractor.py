"""Text extraction from various file formats for VisioLearn"""

import PyPDF2
from docx import Document
from pathlib import Path
from typing import Optional


class TextExtractionError(Exception):
    """Raised when text extraction fails"""
    pass


def extract_pdf(file_path: str) -> str:
    """
    Extract text from PDF file
    
    Args:
        file_path: Full path to PDF file
        
    Returns:
        Extracted text content
        
    Raises:
        TextExtractionError: If extraction fails
    """
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        raise TextExtractionError(f"Failed to extract text from PDF: {str(e)}")


def extract_docx(file_path: str) -> str:
    """
    Extract text from DOCX file
    
    Args:
        file_path: Full path to DOCX file
        
    Returns:
        Extracted text content
        
    Raises:
        TextExtractionError: If extraction fails
    """
    try:
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text.strip()
    except Exception as e:
        raise TextExtractionError(f"Failed to extract text from DOCX: {str(e)}")


def extract_txt(file_path: str) -> str:
    """
    Extract text from plain text file
    
    Args:
        file_path: Full path to TXT file
        
    Returns:
        File content as string
        
    Raises:
        TextExtractionError: If extraction fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as txt_file:
            return txt_file.read().strip()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as txt_file:
                return txt_file.read().strip()
        except Exception as e:
            raise TextExtractionError(f"Failed to read text file: {str(e)}")
    except Exception as e:
        raise TextExtractionError(f"Failed to extract text from TXT: {str(e)}")


def extract_from_file(file_path: str) -> str:
    """
    Extract text from file based on file extension
    
    Args:
        file_path: Full path to file
        
    Returns:
        Extracted text content
        
    Raises:
        TextExtractionError: If file type not supported or extraction fails
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    
    if extension == '.pdf':
        return extract_pdf(file_path)
    elif extension in ['.docx', '.doc']:
        return extract_docx(file_path)
    elif extension == '.txt':
        return extract_txt(file_path)
    else:
        raise TextExtractionError(f"Unsupported file type: {extension}")


def sanitize_text(text: str) -> str:
    """
    Sanitize extracted text by removing extra whitespace, fixing encoding issues
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    text = '\n'.join(lines)
    
    # Replace multiple spaces with single space
    text = ' '.join(text.split())
    
    return text
