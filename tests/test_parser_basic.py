"""Basic tests for the parser module to verify implementation."""

import pytest
from pathlib import Path
import tempfile
import os
from app.parser import (
    parse_pdf,
    parse_txt,
    parse_document,
    EmptyDocumentError,
    CorruptedFileError,
    ParserError
)


def test_parse_txt_with_valid_content():
    """Test parsing a valid TXT file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("This is a test FNOL document.\nPolicy Number: 12345")
        temp_path = f.name
    
    try:
        result = parse_txt(temp_path)
        assert "This is a test FNOL document" in result
        assert "Policy Number: 12345" in result
    finally:
        os.unlink(temp_path)


def test_parse_txt_with_empty_file():
    """Test that empty TXT files raise EmptyDocumentError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("")
        temp_path = f.name
    
    try:
        with pytest.raises(EmptyDocumentError, match="Document contains no content"):
            parse_txt(temp_path)
    finally:
        os.unlink(temp_path)


def test_parse_txt_with_whitespace_only():
    """Test that whitespace-only files raise EmptyDocumentError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("   \n\n  \t  ")
        temp_path = f.name
    
    try:
        with pytest.raises(EmptyDocumentError, match="Document contains no content"):
            parse_txt(temp_path)
    finally:
        os.unlink(temp_path)


def test_parse_document_routes_to_txt():
    """Test that parse_document correctly routes TXT files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Test content")
        temp_path = f.name
    
    try:
        result = parse_document(temp_path, 'txt')
        assert "Test content" in result
    finally:
        os.unlink(temp_path)


def test_parse_document_with_unsupported_type():
    """Test that unsupported file types raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        parse_document("dummy.docx", "docx")


def test_parse_document_handles_extension_variations():
    """Test that file type parsing handles dots and case variations."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Test content")
        temp_path = f.name
    
    try:
        # Test with dot prefix
        result = parse_document(temp_path, '.txt')
        assert "Test content" in result
        
        # Test with uppercase
        result = parse_document(temp_path, 'TXT')
        assert "Test content" in result
    finally:
        os.unlink(temp_path)
