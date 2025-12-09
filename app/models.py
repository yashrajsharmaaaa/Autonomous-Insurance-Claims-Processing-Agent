"""
Pydantic data models for FNOL claim processing.

This module defines all data structures used throughout the FNOL Agent,
including request/response models and nested field structures.
All field names use camelCase for consistency.
"""

from typing import Optional
from pydantic import BaseModel, Field


class PolicyInformation(BaseModel):
    """Policy-related information extracted from FNOL documents."""
    
    policyNumber: Optional[str] = Field(
        None,
        description="Unique identifier for the insurance policy"
    )
    policyholderName: Optional[str] = Field(
        None,
        description="Name of the policyholder"
    )
    effectiveDates: Optional[str] = Field(
        None,
        description="Policy effective date range"
    )


class IncidentInformation(BaseModel):
    """Incident details extracted from FNOL documents."""
    
    date: Optional[str] = Field(
        None,
        description="Date when the incident occurred"
    )
    time: Optional[str] = Field(
        None,
        description="Time when the incident occurred"
    )
    location: Optional[str] = Field(
        None,
        description="Location where the incident occurred"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the incident"
    )


class InvolvedParties(BaseModel):
    """Information about parties involved in the claim."""
    
    claimant: Optional[str] = Field(
        None,
        description="Name of the claimant"
    )
    thirdParties: Optional[list[str]] = Field(
        None,
        description="List of third parties involved"
    )
    contactDetails: Optional[str] = Field(
        None,
        description="Contact information for involved parties"
    )


class AssetDetails(BaseModel):
    """Details about the asset involved in the claim."""
    
    assetType: Optional[str] = Field(
        None,
        description="Type of asset (e.g., vehicle, property)"
    )
    assetId: Optional[str] = Field(
        None,
        description="Unique identifier for the asset"
    )
    estimatedDamage: Optional[float] = Field(
        None,
        description="Estimated damage amount in USD"
    )


class ExtractedFields(BaseModel):
    """Complete set of fields extracted from an FNOL document."""
    
    policyInformation: PolicyInformation = Field(
        ...,
        description="Policy-related information"
    )
    incidentInformation: IncidentInformation = Field(
        ...,
        description="Incident details"
    )
    involvedParties: InvolvedParties = Field(
        ...,
        description="Information about involved parties"
    )
    assetDetails: AssetDetails = Field(
        ...,
        description="Asset details"
    )
    claimType: Optional[str] = Field(
        None,
        description="Type of claim (e.g., injury, property, liability)"
    )
    attachments: Optional[list[str]] = Field(
        None,
        description="List of attachment references"
    )
    initialEstimate: Optional[float] = Field(
        None,
        description="Initial estimate amount in USD"
    )


class ProcessClaimResponse(BaseModel):
    """Response model for the /process-claim endpoint."""
    
    extractedFields: ExtractedFields = Field(
        ...,
        description="Structured fields extracted from the FNOL document"
    )
    missingFields: list[str] = Field(
        ...,
        description="List of mandatory fields that are missing or null"
    )
    recommendedRoute: str = Field(
        ...,
        description="Recommended routing decision: FastTrack, ManualReview, Investigation, SpecialistQueue, or Standard"
    )
    reasoning: str = Field(
        ...,
        description="Human-readable explanation (1-3 sentences) for the routing decision"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(
        ...,
        description="Error type or category"
    )
    message: str = Field(
        ...,
        description="Human-readable error description"
    )
    details: Optional[str] = Field(
        None,
        description="Additional context or technical details"
    )
