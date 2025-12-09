"""
Validation and routing logic for FNOL claims.

This module implements the business rules for validating claim completeness
and determining optimal routing paths based on claim characteristics.
Routing follows a strict priority order to ensure consistent classification.
"""

from typing import Optional
from app.models import ExtractedFields


# Define mandatory fields that must be present for standard processing
# Requirements: 6.4
MANDATORY_FIELDS = [
    "policyInformation.policyNumber",
    "policyInformation.policyholderName",
    "incidentInformation.date",
    "incidentInformation.description",
    "claimType",
    "assetDetails.estimatedDamage"
]

# Fraud keywords that trigger investigation route (case-insensitive)
# Requirements: 7.1
FRAUD_KEYWORDS = ["fraud", "inconsistent", "staged"]

# Fast-track threshold for estimated damage (USD)
# Requirements: 7.4, 7.6
FAST_TRACK_THRESHOLD = 25000.0


def identify_missing_fields(extracted: ExtractedFields) -> list[str]:
    """
    Identify mandatory fields that are missing or null in extracted data.
    
    Args:
        extracted: ExtractedFields object containing all extracted claim data
        
    Returns:
        List of field paths (e.g., "policyInformation.policyNumber") that are
        missing or null. Returns empty list if all mandatory fields are present.
        
    Requirements: 6.1, 6.2, 6.3
    """
    missing = []
    
    for field_path in MANDATORY_FIELDS:
        # Parse the field path to navigate nested objects
        parts = field_path.split(".")
        
        if len(parts) == 1:
            # Top-level field (e.g., "claimType")
            value = getattr(extracted, parts[0], None)
        elif len(parts) == 2:
            # Nested field (e.g., "policyInformation.policyNumber")
            parent = getattr(extracted, parts[0], None)
            if parent is None:
                value = None
            else:
                value = getattr(parent, parts[1], None)
        else:
            # Deeper nesting not expected in current schema
            value = None
        
        # Check if value is None or empty string
        if value is None or (isinstance(value, str) and value.strip() == ""):
            missing.append(field_path)
    
    return missing


def check_fraud_keywords(description: Optional[str]) -> bool:
    """
    Check if incident description contains fraud indicator keywords.
    
    Args:
        description: Incident description text (may be None)
        
    Returns:
        True if any fraud keyword is found (case-insensitive), False otherwise
        
    Requirements: 7.1
    """
    if description is None:
        return False
    
    # Convert to lowercase for case-insensitive matching
    description_lower = description.lower()
    
    # Check if any fraud keyword appears in the description
    return any(keyword in description_lower for keyword in FRAUD_KEYWORDS)


def determine_route(extracted: ExtractedFields, missing: list[str]) -> tuple[str, str]:
    """
    Determine the recommended routing decision based on claim characteristics.
    
    Applies routing rules in strict priority order:
    1. Investigation - if fraud keywords present
    2. ManualReview - if any mandatory field missing
    3. SpecialistQueue - if claim type is "injury"
    4. FastTrack - if estimated damage < $25,000
    5. Standard - default route
    
    Args:
        extracted: ExtractedFields object containing all extracted claim data
        missing: List of missing mandatory field paths
        
    Returns:
        Tuple of (route_name, reasoning) where:
        - route_name: One of "Investigation", "ManualReview", "SpecialistQueue", 
                     "FastTrack", or "Standard"
        - reasoning: Human-readable explanation (1-3 sentences) for the decision
        
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6
    """
    
    # Priority 1: Check for fraud keywords (Investigation route)
    # Requirements: 7.1, 8.3
    if check_fraud_keywords(extracted.incidentInformation.description):
        reasoning = (
            f"Claim flagged for investigation due to presence of fraud indicators "
            f"in the incident description. Manual review required to assess validity."
        )
        return "Investigation", reasoning
    
    # Priority 2: Check for missing mandatory fields (ManualReview route)
    # Requirements: 7.2, 8.4
    if missing:
        missing_list = ", ".join(missing)
        reasoning = (
            f"Claim requires manual review due to missing mandatory fields: {missing_list}. "
            f"Complete information is needed before processing can continue."
        )
        return "ManualReview", reasoning
    
    # Priority 3: Check for injury claim type (SpecialistQueue route)
    # Requirements: 7.3, 8.5
    if extracted.claimType and extracted.claimType.lower() == "injury":
        reasoning = (
            f"Claim routed to specialist queue due to injury claim type. "
            f"Specialized handling required for injury-related claims."
        )
        return "SpecialistQueue", reasoning
    
    # Priority 4: Check for low damage amount (FastTrack route)
    # IMPORTANT: Threshold is strictly less than $25,000 (not equal to)
    estimated_damage = extracted.assetDetails.estimatedDamage
    if estimated_damage is not None and estimated_damage < FAST_TRACK_THRESHOLD:
        reasoning = (
            f"Claim eligible for fast-track processing with estimated damage of "
            f"${estimated_damage:,.2f}, which is below the ${FAST_TRACK_THRESHOLD:,.2f} threshold."
        )
        return "FastTrack", reasoning
    
    # Priority 5: Default to Standard route
    # Requirements: 7.5, 8.1, 8.2
    reasoning = (
        f"Claim routed to standard processing queue. "
        f"No special conditions identified requiring alternative routing."
    )
    return "Standard", reasoning
