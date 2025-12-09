"""
Hypothesis strategies for property-based testing of FNOL claim processor.

This module provides strategies for generating random test data including:
- FNOL document text with varying field combinations
- Extracted field dictionaries with controlled field presence
- Damage amounts including boundary values
- Claim types and fraud keywords
- Field sets with missing mandatory fields

These strategies are used by property-based tests to verify universal
properties across a wide range of inputs.
"""

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from typing import Optional
from app.models import (
    PolicyInformation,
    IncidentInformation,
    InvolvedParties,
    AssetDetails,
    ExtractedFields
)
from app.router_rules import MANDATORY_FIELDS, FRAUD_KEYWORDS, FAST_TRACK_THRESHOLD


# ============================================================================
# Basic Building Blocks
# ============================================================================

@st.composite
def policy_numbers(draw) -> str:
    """Generate realistic policy numbers."""
    prefix = draw(st.sampled_from(["POL", "INS", "CLM", "P"]))
    number = draw(st.integers(min_value=100000, max_value=999999))
    return f"{prefix}-{number}"


@st.composite
def person_names(draw) -> str:
    """Generate realistic person names."""
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    first = draw(st.sampled_from(first_names))
    last = draw(st.sampled_from(last_names))
    return f"{first} {last}"


@st.composite
def dates(draw) -> str:
    """Generate realistic date strings in various formats."""
    year = draw(st.integers(min_value=2020, max_value=2024))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))  # Safe for all months
    
    format_choice = draw(st.integers(min_value=0, max_value=2))
    if format_choice == 0:
        return f"{month:02d}/{day:02d}/{year}"
    elif format_choice == 1:
        return f"{year}-{month:02d}-{day:02d}"
    else:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{months[month-1]} {day}, {year}"


@st.composite
def times(draw) -> str:
    """Generate realistic time strings."""
    hour = draw(st.integers(min_value=0, max_value=23))
    minute = draw(st.integers(min_value=0, max_value=59))
    
    format_choice = draw(st.booleans())
    if format_choice:
        # 24-hour format
        return f"{hour:02d}:{minute:02d}"
    else:
        # 12-hour format
        period = "AM" if hour < 12 else "PM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{minute:02d} {period}"


@st.composite
def locations(draw) -> str:
    """Generate realistic location strings."""
    streets = ["Main St", "Oak Ave", "Elm St", "Park Blvd", "Washington St", "Maple Dr"]
    cities = ["Springfield", "Portland", "Austin", "Denver", "Seattle", "Boston"]
    states = ["CA", "TX", "NY", "FL", "IL", "WA", "CO", "MA"]
    
    street_num = draw(st.integers(min_value=100, max_value=9999))
    street = draw(st.sampled_from(streets))
    city = draw(st.sampled_from(cities))
    state = draw(st.sampled_from(states))
    
    return f"{street_num} {street}, {city}, {state}"


@st.composite
def phone_numbers(draw) -> str:
    """Generate realistic phone numbers."""
    area = draw(st.integers(min_value=200, max_value=999))
    prefix = draw(st.integers(min_value=200, max_value=999))
    line = draw(st.integers(min_value=1000, max_value=9999))
    return f"({area}) {prefix}-{line}"


@st.composite
def asset_ids(draw) -> str:
    """Generate realistic asset IDs (e.g., VIN, serial numbers)."""
    prefix = draw(st.sampled_from(["VIN", "SN", "ID", "REG"]))
    number = draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd")), min_size=8, max_size=12))
    return f"{prefix}{number}"


# ============================================================================
# Claim Type Strategy
# ============================================================================

def claim_types() -> SearchStrategy[str]:
    """
    Generate random claim types.
    
    Includes "injury" as a special case for routing logic, plus other common types.
    """
    return st.sampled_from([
        "injury",
        "property",
        "liability",
        "collision",
        "comprehensive",
        "theft",
        "vandalism"
    ])


# ============================================================================
# Damage Amount Strategies
# ============================================================================

