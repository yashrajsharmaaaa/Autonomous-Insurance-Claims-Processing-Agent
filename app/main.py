"""
FastAPI application for FNOL claim processing.

This module provides the REST API endpoint for processing First Notice of Loss
documents. It orchestrates the complete processing pipeline: parsing, extraction,
validation, and routing.
"""

import tempfile
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.models import ProcessClaimResponse, ErrorResponse, ExtractedFields
from app.parser import (
    parse_document,
    EmptyDocumentError,
    CorruptedFileError,
    ParserError
)
from app.extractor import extract_fields, ExtractionError
from app.router_rules import identify_missing_fields, determine_route


# Initialize FastAPI application
app = FastAPI(
    title="FNOL Claim Processor",
    description="Automated processing of First Notice of Loss insurance claims",
    version="1.0.0"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model for JSON text input
class TextClaimRequest(BaseModel):
    """Request model for submitting claim text directly."""
    text: str


# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "FNOL Claim Processor",
        "status": "operational",
        "version": "1.0.0"
    }


@app.post(
    "/process-claim",
    response_model=ProcessClaimResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid input"},
        413: {"model": ErrorResponse, "description": "Payload Too Large"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        503: {"model": ErrorResponse, "description": "Service Unavailable"},
        504: {"model": ErrorResponse, "description": "Gateway Timeout"}
    },
    summary="Process FNOL claim document",
    description="Accept FNOL document (PDF/TXT file or JSON text) and return structured extraction with routing recommendation"
)
async def process_claim(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = None
):
    """
    Process an FNOL claim document and return structured data with routing decision.
    
    Accepts either:
    - File upload (PDF or TXT) via multipart/form-data
    - Raw text via JSON body with 'text' field
    
    Returns:
    - extractedFields: Structured data extracted from the document
    - missingFields: List of mandatory fields that are missing
    - recommendedRoute: Routing decision (FastTrack, ManualReview, Investigation, SpecialistQueue, Standard)
    - reasoning: Explanation for the routing decision
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 9.1, 9.3
    """
    
    raw_text = None
    temp_file_path = None
    
    try:
        # Validate input: must provide either file or text
        if file is None and text is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "MissingInput",
                    "message": "No file or text provided. Please upload a PDF/TXT file or provide text in JSON body."
                }
            )
        
        # Handle file upload
        if file is not None:
            # Validate file type
            # Requirements: 1.1, 1.2, 1.4
            file_extension = Path(file.filename).suffix.lower().strip('.')
            if file_extension not in ['pdf', 'txt']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "UnsupportedFileType",
                        "message": f"Unsupported file format: {file_extension}. Please upload PDF or TXT files only."
                    }
                )
            
            # Read file content
            file_content = await file.read()
            
            # Check file size
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "error": "FileTooLarge",
                        "message": f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024)}MB."
                    }
                )
            
            # Save to temporary file for parsing
            with tempfile.NamedTemporaryFile(
                mode='wb',
                suffix=f'.{file_extension}',
                delete=False
            ) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # Parse document to extract raw text
            # Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3
            try:
                raw_text = parse_document(temp_file_path, file_extension)
            except EmptyDocumentError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "EmptyDocument",
                        "message": str(e)
                    }
                )
            except CorruptedFileError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "CorruptedFile",
                        "message": str(e)
                    }
                )
            except ParserError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "ParsingError",
                        "message": str(e)
                    }
                )
        
        # Handle direct text input
        # Requirements: 1.3
        else:
            raw_text = text
            
            # Validate text is not empty
            if not raw_text or not raw_text.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "EmptyText",
                        "message": "Provided text is empty. Please provide valid FNOL document text."
                    }
                )
        
        # Extract structured fields from raw text
        # Requirements: 2.1-2.16, 5.1, 5.2, 5.3, 5.4, 5.5
        try:
            extracted_dict = extract_fields(raw_text)
            
            # Convert to Pydantic model for validation
            extracted_fields = ExtractedFields(**extracted_dict)
            
        except ExtractionError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "ExtractionError",
                    "message": "Field extraction service unavailable",
                    "details": str(e)
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "ExtractionError",
                    "message": "Failed to extract fields from document",
                    "details": str(e)
                }
            )
        
        # Identify missing mandatory fields
        # Requirements: 6.1, 6.2, 6.3, 6.4
        missing_fields = identify_missing_fields(extracted_fields)
        
        # Determine routing decision
        # Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6
        recommended_route, reasoning = determine_route(extracted_fields, missing_fields)
        
        # Build and return response
        # Requirements: 9.1, 9.2, 9.3, 9.4
        response = ProcessClaimResponse(
            extractedFields=extracted_fields,
            missingFields=missing_fields,
            recommendedRoute=recommended_route,
            reasoning=reasoning
        )
        
        return response
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "An unexpected error occurred during claim processing",
                "details": str(e)
            }
        )
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass  # Ignore cleanup errors


# Alternative endpoint for JSON text input
@app.post(
    "/process-claim-text",
    response_model=ProcessClaimResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid input"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        503: {"model": ErrorResponse, "description": "Service Unavailable"}
    },
    summary="Process FNOL claim text",
    description="Accept FNOL document text via JSON and return structured extraction with routing recommendation"
)
async def process_claim_text(request: TextClaimRequest):
    """
    Alternative endpoint that accepts claim text via JSON body.
    
    This is a convenience endpoint that delegates to the main process_claim endpoint.
    
    Requirements: 1.3
    """
    return await process_claim(file=None, text=request.text)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
