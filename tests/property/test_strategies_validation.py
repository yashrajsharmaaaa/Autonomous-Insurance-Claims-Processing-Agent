"""
Validation tests for Hypothesis strategies.

These tests verify that the strategies generate valid data that conforms
to the expected schemas and constraints.
"""

import pytest
from hypothesis import given, settings
from tests.property.strategies import (
    policy_numbers,
    person_names,
    dates,
    times,
    locations,
    claim_types,
    damage_amounts,
    low_damage_amounts,
    high_damage_amounts,
    descriptions_without_fraud,
    descriptions_with_fraud,
    extracted_fields_objects,
    fraud_claims,
    incomplete_claims,
    injury_claims,
    fast_track_claims,
    standard_claims,
    fnol_text,
    field_sets_with_missing_mandatory
)
from app.models import ExtractedFields
from app.router_rules import FRAUD_KEYWORDS, FAST_TRACK_THRESHOLD


class TestBasicStrategies:
    """Test basic building block strategies."""
    
    @given(policy_numbers())
    @settings(max_examples=10)
    def test_policy_numbers_format(self, policy_num):
        """Policy numbers should be non-empty strings."""
        assert isinstance(policy_num, str)
        assert len(policy_num) > 0
        assert "-" in policy_num
    
    @given(person_names())
    @settings(max_examples=10)
    def test_person_names_format(self, name):
        """Person names should contain first and last name."""
        assert isinstance(name, str)
        assert " " in name
        parts = name.split()
        assert len(parts) >= 2
    
    @given(dates())
    @settings(max_examples=10)
    def test_dates_format(self, date_str):
        """Dates should be non-empty strings."""
        assert isinstance(date_str, str)
        assert len(date_str) > 0
    
    @given(claim_types())
    @settings(max_examples=10)
    def test_claim_types_valid(self, claim_type):
        """Claim types should be from valid set."""
        assert isinstance(claim_type, str)
        assert claim_type in ["injury", "property", "liability", "collision", "comprehensive", "theft", "vandalism"]


class TestDamageAmountStrategies:
    """Test damage amount strategies."""
    
    @given(damage_amounts())
    @settings(max_examples=20)
    def test_damage_amounts_positive(self, amount):
        """Damage amounts should be positive numbers."""
        assert isinstance(amount, float)
        assert amount >= 0
    
    @given(low_damage_amounts())
    @settings(max_examples=20)
    def test_low_damage_below_threshold(self, amount):
        """Low damage amounts should be strictly below threshold."""
        assert isinstance(amount, float)
        assert amount < FAST_TRACK_THRESHOLD
    
    @given(high_damage_amounts())
    @settings(max_examples=20)
    def test_high_damage_at_or_above_threshold(self, amount):
        """High damage amounts should be at or above threshold."""
        assert isinstance(amount, float)
        assert amount >= FAST_TRACK_THRESHOLD


class TestDescriptionStrategies:
    """Test description strategies."""
    
    @given(descriptions_without_fraud())
    @settings(max_examples=20)
    def test_descriptions_without_fraud_no_keywords(self, desc):
        """Descriptions without fraud should not contain fraud keywords."""
        assert isinstance(desc, str)
        assert len(desc) > 0
        desc_lower = desc.lower()
        for keyword in FRAUD_KEYWORDS:
            assert keyword not in desc_lower
    
    @given(descriptions_with_fraud())
    @settings(max_examples=20)
    def test_descriptions_with_fraud_has_keywords(self, desc):
        """Descriptions with fraud should contain at least one fraud keyword."""
        assert isinstance(desc, str)
        assert len(desc) > 0
        desc_lower = desc.lower()
        has_keyword = any(keyword in desc_lower for keyword in FRAUD_KEYWORDS)
        assert has_keyword


class TestExtractedFieldsStrategies:
    """Test extracted fields strategies."""
    
    @given(extracted_fields_objects(allow_missing=False))
    @settings(max_examples=10)
    def test_extracted_fields_complete(self, fields):
        """Complete extracted fields should have all mandatory fields."""
        assert isinstance(fields, ExtractedFields)
        assert fields.policyInformation.policyNumber is not None
        assert fields.policyInformation.policyholderName is not None
        assert fields.incidentInformation.date is not None
        assert fields.incidentInformation.description is not None
        assert fields.claimType is not None
        assert fields.assetDetails.estimatedDamage is not None
    
    @given(fraud_claims())
    @settings(max_examples=10)
    def test_fraud_claims_have_keywords(self, fields):
        """Fraud claims should contain fraud keywords in description."""
        assert isinstance(fields, ExtractedFields)
        desc = fields.incidentInformation.description
        assert desc is not None
        desc_lower = desc.lower()
        has_keyword = any(keyword in desc_lower for keyword in FRAUD_KEYWORDS)
        assert has_keyword
    
    @given(injury_claims())
    @settings(max_examples=10)
    def test_injury_claims_have_injury_type(self, fields):
        """Injury claims should have claim type 'injury'."""
        assert isinstance(fields, ExtractedFields)
        assert fields.claimType == "injury"
    
    @given(fast_track_claims())
    @settings(max_examples=10)
    def test_fast_track_claims_low_damage(self, fields):
        """Fast track claims should have damage below threshold."""
        assert isinstance(fields, ExtractedFields)
        assert fields.assetDetails.estimatedDamage is not None
        assert fields.assetDetails.estimatedDamage < FAST_TRACK_THRESHOLD
        assert fields.claimType != "injury"
    
    @given(standard_claims())
    @settings(max_examples=10)
    def test_standard_claims_high_damage(self, fields):
        """Standard claims should have damage at or above threshold."""
        assert isinstance(fields, ExtractedFields)
        assert fields.assetDetails.estimatedDamage is not None
        assert fields.assetDetails.estimatedDamage >= FAST_TRACK_THRESHOLD
        assert fields.claimType != "injury"


class TestFNOLTextStrategy:
    """Test FNOL text generation strategy."""
    
    @given(fnol_text())
    @settings(max_examples=10)
    def test_fnol_text_format(self, text):
        """FNOL text should contain key sections."""
        assert isinstance(text, str)
        assert len(text) > 0
        assert "FIRST NOTICE OF LOSS" in text
        assert "POLICY INFORMATION" in text
        assert "INCIDENT INFORMATION" in text


class TestMissingFieldsStrategy:
    """Test missing fields strategy."""
    
    @given(field_sets_with_missing_mandatory())
    @settings(max_examples=10)
    def test_missing_fields_has_missing(self, data):
        """Field sets should have at least one missing mandatory field."""
        fields, expected_missing = data
        assert isinstance(fields, ExtractedFields)
        assert isinstance(expected_missing, list)
        assert len(expected_missing) > 0
        
        # Verify at least one field is actually None
        has_none = False
        for field_path in expected_missing:
            parts = field_path.split(".")
            if len(parts) == 1:
                if getattr(fields, parts[0], None) is None:
                    has_none = True
            elif len(parts) == 2:
                parent = getattr(fields, parts[0], None)
                if parent is None or getattr(parent, parts[1], None) is None:
                    has_none = True
        
        assert has_none, "At least one mandatory field should be None"