def damage_amounts() -> SearchStrategy[float]:
    """
    Generate random damage amounts including boundary values.
    
    Includes values around the fast-track threshold ($25,000) to test
    boundary conditions in routing logic.
    """
    return st.one_of(
        # Values well below threshold
        st.floats(min_value=100.0, max_value=10000.0),
        # Values near threshold (below)
        st.floats(min_value=24000.0, max_value=24999.99),
        # Exact threshold (should NOT be fast-track)
        st.just(FAST_TRACK_THRESHOLD),
        # Values just above threshold
        st.floats(min_value=25000.01, max_value=26000.0),
        # High values
        st.floats(min_value=30000.0, max_value=500000.0)
    )


def low_damage_amounts() -> SearchStrategy[float]:
    """Generate damage amounts strictly below fast-track threshold."""
    return st.floats(min_value=100.0, max_value=FAST_TRACK_THRESHOLD - 0.01)


def high_damage_amounts() -> SearchStrategy[float]:
    """Generate damage amounts at or above fast-track threshold."""
    return st.floats(min_value=FAST_TRACK_THRESHOLD, max_value=500000.0)


# ============================================================================
# Description Strategies (with/without fraud keywords)
# ============================================================================

@st.composite
def descriptions_without_fraud(draw) -> str:
    """
    Generate incident descriptions that do NOT contain fraud keywords.
    
    Used for testing non-investigation routing paths.
    """
    templates = [
        "Vehicle collision at intersection. Driver failed to yield at stop sign.",
        "Property damage due to severe weather conditions. Roof sustained water damage.",
        "Minor fender bender in parking lot. No injuries reported.",
        "Rear-end collision on highway during rush hour traffic.",
        "Tree fell on vehicle during storm. Windshield and hood damaged.",
        "Slip and fall incident on wet floor. Medical attention required.",
        "Vehicle struck by falling debris from construction site.",
        "Water damage from burst pipe in basement. Multiple rooms affected."
    ]
    
    base = draw(st.sampled_from(templates))
    
    # Add some variation
    additions = [
        " Police report filed.",
        " Witnesses present at scene.",
        " Photos taken of damage.",
        " Emergency services contacted.",
        ""
    ]
    addition = draw(st.sampled_from(additions))
    
    return base + addition


@st.composite
def descriptions_with_fraud(draw) -> str:
    """
    Generate incident descriptions that contain fraud keywords.
    
    Used for testing investigation routing path. Includes fraud keywords
    in various cases to test case-insensitive matching.
    """
    # Choose a fraud keyword and vary its case
    keyword = draw(st.sampled_from(FRAUD_KEYWORDS))
    case_variant = draw(st.sampled_from([
        keyword.lower(),
        keyword.upper(),
        keyword.capitalize()
    ]))
    
    templates = [
        f"Witness reports suggest {case_variant} activity at the scene.",
        f"Details appear {case_variant} based on initial investigation.",
        f"Possible {case_variant} accident involving multiple parties.",
        f"Evidence indicates this may be a {case_variant} claim.",
        f"The circumstances seem {case_variant} and require further review."
    ]
    
    return draw(st.sampled_from(templates))


def descriptions(include_fraud: Optional[bool] = None) -> SearchStrategy[str]:
    """
    Generate incident descriptions with optional fraud keyword control.
    
    Args:
        include_fraud: If True, always include fraud keywords.
                      If False, never include fraud keywords.
                      If None, randomly choose.
    """
    if include_fraud is True:
        return descriptions_with_fraud()
    elif include_fraud is False:
        return descriptions_without_fraud()
    else:
        return st.one_of(descriptions_with_fraud(), descriptions_without_fraud())


# ============================================================================
# Extracted Fields Strategies
# ============================================================================

