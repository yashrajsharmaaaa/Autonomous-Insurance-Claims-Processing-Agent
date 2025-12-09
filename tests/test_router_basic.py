"""
Basic unit tests for router_rules module.

Tests the core routing logic functions to ensure they work correctly
with various claim scenarios.
"""

import pytest
from app.models import (
    ExtractedFields,
    PolicyInformation,
    IncidentInformation,
    InvolvedParties,
    AssetDetails
)
from app.router_rules import (
    identify_missing_fields,
    check_fraud_keywords,
    determine_route,
    MANDATORY_FIELDS
)


def create_complete_claim(
    policy_number: str = "POL123",
    policyholder_name: str = "John Doe",
    incident_date: str = "2024-01-15",
    incident_description: str = "Minor fender bender",
    claim_type: str = "property",
    estimated_damage: float = 5000.0
) -> ExtractedFields:
    """Helper function to create a complete claim with all mandatory fields."""
    return ExtractedFields(
        policyInformation=PolicyInformation(
            policyNumber=policy_number,
            policyholderName=policyholder_name,
            effectiveDates="2023-01-01 to 2024-01-01"
        ),
        incidentInformation=IncidentInformation(
            date=incident_date,
            time="14:30",
            location="Main St and 5th Ave",
            description=incident_description
        ),
        involvedParties=InvolvedParties(
            claimant="John Doe",
            thirdParties=["Jane Smith"],
            contactDetails="555-1234"
        ),
        assetDetails=AssetDetails(
            assetType="vehicle",
            assetId="VIN123456",
            estimatedDamage=estimated_damage
        ),
        claimType=claim_type,
        attachments=["photo1.jpg"],
        initialEstimate=5000.0
    )


class TestIdentifyMissingFields:
    """Tests for identify_missing_fields function."""
    
    def test_no_missing_fields(self):
        """Test that complete claim returns empty list."""
        claim = create_complete_claim()
        missing = identify_missing_fields(claim)
        assert missing == []
    
    def test_missing_policy_number(self):
        """Test detection of missing policy number."""
        claim = create_complete_claim(policy_number=None)
        missing = identify_missing_fields(claim)
        assert "policyInformation.policyNumber" in missing
    
    def test_missing_policyholder_name(self):
        """Test detection of missing policyholder name."""
        claim = create_complete_claim(policyholder_name=None)
        missing = identify_missing_fields(claim)
        assert "policyInformation.policyholderName" in missing
    
    def test_missing_incident_date(self):
        """Test detection of missing incident date."""
        claim = create_complete_claim(incident_date=None)
        missing = identify_missing_fields(claim)
        assert "incidentInformation.date" in missing
    
    def test_missing_incident_description(self):
        """Test detection of missing incident description."""
        claim = create_complete_claim(incident_description=None)
        missing = identify_missing_fields(claim)
        assert "incidentInformation.description" in missing
    
    def test_missing_claim_type(self):
        """Test detection of missing claim type."""
        claim = create_complete_claim(claim_type=None)
        missing = identify_missing_fields(claim)
        assert "claimType" in missing
    
    def test_missing_estimated_damage(self):
        """Test detection of missing estimated damage."""
        claim = create_complete_claim(estimated_damage=None)
        missing = identify_missing_fields(claim)
        assert "assetDetails.estimatedDamage" in missing
    
    def test_multiple_missing_fields(self):
        """Test detection of multiple missing fields."""
        claim = create_complete_claim(
            policy_number=None,
            incident_date=None,
            claim_type=None
        )
        missing = identify_missing_fields(claim)
        assert len(missing) == 3
        assert "policyInformation.policyNumber" in missing
        assert "incidentInformation.date" in missing
        assert "claimType" in missing


