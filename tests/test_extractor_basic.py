"""Basic tests for the extractor module."""

import pytest
from app.extractor import extract_fields_heuristic, extract_fields, GeminiAPIError


def test_heuristic_extraction_with_complete_fnol():
    """Test heuristic extraction with a complete FNOL document."""
    fnol_text = """
    Policy Number: ABC123456
    Policyholder: John Smith
    
    Incident Date: 12/15/2023
    Incident Time: 2:30 PM
    Location: 123 Main Street, Springfield
    Description: Vehicle collision at intersection
    
    Claimant: John Smith
    Contact: 555-1234
    
    Claim Type: property
    Asset Type: Vehicle
    VIN: 1HGBH41JXMN109186
    Estimated Damage: $5,000.00
    """
    
    result = extract_fields_heuristic(fnol_text)
    
    # Verify policy information
    assert result["policyInformation"]["policyNumber"] == "ABC123456"
    assert result["policyInformation"]["policyholderName"] == "John Smith"
    
    # Verify incident information
    assert result["incidentInformation"]["date"] == "12/15/2023"
    assert result["incidentInformation"]["time"] == "2:30 PM"
    assert result["incidentInformation"]["location"] == "123 Main Street, Springfield"
    assert "collision" in result["incidentInformation"]["description"].lower()
    
    # Verify involved parties
    assert result["involvedParties"]["claimant"] == "John Smith"
    assert result["involvedParties"]["contactDetails"] == "555-1234"
    
    # Verify asset details
    assert result["assetDetails"]["assetType"] == "Vehicle"
    assert result["assetDetails"]["assetId"] == "1HGBH41JXMN109186"
    assert result["assetDetails"]["estimatedDamage"] == 5000.0
    
    # Verify claim type
    assert result["claimType"] == "property"


def test_heuristic_extraction_with_missing_fields():
    """Test heuristic extraction handles missing fields gracefully."""
    fnol_text = """
    Policy Number: XYZ789
    Incident Date: 01/20/2024
    Description: Minor fender bender
    """
    
    result = extract_fields_heuristic(fnol_text)
    
    # Should extract what's available
    assert result["policyInformation"]["policyNumber"] == "XYZ789"
    assert result["incidentInformation"]["date"] == "01/20/2024"
    assert "fender bender" in result["incidentInformation"]["description"].lower()
    
    # Missing fields should be None
    assert result["policyInformation"]["policyholderName"] is None
    assert result["incidentInformation"]["time"] is None
    assert result["assetDetails"]["estimatedDamage"] is None


def test_heuristic_extraction_with_empty_text():
    """Test heuristic extraction with empty text returns all nulls."""
    result = extract_fields_heuristic("")
    
    # All fields should be None
    assert result["policyInformation"]["policyNumber"] is None
    assert result["incidentInformation"]["date"] is None
    assert result["assetDetails"]["estimatedDamage"] is None


def test_extract_fields_falls_back_to_heuristic():
    """Test that extract_fields falls back to heuristic when Gemini unavailable."""
    fnol_text = """
    Policy Number: TEST123
    Incident Date: 03/01/2024
    Estimated Damage: $1,500
    """
    
    # This should fall back to heuristic if GEMINI_API_KEY is not set
    result = extract_fields(fnol_text)
    
    # Should have extracted something
    assert result is not None
    assert isinstance(result, dict)
    assert "policyInformation" in result
    assert "incidentInformation" in result


def test_heuristic_handles_various_date_formats():
    """Test heuristic extraction handles different date formats."""
    test_cases = [
        ("Incident Date: 12/15/2023", "12/15/2023"),
        ("Date of Incident: 12-15-2023", "12-15-2023"),
        ("Loss Date: 01/05/2024", "01/05/2024"),
    ]
    
    for text, expected_date in test_cases:
        result = extract_fields_heuristic(text)
        assert result["incidentInformation"]["date"] == expected_date


def test_heuristic_handles_currency_formats():
    """Test heuristic extraction handles different currency formats."""
    test_cases = [
        ("Estimated Damage: $5,000.00", 5000.0),
        ("Damage: $25000", 25000.0),
        ("Loss Amount: 1500.50", 1500.5),
    ]
    
    for text, expected_amount in test_cases:
        result = extract_fields_heuristic(text)
        assert result["assetDetails"]["estimatedDamage"] == expected_amount
