# FNOL Claim Processor

**Autonomous Insurance Claims Processing Agent**

---

## 🌐 Live Demo - Test with Your Own FNOL Files!

**Try it now (no setup required):** [https://fnol-agent.onrender.com/docs](https://fnol-agent.onrender.com/docs)

### How to Test:
1. Click the link above to open the interactive API
2. Click on **"POST /process-claim"** to expand it
3. Click **"Try it out"** button
4. Click **"Choose File"** and upload your FNOL document (PDF or TXT)
5. Click **"Execute"**
6. See the JSON response with:
   - ✅ Extracted fields (policy info, incident details, etc.)
   - ✅ Missing mandatory fields (if any)
   - ✅ Recommended routing decision
   - ✅ Human-readable reasoning

**No installation, no API key needed - just upload and test!**

---

## 📋 Assessment Submission

This project demonstrates an autonomous FNOL (First Notice of Loss) claims processing system that extracts structured data from documents, validates completeness, and intelligently routes claims to appropriate workflows.

### ✅ Requirements Completed

| Requirement | Implementation | Status |
|------------|----------------|--------|
| Extract key fields from FNOL documents | 16 structured fields using Google Gemini AI + regex fallback | ✅ |
| Identify claim type, policy data, incident details | Complete data model with Pydantic validation | ✅ |
| Flag missing or inconsistent information | Validates 6 mandatory fields, lists specific missing data | ✅ |
| Simple workflow routing | 5 routes with priority logic: Investigation, ManualReview, SpecialistQueue, FastTrack, Standard | ✅ |
| **Optional**: Basic prediction logic | Rule-based routing with fraud detection and damage thresholds | ✅ |
| **Optional**: Explanation for decisions | Every route includes 1-3 sentence reasoning | ✅ |

### 🚀 Quick Start (For Recruiters Testing with Your Own FNOL Files)

```bash
# 1. Clone and setup
git clone https://github.com/yashrajsharmaaaa/Autonomous-Insurance-Claims-Processing-Agent.git
cd Autonomous-Insurance-Claims-Processing-Agent
pip install -r requirements.txt

# 2. Get FREE Gemini API key (takes 2 minutes)
# Visit: https://makersuite.google.com/app/apikey
# Click "Create API Key" → Copy the key
# Create .env file with: GEMINI_API_KEY=your_key_here

# 3. Test with sample documents
python demo.py

# 4. Test with YOUR OWN FNOL file
curl -X POST "http://localhost:8000/process-claim" \
  -F "file=@your_fnol_document.pdf"

# Or use the interactive API docs:
uvicorn app.main:app --reload
# Then visit: http://localhost:8000/docs
# Click "Try it out" → Upload your file → Execute
```

**📝 Testing with Your Own Files:**
- Supports PDF and TXT formats
- Works with any FNOL document structure (AI adapts to format)
- Returns structured JSON with extracted fields + routing decision + reasoning
- Without API key: Falls back to regex (works but less accurate)

---

### 📤 How to Test with Your Own FNOL Documents

**Method 1: Command Line (Fastest)**
```bash
# Start the server
uvicorn app.main:app --reload

# In another terminal, test with your file
curl -X POST "http://localhost:8000/process-claim" \
  -F "file=@path/to/your/fnol_document.pdf"
```

**Method 2: Interactive API Docs (Easiest)**
```bash
# Start the server
uvicorn app.main:app --reload

# Open browser to: http://localhost:8000/docs
# 1. Click on "POST /process-claim"
# 2. Click "Try it out"
# 3. Click "Choose File" and select your FNOL document
# 4. Click "Execute"
# 5. See the JSON response with extracted data and routing decision
```

**Method 3: Python Script**
```python
from app.parser import parse_document
from app.extractor import extract_fields
from app.router_rules import identify_missing_fields, determine_route
from app.models import ExtractedFields

# Parse your document
text = parse_document("your_fnol.pdf", "pdf")

# Extract fields
extracted_dict = extract_fields(text)
extracted = ExtractedFields(**extracted_dict)

# Get routing decision
missing = identify_missing_fields(extracted)
route, reasoning = determine_route(extracted, missing)

print(f"Route: {route}")
print(f"Reasoning: {reasoning}")
```

---

### 🎯 What I Built

**Problem**: Insurance companies receive unstructured FNOL documents that need to be processed, validated, and routed efficiently.

**Solution**: An automated pipeline that:
1. **Parses** PDF/TXT documents to extract raw text
2. **Extracts** 16 structured fields using AI (with fallback)
3. **Validates** completeness against 6 mandatory fields
4. **Routes** claims based on priority rules (fraud > missing fields > injury > low damage > standard)
5. **Explains** every decision with human-readable reasoning

**Architecture**:
```
Document → Parser → Extractor → Validator → Router → Response
```

---

## 🛠️ How I Approached This

### 1. Problem Breakdown

I started by identifying the core challenges:
- Unstructured text needs to become structured data
- Different document formats (PDF, TXT)
- Missing or incomplete information
- Multiple routing scenarios with different priorities
- Need for explainable decisions

### 2. Design Decisions

**AI-First with Fallback**
- Used Google Gemini API for primary extraction (handles natural language well)
- Built regex-based fallback for reliability when API unavailable
- Engineered prompts to prevent hallucination ("return null for missing fields")

**Priority-Based Routing**
- Sequential evaluation ensures consistent, predictable decisions
- Clear precedence: fraud detection > completeness > specialization > value
- Easy to test and validate each rule independently

**Modular Architecture**
- Separated concerns: parsing, extraction, validation, routing
- Each module can be tested independently
- Type-safe with Pydantic models throughout

**Comprehensive Testing**
- 56 tests covering unit tests and property-based tests
- Property tests use Hypothesis to verify correctness across random inputs
- 66% code coverage with 100% on critical modules

### 3. AI Tool Usage

**Google Gemini API**
- Primary field extraction with structured JSON prompts
- Temperature=0 for deterministic results
- Explicit instructions to avoid hallucination

**Kiro AI**
- Accelerated development workflow
- Generated boilerplate and test scaffolding
- Helped with documentation and code structure

**Fallback Strategy**
- Regex patterns for common field formats
- Ensures system works even without API key
- Graceful degradation

---

## 📊 Technical Implementation

### Data Model (16 Fields Extracted)

```json
{
  "policyInformation": {
    "policyNumber": "POL-2024-789456",
    "policyholderName": "Sarah Johnson",
    "effectiveDates": "01/01/2024 - 12/31/2024"
  },
  "incidentInformation": {
    "date": "11/15/2024",
    "time": "2:30 PM",
    "location": "1234 Oak Street, Springfield, IL",
    "description": "Minor fender bender in parking lot..."
  },
  "involvedParties": {
    "claimant": "Sarah Johnson",
    "thirdParties": ["Michael Chen"],
    "contactDetails": "555-123-4567"
  },
  "assetDetails": {
    "assetType": "Vehicle",
    "assetId": "VIN 1HGBH41JXMN109186",
    "estimatedDamage": 3500.0
  },
  "claimType": "property",
  "attachments": ["photos.jpg"],
  "initialEstimate": 3500.0
}
```

### Routing Logic (Priority Order)

1. **Investigation** - Fraud keywords detected ("fraud", "inconsistent", "staged")
2. **ManualReview** - Any mandatory field missing
3. **SpecialistQueue** - Claim type = "injury"
4. **FastTrack** - Estimated damage < $25,000
5. **Standard** - Default route

**Key Edge Case**: Exactly $25,000 is NOT fast-track (must be strictly less than)

### Example Response

```json
{
  "extractedFields": { ... },
  "missingFields": [],
  "recommendedRoute": "FastTrack",
  "reasoning": "Claim eligible for fast-track processing with estimated damage of $3,500.00, which is below the $25,000.00 threshold."
}
```

---

## 🧪 Testing & Quality

**Test Coverage**: 56 tests, all passing
- Unit tests: Specific examples and edge cases
- Property-based tests: Random inputs to verify correctness
- Integration tests: End-to-end workflows

**Coverage by Module**:
- `models.py`: 100%
- `router_rules.py`: 95%
- `extractor.py`: 84%
- `parser.py`: 69%

**Run Tests**:
```bash
pytest -v                    # All tests
pytest --cov=app tests/      # With coverage
```

---

## 🚀 Setup & Usage

### Prerequisites
- Python 3.11+
- Google Gemini API key (optional - works without it)

### Installation

```bash
# 1. Clone repository
git clone <repo-url>
cd fnol-claim-processor

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Add Gemini API key
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here
```

### Running the Application

**Option 1: Demo Script** (Easiest way to see it work)
```bash
python demo.py
```

**Option 2: API Server**
```bash
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs for interactive API
```

**Option 3: Direct API Call**
```bash
curl -X POST "http://localhost:8000/process-claim" \
  -F "file=@sample_docs/fnol_fasttrack.txt"
```

### Sample Documents

I've included 5 sample FNOL documents demonstrating different scenarios:
- `fnol_fasttrack.txt` - Low damage ($3,500) → FastTrack route
- `fnol_investigation.txt` - Contains fraud keywords → Investigation route
- `fnol_manual_review.txt` - Missing fields → ManualReview route
- `fnol_specialist_queue.txt` - Injury claim → SpecialistQueue route
- `fnol_standard.txt` - Standard claim → Standard route

---

## 📁 Project Structure

```
fnol-claim-processor/
├── app/
│   ├── main.py              # FastAPI endpoints
│   ├── models.py            # Pydantic data models
│   ├── parser.py            # PDF/TXT parsing
│   ├── extractor.py         # AI + heuristic extraction
│   └── router_rules.py      # Validation & routing logic
├── tests/
│   ├── test_parser_*.py     # Parser tests
│   ├── test_extractor_*.py  # Extractor tests
│   ├── test_router_*.py     # Router tests
│   └── property/            # Property-based tests
├── sample_docs/             # 5 test scenarios
├── demo.py                  # Quick demonstration
├── requirements.txt         # Dependencies
└── README.md               # This file
```

---

## 💡 Key Assumptions

1. **Currency**: All amounts in USD
2. **Threshold**: Exactly $25,000 is NOT fast-track (must be < $25,000)
3. **PDF Format**: Text-based PDFs (no OCR required)
4. **Language**: English documents only
5. **Fraud Keywords**: ["fraud", "inconsistent", "staged"] (case-insensitive)
6. **Priority Order**: Strict sequential evaluation
7. **Mandatory Fields**: 6 fields required (policy number, policyholder name, incident date, incident description, claim type, estimated damage)

---

## 🎓 What I Learned

1. **Prompt Engineering**: Structured prompts with explicit schemas prevent AI hallucination
2. **Property-Based Testing**: Hypothesis library catches edge cases I wouldn't have thought of
3. **Type Safety**: Pydantic models catch errors at development time, not runtime
4. **Modular Design**: Separation of concerns makes testing and debugging much easier
5. **Graceful Degradation**: Fallback strategies ensure reliability

---

## 🔧 Technical Stack

- **Language**: Python 3.11
- **API Framework**: FastAPI
- **Data Validation**: Pydantic
- **PDF Parsing**: pdfplumber
- **AI Extraction**: Google Gemini API (gemini-1.5-flash)
- **Testing**: pytest + Hypothesis (property-based testing)
- **Type Checking**: Full type hints throughout

---

## 📈 Performance

- **Response Time**: 2-5 seconds with Gemini API, <1 second with fallback
- **File Size Limit**: 10MB (configurable)
- **Concurrency**: FastAPI async support for multiple requests
- **Reliability**: Fallback extraction ensures system always works

---

## 🚦 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**Main Endpoint**: `POST /process-claim`
- Accepts: PDF file, TXT file, or raw text
- Returns: Extracted fields, missing fields, route, reasoning

---

## 🤔 Design Trade-offs

**AI vs Rules**
- Chose AI-first for flexibility with document formats
- Added rule-based fallback for reliability
- Trade-off: Requires API key but handles variations better

**Priority vs Scoring**
- Chose priority-based sequential evaluation
- Trade-off: Less flexible but more predictable and testable

**Testing Depth**
- Invested in comprehensive testing (56 tests)
- Trade-off: More upfront time but higher confidence

---

## 🎯 If I Had More Time

1. **Web UI**: Simple dashboard for uploading and viewing results
2. **Confidence Scores**: Add confidence metrics to extraction
3. **Batch Processing**: Handle multiple documents at once
4. **OCR Support**: Process scanned PDFs
5. **Database**: Store claims for historical analysis
6. **Custom ML Model**: Train on historical data for better routing

---

## 📞 Contact

**Name**: [Your Name]  
**Email**: [Your Email]  
**GitHub**: [Your GitHub]  
**LinkedIn**: [Your LinkedIn]

---

## 🙏 Thank You

Thank you for reviewing my assessment! I'm excited about the opportunity to join Synapx and contribute to building products that ship fast and matter. I'm comfortable with AI tools, enjoy solving messy problems with clean logic, and thrive in fast-paced, product-first environments.

I'm happy to discuss any aspect of this implementation, walk through the code, or answer questions about my approach.

---

**Note**: This project demonstrates clarity over complexity. The focus is on clean, working code with good structure and explainable logic - exactly what was requested in the assessment.
