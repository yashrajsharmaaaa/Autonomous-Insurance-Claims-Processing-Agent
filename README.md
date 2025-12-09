# Autonomous Insurance Claims Processing Agent

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



## � Moore Projects

I've built several other projects using AI-assisted development that demonstrate my ability to ship products quickly. Check out my GitHub profile for more examples:

**GitHub Portfolio**: [https://github.com/yashrajsharmaaaa](https://github.com/yashrajsharmaaaa)

Each project showcases:
- Clean, production-ready code
- AI-accelerated development workflow
- Deployed, working applications

I'm comfortable using AI tools to move fast while maintaining code quality - exactly the approach Synapx values.

---

## 📞 Contact

**Name**: Yashraj Sharma  
**Email**: yashrajsharma413@gmail.com  
**GitHub**: https://github.com/yashrajsharmaaaa  
**LinkedIn**: https://www.linkedin.com/in/yashrajsharmaaaa

---

## 🙏 Thank You

Thank you for reviewing my assessment! I'm excited about the opportunity to join Synapx and contribute to building products that ship fast and matter. I'm comfortable with AI tools, enjoy solving messy problems with clean logic, and thrive in fast-paced, product-first environments.

I'm happy to discuss any aspect of this implementation.

---

**Note**: This project demonstrates clarity over complexity. The focus is on clean, working code with good structure and explainable logic - exactly what was requested in the assessment.
