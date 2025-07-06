
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
import os
from dotenv import load_dotenv

from app.agents.orchestrator import ClaimOrchestrator
from app.models.schemas import ClaimProcessingResponse
from app.services.llm_service import LLMService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HealthPay Claim Processor",
    description="AI-driven agentic backend for processing medical insurance claims",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
def get_llm_service():
    return LLMService()

def get_orchestrator(llm_service: LLMService = Depends(get_llm_service)):
    return ClaimOrchestrator(llm_service)

@app.get("/")
async def root():
    return {"message": "HealthPay Claim Processor API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "claim-processor"}

@app.post("/process-claim", response_model=ClaimProcessingResponse)
async def process_claim(
    files: List[UploadFile] = File(...),
    orchestrator: ClaimOrchestrator = Depends(get_orchestrator)
):
    """
    Process medical insurance claim documents using AI agents.
    
    Accepts multiple PDF files and returns structured claim data with decision.
    """
    try:
        logger.info(f"Processing {len(files)} files for claim")
        
        # Validate file types
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}. Only PDF files are supported."
                )
        
        # Process claim through orchestrator
        result = await orchestrator.process_claim(files)
        
        logger.info("Claim processing completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error processing claim: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)