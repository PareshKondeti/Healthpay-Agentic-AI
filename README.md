# HealthPay Claim Document Processor

An AI-driven agentic backend pipeline for processing medical insurance claim documents using FastAPI and modern LLM technologies.

## 🏗️ Architecture & Design

### System Architecture
The system follows a **multi-agent architecture** with clear separation of concerns:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│  Orchestrator    │───▶│  LLM Service    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Specialized     │
                       │  Agents          │
                       │  ├─ Classifier   │
                       │  ├─ BillAgent    │
                       │  ├─ DischargeAgent│
                       │  └─ IDCardAgent  │
                       └──────────────────┘
```

### Key Components

1. **ClaimOrchestrator**: Main coordinator that manages the entire processing pipeline
2. **Specialized Agents**: Each agent handles specific document types with domain expertise
3. **LLM Service**: Centralized service for all AI/LLM interactions using Google's Gemini
4. **PDF Service**: Handles PDF text extraction with async processing
5. **Validation System**: Multi-layer validation with AI-powered consistency checks

### Agent Workflow

1. **Document Classification**: AI classifies each document type
2. **Specialized Processing**: Route to appropriate agent (Bill, Discharge, ID Card)
3. **Data Extraction**: Extract structured data using LLM prompts
4. **Validation**: Cross-document validation and consistency checks
5. **Decision Making**: AI-powered claim approval/rejection logic

## 🛠️ Tech Stack

- **Backend**: FastAPI with async/await patterns
- **AI/LLM**: Google Gemini Pro for document processing
- **Document Processing**: PyPDF2 for text extraction
- **Validation**: Pydantic models with type safety
- **Architecture**: Agent-based with orchestration pattern
- **Containerization**: Docker with docker-compose
- **Database Ready**: PostgreSQL and Redis configured

## 🤖 AI Tool Usage Documentation

### Tools Used

1. **Claude (Anthropic)** - Primary assistant for:
   - Architecture design and system planning
   - Code structure and FastAPI patterns
   - Agent design patterns and orchestration logic
   - Error handling and validation strategies

2. **Bolt A** - Code completion and refactoring:
   - Automated boilerplate generation
   - Type hint completion
   - Import organization and code formatting

3. **Google Gemini Pro** - LLM for document processing:
   - Document classification
   - Structured data extraction
   - Validation and consistency checking
   - Claim decision making

### Key Prompts Used

#### 1. Document Classification Prompt
```
Analyze the following document text and filename to classify the document type.

Filename: {filename}

Document Text (first 1000 chars):
{text}

Classify this document as one of:
- bill: Medical bill or invoice
- discharge_summary: Hospital discharge summary
- id_card: Insurance ID card
- unknown: Cannot determine type

Return a JSON response with:
{
    "type": "document_type",
    "confidence": 0.95,
    "reasoning": "Brief explanation of classification"
}
```

#### 2. Bill Data Extraction Prompt
```
Extract key information from this medical bill document:

{text}

Extract the following information and return as JSON:
{
    "hospital_name": "Name of hospital/provider",
    "total_amount": 12500.00,
    "date_of_service": "2024-04-10",
    "patient_name": "Patient Name",
    "services": ["Service 1", "Service 2"],
    "insurance_id": "Insurance ID if present"
}

If information is not found, use null for that field.
```

#### 3. Claim Decision Prompt
```
Make a claim decision based on the processed documents and validation results:

Documents: {documents}
Validation Results: {validation}

Decision criteria:
- Approve if all required documents present and no major discrepancies
- Reject if critical information missing or major discrepancies found
- Require review if minor issues that need human attention

Return decision as JSON:
{
    "status": "approved|rejected|requires_review",
    "reason": "Detailed explanation of decision",
    "confidence": 0.95,
    "recommended_actions": ["Action 1", "Action 2"]
}
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Google API Key for Gemini

## 🚀 Running Instructions

Follow these steps to set up and run the FastAPI project locally:

```powershell
# Step 1: Create a virtual environment (Python 3.11)
py -3.11 -m venv venv

# Step 2: Activate the virtual environment (for PowerShell)
.\venv\Scripts\Activate.ps1

# Step 3: Install required packages
pip install -r requirements.txt

# Step 4: Run the FastAPI app
python -m uvicorn app.main:app --reload
```

🔍 **API Documentation (Swagger UI):**  
Open your browser and go to: [http://localhost:8000/docs](http://localhost:8000/docs)


### Setup

1. **Clone and Setup Environment**
```bash
git clone <repo-url>
cd healthpay-claim-processor
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run with Docker**
```bash
docker-compose up -d
```

4. **Or Run Locally**
```bash
uvicorn app.main:app --reload 
```
5. **Fastapi Link**
"http://localhost:8000/docs" 
Here click on process claim and test the code 

### API Usage

**Process Claim Documents**
```bash
curl -X POST "http://localhost:8000/process-claim" \
  -F "files=@medical_bill.pdf" \
  -F "files=@discharge_summary.pdf" \
  -F "files=@insurance_card.pdf"
```

**Example Response**
```json
{
  "documents": [
    {
      "type": "bill",
      "filename": "medical_bill.pdf",
      "confidence": 0.95,
      "extracted_data": {
        "hospital_name": "General Hospital",
        "total_amount": 12500.00,
        "date_of_service": "2024-04-10",
        "patient_name": "John Doe"
      }
    }
  ],
  "validation": {
    "missing_documents": [],
    "discrepancies": [],
    "validation_passed": true
  },
  "claim_decision": {
    "status": "approved",
    "reason": "All required documents present and data is consistent",
    "confidence": 0.92
  }
}
```

## 🧪 Testing

Run tests with:
```bash
pytest tests/ -v
```

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `ENVIRONMENT`: development/production
- `LOG_LEVEL`: INFO/DEBUG/WARNING/ERROR

### Agent Configuration
Each agent can be configured with:
- Processing timeout settings
- Validation thresholds
- Error handling strategies

## 📊 Performance Considerations

- **Async Processing**: All file operations and LLM calls are async
- **Concurrent Document Processing**: Multiple documents processed in parallel
- **Connection Pooling**: Efficient LLM API usage
- **Memory Management**: Streaming file processing for large documents

## 🔍 Monitoring & Logging

- Structured logging with correlation IDs
- Processing time metrics
- Agent performance tracking
- Error rate monitoring

## 🛡️ Security

- Input validation with Pydantic models
- File type validation
- API key security
- Rate limiting ready

## 📈 Scalability

- Horizontal scaling with load balancers
- Database integration ready
- Redis caching for performance
- Microservice architecture support

## 🔄 Future Enhancements

- [ ] Vector database integration for document similarity
- [ ] Real-time processing status updates
- [ ] Advanced fraud detection agents
- [ ] Multi-language document support
- [ ] Advanced analytics and reporting

## 📝 Development Notes

### AI-Assisted Development Process
1. Used Claude for architectural decisions and system design
2. Leveraged Cursor AI for code completion and refactoring
3. Iterative prompt engineering for optimal LLM performance
4. Continuous validation and testing of AI outputs

### Design Decisions
- **Agent Pattern**: Chosen for modularity and specialization
- **Async Architecture**: For handling multiple documents efficiently
- **JSON Schema**: For structured, validated outputs
- **Error Handling**: Comprehensive error handling with fallbacks
- **LLM Integration**: Centralized service for consistency

### Known Limitations
- PDF text extraction quality depends on document format
- LLM response consistency may vary
- Processing time increases with document complexity
- Rate limiting considerations for production deployment

---

**Built with ❤️ using AI-powered development tools**