#!/usr/bin/env python3
"""
Quick demo script for FNOL Claim Processor assessment.

This script demonstrates the system's capabilities by processing
all sample documents and displaying the results.
"""

import json
from pathlib import Path
from app.parser import parse_document
from app.extractor import extract_fields
from app.router_rules import identify_missing_fields, determine_route
from app.models import ExtractedFields


def process_fnol_document(file_path: str) -> dict:
    """Process a single FNOL document through the complete pipeline."""
    
    # Determine file type
    file_type = Path(file_path).suffix.lstrip('.')
    
    # Step 1: Parse document
    print(f"  📄 Parsing {Path(file_path).name}...")
    raw_text = parse_document(file_path, file_type)
    
    # Step 2: Extract fields
    print(f"  🔍 Extracting fields...")
    extracted_dict = extract_fields(raw_text)
    
    # Step 3: Validate with Pydantic
    extracted = ExtractedFields(**extracted_dict)
    
    # Step 4: Identify missing fields
    missing = identify_missing_fields(extracted)
    
    # Step 5: Determine route
    route, reasoning = determine_route(extracted, missing)
    
    return {
        "extractedFields": extracted.dict(),
        "missingFields": missing,
        "recommendedRoute": route,
        "reasoning": reasoning
    }


def print_result(filename: str, result: dict):
    """Pretty print processing result."""
    print(f"\n{'='*80}")
    print(f"📋 Document: {filename}")
    print(f"{'='*80}")
    
    # Route and reasoning
    route = result["recommendedRoute"]
    route_emoji = {
        "FastTrack": "🚀",
        "ManualReview": "👤",
        "Investigation": "🔍",
        "SpecialistQueue": "🏥",
        "Standard": "📊"
    }
    
    print(f"\n{route_emoji.get(route, '📌')} Recommended Route: {route}")
    print(f"💭 Reasoning: {result['reasoning']}")
    
    # Missing fields
    if result["missingFields"]:
        print(f"\n⚠️  Missing Fields:")
        for field in result["missingFields"]:
            print(f"   - {field}")
    else:
        print(f"\n✅ All mandatory fields present")
    
    # Key extracted data
    fields = result["extractedFields"]
    print(f"\n📊 Key Extracted Data:")
    
    policy_info = fields.get("policyInformation", {})
    if policy_info.get("policyNumber"):
        print(f"   Policy: {policy_info['policyNumber']}")
    if policy_info.get("policyholderName"):
        print(f"   Policyholder: {policy_info['policyholderName']}")
    
    incident_info = fields.get("incidentInformation", {})
    if incident_info.get("date"):
        print(f"   Incident Date: {incident_info['date']}")
    
    if fields.get("claimType"):
        print(f"   Claim Type: {fields['claimType']}")
    
    asset_details = fields.get("assetDetails", {})
    if asset_details.get("estimatedDamage"):
        print(f"   Estimated Damage: ${asset_details['estimatedDamage']:,.2f}")


def main():
    """Run demo with all sample documents."""
    
    print("\n" + "="*80)
    print("🎯 FNOL Claim Processor - Assessment Demo")
    print("="*80)
    print("\nThis demo processes all sample FNOL documents to demonstrate:")
    print("  ✅ Field extraction from unstructured text")
    print("  ✅ Missing field identification")
    print("  ✅ Intelligent routing with priority rules")
    print("  ✅ Explainable AI decisions")
    
    # Sample documents to process
    sample_docs = [
        "sample_docs/fnol_fasttrack.txt",
        "sample_docs/fnol_investigation.txt",
        "sample_docs/fnol_manual_review.txt",
        "sample_docs/fnol_specialist_queue.txt",
        "sample_docs/fnol_standard.txt",
    ]
    
    results = []
    
    for doc_path in sample_docs:
        if not Path(doc_path).exists():
            print(f"\n⚠️  Skipping {doc_path} (not found)")
            continue
        
        try:
            print(f"\n{'─'*80}")
            print(f"Processing: {Path(doc_path).name}")
            print(f"{'─'*80}")
            
            result = process_fnol_document(doc_path)
            results.append((Path(doc_path).name, result))
            
            print_result(Path(doc_path).name, result)
            
        except Exception as e:
            print(f"\n❌ Error processing {doc_path}: {str(e)}")
    
    # Summary
    print(f"\n\n{'='*80}")
    print("📊 Processing Summary")
    print(f"{'='*80}")
    
    route_counts = {}
    for filename, result in results:
        route = result["recommendedRoute"]
        route_counts[route] = route_counts.get(route, 0) + 1
    
    print(f"\nTotal documents processed: {len(results)}")
    print(f"\nRouting Distribution:")
    for route, count in sorted(route_counts.items()):
        print(f"  {route}: {count}")
    
    print(f"\n{'='*80}")
    print("✅ Demo Complete!")
    print(f"{'='*80}\n")
    
    print("💡 Next Steps:")
    print("  1. Start the API: uvicorn app.main:app --reload")
    print("  2. Visit http://localhost:8000/docs for interactive API docs")
    print("  3. Run tests: pytest -v")
    print("  4. Check coverage: pytest --cov=app tests/")
    print()


if __name__ == "__main__":
    main()
