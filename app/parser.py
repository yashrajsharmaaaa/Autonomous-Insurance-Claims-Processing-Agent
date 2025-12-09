"""Document parser module for FNOL documents.

This module handles parsing of PDF and TXT files to extract raw text content.
Supports error handling for empty files, corrupted files, and encoding issues.
"""

import pdfplumber
from pathlib import Path
from typing import Union


class ParserError(Exception):
    """Base exception for parser-related errors."""
    pass


class EmptyDocumentError(ParserError):
    """Raised when a document contains no extractable content."""
    pass


class CorruptedFileError(ParserError):
    """Raised when a file cannot be parsed due to corruption."""
    pass


def parse_pdf(file_path: Union[str, Path]) -> str:
    """Extract text from a PDF file using pdfplumber.
    
    Processes text-based PDFs (not scanned images requiring OCR).
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content as a string
        
    Raises:
        EmptyDocumentError: If the PDF contains no extractable text
        CorruptedFileError: If the PDF file is corrupted or cannot be parsed
        ParserError: For other parsing errors
        
    Requirements: 3.1, 3.2, 3.3
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            text_parts = []
            
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            if not text_parts:
                raise EmptyDocumentError("Document contains no extractable text")
            
            return "\n".join(text_parts)
            
    except EmptyDocumentError:
        raise
    except Exception as e:
        error_msg = f"Unable to parse PDF file: {str(e)}"
        raise CorruptedFileError(error_msg) from e


def parse_txt(file_path: Union[str, Path]) -> str:
    """Read text from a TXT file using standard file I/O.
    
    Implements encoding fallback: UTF-8 first, then latin-1.
    
    Args:
        file_path: Path to the TXT file
        
    Returns:
        File content as a string
        
    Raises:
        EmptyDocumentError: If the file contains no content
        ParserError: For file reading errors
        
    Requirements: 4.1, 4.2, 4.3
    """
    try:
        # Try UTF-8 first, fallback to latin-1 for legacy files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        if not content or not content.strip():
            raise EmptyDocumentError("Document contains no content")
        
        return content
        
    except EmptyDocumentError:
        raise
    except Exception as e:
        error_msg = f"Unable to read TXT file: {str(e)}"
        raise ParserError(error_msg) from e


def parse_document(file_path: Union[str, Path], file_type: str) -> str:
    """Route to appropriate parser based on file type.
    
    Main entry point for document parsing. Normalizes file type and
    delegates to the appropriate parser.
    
    Args:
        file_path: Path to the document file
        file_type: File type/extension (e.g., 'pdf', 'txt')
        
    Returns:
        Extracted text content as a string
        
    Raises:
        ValueError: If file type is not supported
        EmptyDocumentError: If the document contains no content
        CorruptedFileError: If the file is corrupted
        ParserError: For other parsing errors
        
    Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3
    """
    file_type = file_type.lower().strip('.')
    
    if file_type == 'pdf':
        return parse_pdf(file_path)
    elif file_type == 'txt':
        return parse_txt(file_path)
    else:
        raise ValueError(
            f"Unsupported file format: {file_type}. "
            "Please upload PDF or TXT files only."
        )
