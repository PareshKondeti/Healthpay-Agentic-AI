from typing import List, Dict, Any
from fastapi import UploadFile
import asyncio
import time
import logging

from app.agents.base import BaseAgent
from app.agents.classifier import ClassifierAgent
from app.agents.bill_agent import BillAgent
from app.agents.discharge_agent import DischargeAgent
from app.agents.id_card_agent import IDCardAgent
from app.services.llm_service import LLMService
from app.services.pdf_service import PDFService
from app.models.schemas import ClaimProcessingResponse, ProcessedDocument, ValidationResult, ClaimDecision

logger = logging.getLogger(__name__)

class ClaimOrchestrator:
    """Main orchestrator for claim processing pipeline"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.pdf_service = PDFService()
        
        # Initialize agents
        self.classifier_agent = ClassifierAgent(llm_service)
        self.bill_agent = BillAgent(llm_service)
        self.discharge_agent = DischargeAgent(llm_service)
        self.id_card_agent = IDCardAgent(llm_service)
        
        # Agent mapping
        self.agent_mapping = {
            'bill': self.bill_agent,
            'discharge_summary': self.discharge_agent,
            'id_card': self.id_card_agent
        }
    
    async def process_claim(self, files: List[UploadFile]) -> ClaimProcessingResponse:
        """
        Main orchestration method for processing claim documents
        
        Args:
            files: List of uploaded PDF files
            
        Returns:
            ClaimProcessingResponse with all processing results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting claim processing for {len(files)} files")
            
            # Step 1: Extract text from PDFs
            extracted_texts = await self._extract_texts_from_files(files)
            
            # Step 2: Classify documents
            classifications = await self._classify_documents(extracted_texts)
            
            # Step 3: Process documents with specialized agents
            processed_documents = await self._process_documents(classifications)
            
            # Step 4: Validate claim data
            validation_result = await self._validate_claim(processed_documents)
            
            # Step 5: Make claim decision
            claim_decision = await self._make_claim_decision(processed_documents, validation_result)
            
            # Step 6: Structure response
            response = self._structure_response(
                processed_documents,
                validation_result,
                claim_decision,
                time.time() - start_time
            )
            
            logger.info(f"Claim processing completed in {response.processing_time:.2f} seconds")
            return response
            
        except Exception as e:
            logger.error(f"Claim processing failed: {str(e)}")
            # Return error response
            return ClaimProcessingResponse(
                documents=[],
                validation=ValidationResult(
                    validation_passed=False,
                    data_quality_issues=[f"Processing failed: {str(e)}"]
                ),
                claim_decision=ClaimDecision(
                    status="requires_review",
                    reason=f"Processing error: {str(e)}",
                    confidence=0.0
                ),
                processing_time=time.time() - start_time
            )
    
    async def _extract_texts_from_files(self, files: List[UploadFile]) -> List[Dict[str, Any]]:
        """Extract text from uploaded PDF files"""
        logger.info("Extracting text from PDF files")
        
        async def extract_single_file(file: UploadFile):
            content = await file.read()
            text = await self.pdf_service.extract_text_from_pdf(content)
            return {
                'filename': file.filename,
                'text': text or "",
                'size': len(content)
            }
        
        # Process files concurrently
        tasks = [extract_single_file(file) for file in files]
        results = await asyncio.gather(*tasks)
        
        logger.info(f"Extracted text from {len(results)} files")
        return results
    
    async def _classify_documents(self, extracted_texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify document types using ClassifierAgent"""
        logger.info("Classifying document types")
        
        async def classify_single_document(doc_data):
            return await self.classifier_agent.process(doc_data)
        
        # Classify documents concurrently
        tasks = [classify_single_document(doc) for doc in extracted_texts]
        classifications = await asyncio.gather(*tasks)
        
        # Merge classification results with original data
        for i, classification in enumerate(classifications):
            extracted_texts[i].update(classification)
        
        logger.info(f"Classified {len(classifications)} documents")
        return extracted_texts
    
    async def _process_documents(self, classified_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process documents with specialized agents"""
        logger.info("Processing documents with specialized agents")
        
        processed_docs = []
        
        for doc in classified_docs:
            doc_type = doc.get('type', 'unknown')
            
            if doc_type in self.agent_mapping:
                agent = self.agent_mapping[doc_type]
                result = await agent.process(doc)
                result['filename'] = doc['filename']
                result['classification_confidence'] = doc.get('confidence', 0.0)
                processed_docs.append(result)
            else:
                # Handle unknown document types
                processed_docs.append({
                    'type': 'unknown',
                    'filename': doc['filename'],
                    'extracted_data': {},
                    'validation_errors': ['Unknown document type'],
                    'processing_status': 'skipped',
                    'classification_confidence': doc.get('confidence', 0.0)
                })
        
        logger.info(f"Processed {len(processed_docs)} documents")
        return processed_docs
    
    async def _validate_claim(self, processed_docs: List[Dict[str, Any]]) -> ValidationResult:
        """Validate claim data using LLM"""
        logger.info("Validating claim data")
        
        # Prepare data for validation
        validation_data = []
        for doc in processed_docs:
            validation_data.append({
                'type': doc['type'],
                'filename': doc['filename'],
                'data': doc['extracted_data'],
                'errors': doc.get('validation_errors', [])
            })
        
        # Use LLM for validation
        validation_result = await self.llm_service.validate_claim_data(validation_data)
        
        return ValidationResult(
            missing_documents=validation_result.get('missing_documents', []),
            discrepancies=validation_result.get('discrepancies', []),
            data_quality_issues=validation_result.get('data_quality_issues', []),
            validation_passed=validation_result.get('validation_passed', False)
        )
    
    async def _make_claim_decision(self, processed_docs: List[Dict[str, Any]], validation: ValidationResult) -> ClaimDecision:
        """Make final claim decision using LLM"""
        logger.info("Making claim decision")
        
        # Prepare data for decision making
        decision_data = []
        for doc in processed_docs:
            decision_data.append({
                'type': doc['type'],
                'filename': doc['filename'],
                'data': doc['extracted_data'],
                'status': doc.get('processing_status', 'unknown')
            })
        
        validation_data = {
            'missing_documents': validation.missing_documents,
            'discrepancies': validation.discrepancies,
            'data_quality_issues': validation.data_quality_issues,
            'validation_passed': validation.validation_passed
        }
        
        # Use LLM for decision making
        decision_result = await self.llm_service.make_claim_decision(decision_data, validation_data)
        
        return ClaimDecision(
            status=decision_result.get('status', 'requires_review'),
            reason=decision_result.get('reason', 'Decision could not be determined'),
            confidence=decision_result.get('confidence', 0.0),
            recommended_actions=decision_result.get('recommended_actions', [])
        )
    
    def _structure_response(self, processed_docs: List[Dict[str, Any]], validation: ValidationResult, 
                          decision: ClaimDecision, processing_time: float) -> ClaimProcessingResponse:
        """Structure the final response"""
        
        # Convert processed documents to response format
        documents = []
        structured_data = {}
        
        for doc in processed_docs:
            processed_doc = ProcessedDocument(
                type=doc['type'],
                filename=doc['filename'],
                confidence=doc.get('classification_confidence', 0.0),
                extracted_data=doc.get('extracted_data', {}),
                processing_errors=doc.get('validation_errors', [])
            )
            documents.append(processed_doc)
            
            # Add to structured data
            if doc['type'] != 'unknown':
                structured_data[doc['type']] = doc.get('extracted_data', {})
        
        return ClaimProcessingResponse(
            documents=documents,
            structured_data=structured_data,
            validation=validation,
            claim_decision=decision,
            processing_time=processing_time
        )