class TestCheckFraudKeywords:
    """Tests for check_fraud_keywords function."""
    
    def test_fraud_keyword_present(self):
        """Test detection of 'fraud' keyword."""
        assert check_fraud_keywords("This looks like fraud to me") is True
    
    def test_inconsistent_keyword_present(self):
        """Test detection of 'inconsistent' keyword."""
        assert check_fraud_keywords("The story is inconsistent") is True
    
    def test_staged_keyword_present(self):
        """Test detection of 'staged' keyword."""
        assert check_fraud_keywords("This accident was staged") is True
    
    def test_case_insensitive_matching(self):
        """Test that keyword matching is case-insensitive."""
        assert check_fraud_keywords("FRAUD detected") is True
        assert check_fraud_keywords("Inconsistent details") is True
        assert check_fraud_keywords("STAGED accident") is True
    
    def test_no_fraud_keywords(self):
        """Test that normal descriptions return False."""
        assert check_fraud_keywords("Minor fender bender") is False
        assert check_fraud_keywords("Rear-end collision") is False
    
    def test_none_description(self):
        """Test that None description returns False."""
        assert check_fraud_keywords(None) is False


class TestDetermineRoute:
    """Tests for determine_route function."""
    
    def test_investigation_route_for_fraud(self):
        """Test that fraud keywords trigger Investigation route."""
        claim = create_complete_claim(
            incident_description="This looks like fraud"
        )
        missing = identify_missing_fields(claim)
        route, reasoning = determine_route(claim, missing)
        
        assert route == "Investigation"
        assert "fraud" in reasoning.lower()
    
    def test_manual_review_for_missing_fields(self):
        """Test that missing fields trigger ManualReview route."""
        claim = create_complete_claim(policy_number=None)
        missing = identify_missing_fields(claim)
        route, reasoning = determine_route(claim, missing)
        
        assert route == "ManualReview"
        assert "policyInformation.policyNumber" in reasoning
    
    def test_specialist_queue_for_injury(self):
        """Test that injury claims trigger SpecialistQueue route."""
        claim = create_complete_claim(claim_type="injury")
        missing = identify_missing_fields(claim)
        route, reasoning = determine_route(claim, missing)
        
        assert route == "SpecialistQueue"
        assert "injury" in reasoning.lower()
    
    def test_fast_track_for_low_damage(self):
        """Test that low damage triggers FastTrack route."""
        claim = create_complete_claim(estimated_damage=10000.0)
        missing = identify_missing_fields(claim)
        route, reasoning = determine_route(claim, missing)
        
        assert route == "FastTrack"
        assert "10,000" in reasoning or "10000" in reasoning
    
    def test_standard_route_default(self):
        """Test that claims with no special conditions get Standard route."""
        claim = create_complete_claim(
            claim_type="property",
            estimated_damage=30000.0
        )
        missing = identify_missing_fields(claim)
        route, reasoning = determine_route(claim, missing)
        
        assert route == "Standard"
    
    def test_boundary_exactly_25000_not_fast_track(self):
        """Test that exactly $25,000 damage is NOT fast-track."""
        claim = create_complete_claim(estimated_damage=25000.0)
        missing = identify_missing_fields(claim)
        route, reasoning = determine_route(claim, missing)
        
        assert route == "Standard"
    
    def test_priority_fraud_over_missing_fields(self):
        """Test that fraud takes priority over missing fields."""
        claim = create_complete_claim(
            policy_number=None,
            incident_description="This is fraud"
        )
        missing = identify_missing_fields(claim)
        route, reasoning = determine_route(claim, missing)
        
        assert route == "Investigation"
    
    def test_priority_missing_over_injury(self):
        """Test that missing fields take priority over injury."""
        claim = create_complete_claim(
            policy_number=None,
            claim_type="injury"
        )
        missing = identify_missing_fields(claim)
        route, reasoning = determine_route(claim, missing)
        
        assert route == "ManualReview"
    
    def test_priority_injury_over_fast_track(self):
        """Test that injury takes priority over fast-track."""
        claim = create_complete_claim(
            claim_type="injury",
            estimated_damage=5000.0
        )
        missing = identify_missing_fields(claim)
        route, reasoning = determine_route(claim, missing)
        
        assert route == "SpecialistQueue"