@st.composite
def policy_information_dicts(draw, allow_missing: bool = False) -> dict:
    """
    Generate PolicyInformation as dictionary.
    
    Args:
        allow_missing: If True, fields may be None
    """
    if allow_missing:
        policy_num = draw(st.one_of(st.none(), policy_numbers()))
        holder_name = draw(st.one_of(st.none(), person_names()))
        effective = draw(st.one_of(st.none(), st.text(min_size=10, max_size=50)))
    else:
        policy_num = draw(policy_numbers())
        holder_name = draw(person_names())
        effective = draw(st.text(min_size=10, max_size=50))
    
    return {
        "policyNumber": policy_num,
        "policyholderName": holder_name,
        "effectiveDates": effective
    }


@st.composite
def incident_information_dicts(draw, allow_missing: bool = False, include_fraud: Optional[bool] = None) -> dict:
    """
    Generate IncidentInformation as dictionary.
    
    Args:
        allow_missing: If True, fields may be None
        include_fraud: Control fraud keyword presence in description
    """
    if allow_missing:
        date_val = draw(st.one_of(st.none(), dates()))
        time_val = draw(st.one_of(st.none(), times()))
        location_val = draw(st.one_of(st.none(), locations()))
        desc_val = draw(st.one_of(st.none(), descriptions(include_fraud)))
    else:
        date_val = draw(dates())
        time_val = draw(times())
        location_val = draw(locations())
        desc_val = draw(descriptions(include_fraud))
    
    return {
        "date": date_val,
        "time": time_val,
        "location": location_val,
        "description": desc_val
    }


@st.composite
def involved_parties_dicts(draw, allow_missing: bool = False) -> dict:
    """Generate InvolvedParties as dictionary."""
    if allow_missing:
        claimant_val = draw(st.one_of(st.none(), person_names()))
        third_val = draw(st.one_of(st.none(), st.lists(person_names(), min_size=0, max_size=3)))
        contact_val = draw(st.one_of(st.none(), phone_numbers()))
    else:
        claimant_val = draw(person_names())
        third_val = draw(st.lists(person_names(), min_size=0, max_size=3))
        contact_val = draw(phone_numbers())
    
    return {
        "claimant": claimant_val,
        "thirdParties": third_val,
        "contactDetails": contact_val
    }


@st.composite
def asset_details_dicts(draw, allow_missing: bool = False, damage_strategy: Optional[SearchStrategy[float]] = None) -> dict:
    """
    Generate AssetDetails as dictionary.
    
    Args:
        allow_missing: If True, fields may be None
        damage_strategy: Custom strategy for damage amounts (e.g., low_damage_amounts())
    """
    if damage_strategy is None:
        damage_strategy = damage_amounts()
    
    if allow_missing:
        asset_type_val = draw(st.one_of(st.none(), st.sampled_from(["vehicle", "property", "equipment"])))
        asset_id_val = draw(st.one_of(st.none(), asset_ids()))
        damage_val = draw(st.one_of(st.none(), damage_strategy))
    else:
        asset_type_val = draw(st.sampled_from(["vehicle", "property", "equipment"]))
        asset_id_val = draw(asset_ids())
        damage_val = draw(damage_strategy)
    
    return {
        "assetType": asset_type_val,
        "assetId": asset_id_val,
        "estimatedDamage": damage_val
    }


@st.composite
def extracted_fields_dicts(
    draw,
    allow_missing: bool = False,
    include_fraud: Optional[bool] = None,
    damage_strategy: Optional[SearchStrategy[float]] = None,
    claim_type_value: Optional[str] = None
) -> dict:
    """
    Generate complete ExtractedFields as dictionary.
    
    Args:
        allow_missing: If True, mandatory fields may be None
        include_fraud: Control fraud keyword presence in description
        damage_strategy: Custom strategy for damage amounts
        claim_type_value: Force specific claim type (e.g., "injury")
    """
    policy_info = draw(policy_information_dicts(allow_missing=allow_missing))
    incident_info = draw(incident_information_dicts(allow_missing=allow_missing, include_fraud=include_fraud))
    parties = draw(involved_parties_dicts(allow_missing=False))  # Not mandatory
    assets = draw(asset_details_dicts(allow_missing=allow_missing, damage_strategy=damage_strategy))
    
    if claim_type_value is not None:
        claim_type_val = claim_type_value
    elif allow_missing:
        claim_type_val = draw(st.one_of(st.none(), claim_types()))
    else:
        claim_type_val = draw(claim_types())
    
    attachments_val = draw(st.one_of(st.none(), st.lists(st.text(min_size=5, max_size=20), min_size=0, max_size=3)))
    initial_est_val = draw(st.one_of(st.none(), st.floats(min_value=100.0, max_value=100000.0)))
    
    return {
        "policyInformation": policy_info,
        "incidentInformation": incident_info,
        "involvedParties": parties,
        "assetDetails": assets,
        "claimType": claim_type_val,
        "attachments": attachments_val,
        "initialEstimate": initial_est_val
    }


