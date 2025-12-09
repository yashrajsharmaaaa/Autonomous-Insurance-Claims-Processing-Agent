"""PDF parsing tests for the parser module."""

import pytest
from pathlib import Path
from app.parser import parse_pdf, parse_document, EmptyDocumentError, CorruptedFileError


def test_parse_pdf_with_nonexistent_file():
    """Test that parsing a non-existent PDF raises CorruptedFileError."""
    with pytest.raises(CorruptedFileError):
        parse_pdf("nonexistent_file.pdf")


def test_parse_document_routes_to_pdf():
    """Test that parse_document correctly identifies PDF file type."""
    # This test verifies the routing logic without requiring an actual PDF
    # We expect it to attempt PDF parsing and fail with CorruptedFileError
    # since the file doesn't exist
    with pytest.raises(CorruptedFileError):
        parse_document("test.pdf", "pdf")


def test_parse_document_handles_pdf_extension_variations():
    """Test that PDF file type parsing handles dots and case variations."""
    # Test with dot prefix
    with pytest.raises(CorruptedFileError):
        parse_document("test.pdf", ".pdf")
    
    # Test with uppercase
    with pytest.raises(CorruptedFileError):
        parse_document("test.pdf", "PDF")
