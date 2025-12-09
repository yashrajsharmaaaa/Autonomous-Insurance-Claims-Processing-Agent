"""Field extractor module for FNOL documents.

This module handles extraction of structured fields from raw FNOL text using
Google Gemini API with fallback to heuristic-based extraction.
"""

import os
import json
import re
from typing import Optional
import google.generativeai as genai


class ExtractionError(Exception):
    """Base exception for extraction-related errors."""
    pass


class GeminiAPIError(ExtractionError):
    """Raised when Gemini API fails."""
    pass


def _configure_gemini() -> Optional[genai.GenerativeModel]:
    """Configure and return Gemini API client.
    
    Uses gemini-1.5-flash model for cost-effective extraction.
    
    Returns:
        Configured GenerativeModel instance or None if API key not available
        
    Requirements: 5.1, 5.5
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')


def extract_fields_with_gemini(text: str) -> dict:
    """Use Gemini to extract structured fields from FNOL text.
    
    Sends structured prompt requesting JSON extraction. Uses temperature=0
    for deterministic results. Handles markdown-wrapped JSON responses.
    
    Args:
        text: Raw FNOL document text
        
    Returns:
        Dictionary containing extracted fields (null for missing fields)
        
    Raises:
        GeminiAPIError: If Gemini API is unavailable or returns invalid JSON
                       
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    model = _configure_gemini()
    if not model:
        raise GeminiAPIError("GEMINI_API_KEY environment variable not set")
    
    # Create structured prompt for field extraction
    prompt = f"""Extract the following fields from this FNOL (First Notice of Loss) document and return ONLY valid JSON.

Required JSON structure:
{{
  "policyInformation": {{
    "policyNumber": "string or null",
    "policyholderName": "string or null",
    "effectiveDates": "string or null"
  }},
  "incidentInformation": {{
    "date": "string or null",
    "time": "string or null",
    "location": "string or null",
    "description": "string or null"
  }},
  "involvedParties": {{
    "claimant": "string or null",
    "thirdParties": ["string"] or null,
    "contactDetails": "string or null"
  }},
  "assetDetails": {{
    "assetType": "string or null",
    "assetId": "string or null",
    "estimatedDamage": number or null
  }},
  "claimType": "string or null",
  "attachments": ["string"] or null,
  "initialEstimate": number or null
}}

Rules:
- Use null for any field you cannot find in the document
- Do not invent or guess values
- Use exact field names as shown (camelCase)
- For monetary values (estimatedDamage, initialEstimate), extract only the numeric value without currency symbols
- For thirdParties and attachments, use null if not found, or an array of strings if found
- Return only JSON, no additional text or markdown formatting

Document text:
{text}
"""
    
    try:
        # Generate response with timeout
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0,  # Deterministic extraction
                max_output_tokens=2048,
            ),
            request_options={'timeout': 25}
        )
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            # Remove ```json or ``` at start and ``` at end
            response_text = re.sub(r'^```(?:json)?\s*\n', '', response_text)
            response_text = re.sub(r'\n```\s*$', '', response_text)
        
        # Parse JSON
        extracted = json.loads(response_text)
        return extracted
        
    except json.JSONDecodeError as e:
        raise GeminiAPIError(f"Invalid JSON response from Gemini: {str(e)}")
    except Exception as e:
        raise GeminiAPIError(f"Gemini API error: {str(e)}")