@st.composite
def extracted_fields_objects(
    draw,
    allow_missing: bool = False,
    include_fraud: Optional[bool] = None,
    damage_strategy: Optional[SearchStrategy[float]] = None,
    claim_type_value: Optional[str] = None
) -> ExtractedFields:
    """
    Generate complete ExtractedFields as Pydantic model instance.
    
    This is the primary strategy for generating test data for routing logic.
    
    Args:
        allow_missing: If True, mandatory fields may be None
        include_fraud: Control fraud keyword presence in description
        damage_strategy: Custom strategy for damage amounts
        claim_type_value: Force specific claim type (e.g., "injury")
    """
    fields_dict = draw(extracted_fields_dicts(
        allow_missing=allow_missing,
        include_fraud=include_fraud,
        damage_strategy=damage_strategy,
        claim_type_value=claim_type_value
    ))
    
    return ExtractedFields(
        policyInformation=PolicyInformation(**fields_dict["policyInformation"]),
        incidentInformation=IncidentInformation(**fields_dict["incidentInformation"]),
        involvedParties=InvolvedParties(**fields_dict["involvedParties"]),
        assetDetails=AssetDetails(**fields_dict["assetDetails"]),
        claimType=fields_dict["claimType"],
        attachments=fields_dict["attachments"],
        initialEstimate=fields_dict["initialEstimate"]
    )


# ============================================================================
# Specialized Strategies for Specific Routing Scenarios
# ============================================================================

def fraud_claims() -> SearchStrategy[ExtractedFields]:
    """
    Generate claims that should route to Investigation.
    
    - Contains fraud keywords in description
    - All other fields can vary
    """
    return extracted_fields_objects(
        allow_missing=False,
        include_fraud=True
    )


def incomplete_claims() -> SearchStrategy[ExtractedFields]:
    """
    Generate claims that should route to ManualReview.
    
    - Missing at least one mandatory field
    - No fraud keywords
    """
    return extracted_fields_objects(
        allow_missing=True,
        include_fraud=False
    )


def injury_claims() -> SearchStrategy[ExtractedFields]:
    """
    Generate claims that should route to SpecialistQueue.
    
    - Claim type is "injury"
    - All mandatory fields present
    - No fraud keywords
    """
    return extracted_fields_objects(
        allow_missing=False,
        include_fraud=False,
        claim_type_value="injury"
    )


@st.composite
def fast_track_claims(draw) -> ExtractedFields:
    """
    Generate claims that should route to FastTrack.
    
    - Estimated damage < $25,000
    - All mandatory fields present
    - No fraud keywords
    - Claim type is NOT "injury"
    """
    non_injury_type = draw(st.sampled_from(["property", "collision", "theft", "vandalism"]))
    return draw(extracted_fields_objects(
        allow_missing=False,
        include_fraud=False,
        damage_strategy=low_damage_amounts(),
        claim_type_value=non_injury_type
    ))


