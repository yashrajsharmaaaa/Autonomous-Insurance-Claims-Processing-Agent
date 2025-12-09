# Property-Based Testing Strategies

This directory contains Hypothesis strategies for property-based testing of the FNOL claim processor.

## Available Strategies

### Basic Building Blocks
- `policy_numbers()` - Generate realistic policy numbers
- `person_names()` - Generate person names
- `dates()` - Generate date strings in various formats
- `times()` - Generate time strings
- `locations()` - Generate location strings
- `phone_numbers()` - Generate phone numbers
- `asset_ids()` - Generate asset IDs (VIN, serial numbers)

### Claim Types
- `claim_types()` - Generate valid claim types (injury, property, liability, etc.)

### Damage Amounts
- `damage_amounts()` - Generate random damage amounts including boundary values
- `low_damage_amounts()` - Generate amounts strictly below $25,000 threshold
- `high_damage_amounts()` - Generate amounts at or above $25,000 threshold

### Descriptions
- `descriptions()` - Generate incident descriptions (with optional fraud control)
- `descriptions_without_fraud()` - Generate descriptions without fraud keywords
- `descriptions_with_fraud()` - Generate descriptions containing fraud keywords

### Extracted Fields
- `extracted_fields_objects()` - Generate complete ExtractedFields instances
  - Supports controlling missing fields, fraud keywords, damage amounts, and claim types
- `extracted_fields_dicts()` - Generate ExtractedFields as dictionaries

### Specialized Routing Scenarios
- `fraud_claims()` - Generate claims that should route to Investigation
- `incomplete_claims()` - Generate claims that should route to ManualReview
- `injury_claims()` - Generate claims that should route to SpecialistQueue
- `fast_track_claims()` - Generate claims that should route to FastTrack
- `standard_claims()` - Generate claims that should route to Standard

### FNOL Documents
- `fnol_text()` - Generate realistic FNOL document text

### Missing Fields
- `field_sets_with_missing_mandatory()` - Generate ExtractedFields with at least one missing mandatory field

## Usage Example

```python
from hypothesis import given
from tests.property.strategies import fraud_claims, fast_track_claims
from app.router_rules import determine_route, identify_missing_fields

@given(fraud_claims())
def test_fraud_routing(claim):
    """Fraud claims should always route to Investigation."""
    missing = identify_missing_fields(claim)
    route, reasoning = determine_route(claim, missing)
    assert route == "Investigation"
    assert any(keyword in reasoning.lower() for keyword in ["fraud", "investigation"])

@given(fast_track_claims())
def test_fast_track_routing(claim):
    """Low damage claims should route to FastTrack."""
    missing = identify_missing_fields(claim)
    route, reasoning = determine_route(claim, missing)
    assert route == "FastTrack"
    assert claim.assetDetails.estimatedDamage < 25000
```

## Validation

Run `pytest tests/property/test_strategies_validation.py` to verify all strategies generate valid data.