def extract_fields_heuristic(text: str) -> dict:
    """Fallback regex/keyword-based extraction.
    
    This is a simple heuristic approach that looks for common patterns
    in FNOL documents. Less accurate than LLM extraction but provides
    graceful degradation.
    
    Args:
        text: Raw FNOL document text
        
    Returns:
        Dictionary containing extracted fields (many may be null)
    """
    # Initialize structure with all nulls
    extracted = {
        "policyInformation": {
            "policyNumber": None,
            "policyholderName": None,
            "effectiveDates": None
        },
        "incidentInformation": {
            "date": None,
            "time": None,
            "location": None,
            "description": None
        },
        "involvedParties": {
            "claimant": None,
            "thirdParties": None,
            "contactDetails": None
        },
        "assetDetails": {
            "assetType": None,
            "assetId": None,
            "estimatedDamage": None
        },
        "claimType": None,
        "attachments": None,
        "initialEstimate": None
    }
    
    # Policy number patterns
    policy_patterns = [
        r'Policy\s*(?:Number|#|No\.?)[\s:]+([A-Z0-9-]+)',
        r'Policy[\s:]+([A-Z0-9-]+)',
    ]
    for pattern in policy_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["policyInformation"]["policyNumber"] = match.group(1).strip()
            break
    
    # Policyholder name
    name_patterns = [
        r'Policyholder[\s:]+([A-Za-z\s]+?)(?:\n|,|Policy)',
        r'Insured[\s:]+([A-Za-z\s]+?)(?:\n|,)',
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["policyInformation"]["policyholderName"] = match.group(1).strip()
            break
    
    # Incident date patterns
    date_patterns = [
        r'(?:Incident|Loss|Accident)\s*Date[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Date\s*of\s*(?:Incident|Loss|Accident)[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # Generic date
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["incidentInformation"]["date"] = match.group(1).strip()
            break
    
    # Incident time
    time_patterns = [
        r'(?:Incident|Loss|Accident)\s*Time[\s:]+(\d{1,2}:\d{2}(?:\s*[AP]M)?)',
        r'Time[\s:]+(\d{1,2}:\d{2}(?:\s*[AP]M)?)',
    ]
    for pattern in time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["incidentInformation"]["time"] = match.group(1).strip()
            break
    
    # Location
    location_patterns = [
        r'Location[\s:]+([^\n]+)',
        r'(?:Incident|Accident)\s*Location[\s:]+([^\n]+)',
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["incidentInformation"]["location"] = match.group(1).strip()
            break
    
    # Description (look for description section)
    desc_patterns = [
        r'Description[\s:]+([^\n]+(?:\n(?!\w+:)[^\n]+)*)',
        r'Incident\s*Description[\s:]+([^\n]+(?:\n(?!\w+:)[^\n]+)*)',
    ]
    for pattern in desc_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["incidentInformation"]["description"] = match.group(1).strip()
            break
    
    # Claimant
    claimant_patterns = [
        r'Claimant[\s:]+([A-Za-z\s]+?)(?:\n|,)',
    ]
    for pattern in claimant_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["involvedParties"]["claimant"] = match.group(1).strip()
            break
    
    # Contact details
    contact_patterns = [
        r'Contact[\s:]+([^\n]+)',
        r'Phone[\s:]+([^\n]+)',
        r'Email[\s:]+([^\n]+)',
    ]
    for pattern in contact_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["involvedParties"]["contactDetails"] = match.group(1).strip()
            break
    
    # Estimated damage (look for currency amounts)
    damage_patterns = [
        r'Estimated\s*Damage[\s:]+\$?([\d,]+(?:\.\d{2})?)',
        r'Damage[\s:]+\$?([\d,]+(?:\.\d{2})?)',
        r'Loss\s*Amount[\s:]+\$?([\d,]+(?:\.\d{2})?)',
    ]
    for pattern in damage_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                extracted["assetDetails"]["estimatedDamage"] = float(amount_str)
            except ValueError:
                pass
            break
    
    # Claim type
    claim_type_patterns = [
        r'Claim\s*Type[\s:]+([A-Za-z]+)',
        r'Type\s*of\s*Claim[\s:]+([A-Za-z]+)',
    ]
    for pattern in claim_type_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["claimType"] = match.group(1).strip().lower()
            break
    
    # Asset type
    asset_patterns = [
        r'Asset\s*Type[\s:]+([^\n]+)',
        r'Vehicle\s*Type[\s:]+([^\n]+)',
    ]
    for pattern in asset_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["assetDetails"]["assetType"] = match.group(1).strip()
            break
    
    # Asset ID (VIN, license plate, etc.)
    asset_id_patterns = [
        r'(?:VIN|Vehicle\s*ID)[\s:]+([A-Z0-9]+)',
        r'License\s*Plate[\s:]+([A-Z0-9-]+)',
        r'Asset\s*ID[\s:]+([A-Z0-9-]+)',
    ]
    for pattern in asset_id_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["assetDetails"]["assetId"] = match.group(1).strip()
            break
    
    return extracted


def extract_fields(text: str) -> dict:
    """Main extraction function with fallback logic.
    
    Attempts to extract fields using Gemini API first, then falls back
    to heuristic extraction if Gemini is unavailable or fails.
    
    Args:
        text: Raw FNOL document text
        
    Returns:
        Dictionary containing extracted fields in the defined schema
        
    Raises:
        ExtractionError: If both Gemini and heuristic extraction fail
    """
    # Try Gemini first
    try:
        return extract_fields_with_gemini(text)
    except GeminiAPIError:
        # Fall back to heuristic extraction
        pass
    
    # Use heuristic fallback
    try:
        return extract_fields_heuristic(text)
    except Exception as e:
        raise ExtractionError(f"All extraction methods failed: {str(e)}")