@st.composite
def standard_claims(draw) -> ExtractedFields:
    """
    Generate claims that should route to Standard.
    
    - All mandatory fields present
    - No fraud keywords
    - Claim type is NOT "injury"
    - Estimated damage >= $25,000
    """
    non_injury_type = draw(st.sampled_from(["property", "collision", "liability", "comprehensive"]))
    return draw(extracted_fields_objects(
        allow_missing=False,
        include_fraud=False,
        damage_strategy=high_damage_amounts(),
        claim_type_value=non_injury_type
    ))


# ============================================================================
# FNOL Document Text Strategies
# ============================================================================

@st.composite
def fnol_text(
    draw,
    include_fraud: Optional[bool] = None,
    include_all_fields: bool = True
) -> str:
    """
    Generate realistic FNOL document text.
    
    Args:
        include_fraud: Control fraud keyword presence
        include_all_fields: If False, randomly omit some fields
    
    Returns:
        Formatted FNOL document text as a string
    """
    # Generate field values
    policy_num = draw(policy_numbers())
    holder_name = draw(person_names())
    effective_dates = f"{draw(dates())} to {draw(dates())}"
    incident_date = draw(dates())
    incident_time = draw(times())
    incident_location = draw(locations())
    incident_desc = draw(descriptions(include_fraud))
    claimant = draw(person_names())
    contact = draw(phone_numbers())
    asset_type = draw(st.sampled_from(["vehicle", "property", "equipment"]))
    asset_id = draw(asset_ids())
    damage = draw(damage_amounts())
    claim_type = draw(claim_types())
    
    # Build document text
    lines = [
        "FIRST NOTICE OF LOSS",
        "=" * 50,
        "",
        "POLICY INFORMATION",
        f"Policy Number: {policy_num}",
        f"Policyholder Name: {holder_name}",
        f"Policy Effective Dates: {effective_dates}",
        "",
        "INCIDENT INFORMATION",
        f"Date of Incident: {incident_date}",
        f"Time of Incident: {incident_time}",
        f"Location: {incident_location}",
        f"Description: {incident_desc}",
        "",
        "INVOLVED PARTIES",
        f"Claimant: {claimant}",
        f"Contact Details: {contact}",
        "",
        "ASSET DETAILS",
        f"Asset Type: {asset_type}",
        f"Asset ID: {asset_id}",
        f"Estimated Damage: ${damage:,.2f}",
        "",
        "CLAIM INFORMATION",
        f"Claim Type: {claim_type}",
        ""
    ]
    
    return "\n".join(lines)


# ============================================================================
# Field Sets with Missing Mandatory Fields
# ============================================================================

@st.composite
def field_sets_with_missing_mandatory(draw) -> tuple[ExtractedFields, list[str]]:
    """
    Generate ExtractedFields with at least one missing mandatory field.
    
    Returns:
        Tuple of (ExtractedFields, list of expected missing field paths)
    """
    # Choose which mandatory fields to make missing (at least one)
    num_missing = draw(st.integers(min_value=1, max_value=len(MANDATORY_FIELDS)))
    missing_fields = draw(st.lists(
        st.sampled_from(MANDATORY_FIELDS),
        min_size=num_missing,
        max_size=num_missing,
        unique=True
    ))
    
    # Generate base fields
    fields_dict = draw(extracted_fields_dicts(allow_missing=False, include_fraud=False))
    
    # Set chosen fields to None
    for field_path in missing_fields:
        parts = field_path.split(".")
        if len(parts) == 1:
            fields_dict[parts[0]] = None
        elif len(parts) == 2:
            fields_dict[parts[0]][parts[1]] = None
    
    # Create ExtractedFields object
    extracted = ExtractedFields(
        policyInformation=PolicyInformation(**fields_dict["policyInformation"]),
        incidentInformation=IncidentInformation(**fields_dict["incidentInformation"]),
        involvedParties=InvolvedParties(**fields_dict["involvedParties"]),
        assetDetails=AssetDetails(**fields_dict["assetDetails"]),
        claimType=fields_dict["claimType"],
        attachments=fields_dict["attachments"],
        initialEstimate=fields_dict["initialEstimate"]
    )
    
    return extracted, missing_fields
