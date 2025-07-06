from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    BILL = "bill"
    DISCHARGE_SUMMARY = "discharge_summary"
    ID_CARD = "id_card"
    UNKNOWN = "unknown"

class ClaimStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"

class ProcessedDocument(BaseModel):
    type: DocumentType
    filename: str
    confidence: float = Field(ge=0, le=1)
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    processing_errors: List[str] = Field(default_factory=list)

class BillDocument(BaseModel):
    type: DocumentType = DocumentType.BILL
    hospital_name: Optional[str] = None
    total_amount: Optional[float] = None
    date_of_service: Optional[str] = None
    patient_name: Optional[str] = None
    services: List[str] = Field(default_factory=list)
    insurance_id: Optional[str] = None

class DischargeSummaryDocument(BaseModel):
    type: DocumentType = DocumentType.DISCHARGE_SUMMARY
    patient_name: Optional[str] = None
    diagnosis: Optional[str] = None
    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None
    treating_physician: Optional[str] = None
    hospital_name: Optional[str] = None
    procedures: List[str] = Field(default_factory=list)

class IDCardDocument(BaseModel):
    type: DocumentType = DocumentType.ID_CARD
    patient_name: Optional[str] = None
    insurance_id: Optional[str] = None
    policy_number: Optional[str] = None
    group_number: Optional[str] = None
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None

class ValidationResult(BaseModel):
    missing_documents: List[str] = Field(default_factory=list)
    discrepancies: List[str] = Field(default_factory=list)
    data_quality_issues: List[str] = Field(default_factory=list)
    validation_passed: bool = True

class ClaimDecision(BaseModel):
    status: ClaimStatus
    reason: str
    confidence: float = Field(ge=0, le=1)
    recommended_actions: List[str] = Field(default_factory=list)

class ClaimProcessingResponse(BaseModel):
    documents: List[ProcessedDocument]
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    validation: ValidationResult
    claim_decision: ClaimDecision
    processing_time: float
    processed_at: datetime = Field(default_factory=datetime.now)