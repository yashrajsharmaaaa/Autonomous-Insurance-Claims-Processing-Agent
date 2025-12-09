"""Integration tests for extractor with Pydantic models."""

import pytest
from app.extractor import extract_fields_heuristic
from app.models import ExtractedFields, PolicyInformation, IncidentInformation, InvolvedParties, AssetDetails


def test_extracted_fields_validate_with_pydantic():
    """Test that heuristic extraction output validates with Pydantic models."""
    fnol_text = """
    Policy Number: ABC123456
    Policyholder: Jane Doe
    
    Incident Date: 11/20/2023
    Incident Time: 10:15 AM
    Location: 456 Oak Avenue, Portland
    Description: Rear-end collision on highway
    
    Claimant: Jane Doe
    Contact: jane.doe@email.com
    
    Claim Type: injury
    Asset Type: Vehicle
    VIN: 5YJSA1E14HF123456
    Estimated Damage: $12,500.00
    """
    
    # Extract fields
    extracted_dict = extract_fields_heuristic(fnol_text)
    
    # Validate with Pydantic models
    policy_info = PolicyInformation(**extracted_dict["policyInformation"])
    incident_info = IncidentInformation(**extracted_dict["incidentInformation"])
    involved_parties = InvolvedParties(**extracted_dict["involvedParties"])
    asset_details = AssetDetails(**extracted_dict["assetDetails"])
    
    # Create full ExtractedFields model
    extracted_fields = ExtractedFields(
        policyInformation=policy_info,
        incidentInformation=incident_info,
        involvedParties=involved_parties,
        assetDetails=asset_details,
        claimType=extracted_dict["claimType"],
        attachments=extracted_dict["attachments"],
        initialEstimate=extracted_dict["initialEstimate"]
    )
    
    # Verify the model was created successfully
    assert extracted_fields.policyInformation.policyNumber == "ABC123456"
    assert extracted_fields.incidentInformation.date == "11/20/2023"
    assert extracted_fields.assetDetails.estimatedDamage == 12500.0
    assert extracted_fields.claimType == "injury"


def test_extracted_fields_with_nulls_validate():
    """Test that extraction with many null fields still validates."""
    fnol_text = """
    Policy Number: MIN123
    Incident Date: 05/10/2024
    """
    
    extracted_dict = extract_fields_heuristic(fnol_text)
    
    # Should validate even with many null fields
    extracted_fields = ExtractedFields(
        policyInformation=PolicyInformation(**extracted_dict["policyInformation"]),
        incidentInformation=IncidentInformation(**extracted_dict["incidentInformation"]),
        involvedParties=InvolvedParties(**extracted_dict["involvedParties"]),
        assetDetails=AssetDetails(**extracted_dict["assetDetails"]),
        claimType=extracted_dict["claimType"],
        attachments=extracted_dict["attachments"],
        initialEstimate=extracted_dict["initialEstimate"]
    )
    
    # Verify extracted fields
    assert extracted_fields.policyInformation.policyNumber == "MIN123"
    assert extracted_fields.incidentInformation.date == "05/10/2024"
    
    # Verify null fields
    assert extracted_fields.policyInformation.policyholderName is None
    assert extracted_fields.assetDetails.estimatedDamage is None
