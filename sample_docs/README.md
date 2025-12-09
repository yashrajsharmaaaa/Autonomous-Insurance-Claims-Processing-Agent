# Sample FNOL Documents

This directory contains sample First Notice of Loss (FNOL) documents for testing the claim processor.

## Document Scenarios

### 1. fnol_fasttrack.txt / fnol_fasttrack.pdf
**Scenario:** Fast-track routing
- All mandatory fields present
- Low damage amount ($3,500 < $25,000)
- Property claim type (non-injury)
- Expected route: **FastTrack**

### 2. fnol_manual_review.txt
**Scenario:** Manual review routing
- Missing mandatory fields (Claim Type and Estimated Damage)
- Incomplete information
- Expected route: **ManualReview**

### 3. fnol_investigation.txt / fnol_investigation.pdf
**Scenario:** Investigation routing
- Contains fraud keywords ("inconsistent", "staged")
- All mandatory fields present
- Expected route: **Investigation** (highest priority)

### 4. fnol_specialist_queue.txt / fnol_specialist_queue.pdf
**Scenario:** Specialist queue routing
- Claim type is "injury"
- All mandatory fields present
- No fraud keywords
- Expected route: **SpecialistQueue**

### 5. fnol_standard.txt
**Scenario:** Standard routing
- All mandatory fields present
- High damage amount ($32,000 >= $25,000)
- Property claim type (non-injury)
- No fraud keywords
- Expected route: **Standard**

## File Formats

- **TXT files:** Plain text format for easy parsing
- **PDF files:** PDF format to test PDF parsing functionality

## Usage

These documents can be used to test the `/process-claim` endpoint:

```bash
# Test with TXT file
curl -X POST http://localhost:8000/process-claim \
  -F "file=@sample_docs/fnol_fasttrack.txt"

# Test with PDF file
curl -X POST http://localhost:8000/process-claim \
  -F "file=@sample_docs/fnol_fasttrack.pdf"
```

## Creating Additional PDFs

To create PDF versions of the remaining TXT files, run:

```bash
python sample_docs/create_pdfs.py
```

Note: Requires `reportlab` package (`pip install reportlab`)
