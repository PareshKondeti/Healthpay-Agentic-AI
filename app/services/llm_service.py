import google.generativeai as genai
import os
import logging
from typing import List, Dict, Any, Optional
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        # Updated to use the current available model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    async def generate_async(self, prompt: str, temperature: float = 0.1) -> str:
        """Async wrapper for Gemini API calls"""
        loop = asyncio.get_event_loop()
        
        def _generate():
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=2048,
                    )
                )
                return response.text
            except Exception as e:
                logger.error(f"LLM generation error: {str(e)}")
                raise
        
        return await loop.run_in_executor(self.executor, _generate)
    
    async def classify_document(self, text: str, filename: str) -> Dict[str, Any]:
        """Classify document type using LLM"""
        prompt = f"""
        Analyze the following document text and filename to classify the document type.
        
        Filename: {filename}
        
        Document Text (first 1000 chars):
        {text[:1000]}
        
        Classify this document as one of:
        - bill: Medical bill or invoice
        - discharge_summary: Hospital discharge summary
        - id_card: Insurance ID card
        - unknown: Cannot determine type
        
        Return a JSON response with:
        {{
            "type": "document_type",
            "confidence": 0.95,
            "reasoning": "Brief explanation of classification"
        }}
        
        IMPORTANT: Return ONLY valid JSON, no other text.
        """
        
        try:
            response = await self.generate_async(prompt)
            # Clean the response to extract JSON
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            result = json.loads(response_text)
            return result
        except Exception as e:
            logger.error(f"Document classification error: {str(e)}")
            return {
                "type": "unknown",
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}"
            }
    
    async def extract_bill_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from medical bill"""
        prompt = f"""
        Extract key information from this medical bill document:
        
        {text}
        
        Extract the following information and return as JSON:
        {{
            "hospital_name": "Name of hospital/provider",
            "total_amount": 12500.00,
            "date_of_service": "2024-04-10",
            "patient_name": "Patient Name",
            "services": ["Service 1", "Service 2"],
            "insurance_id": "Insurance ID if present"
        }}
        
        If information is not found, use null for that field.
        IMPORTANT: Return ONLY valid JSON, no other text.
        """
        
        try:
            response = await self.generate_async(prompt)
            # Clean the response to extract JSON
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Bill extraction error: {str(e)}")
            return {}
    
    async def extract_discharge_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from discharge summary"""
        prompt = f"""
        Extract key information from this discharge summary document:
        
        {text}
        
        Extract the following information and return as JSON:
        {{
            "patient_name": "Patient Name",
            "diagnosis": "Primary diagnosis",
            "admission_date": "2024-04-01",
            "discharge_date": "2024-04-10",
            "treating_physician": "Doctor Name",
            "hospital_name": "Hospital Name",
            "procedures": ["Procedure 1", "Procedure 2"]
        }}
        
        If information is not found, use null for that field.
        IMPORTANT: Return ONLY valid JSON, no other text.
        """
        
        try:
            response = await self.generate_async(prompt)
            # Clean the response to extract JSON
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Discharge summary extraction error: {str(e)}")
            return {}
    
    async def extract_id_card_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from insurance ID card"""
        prompt = f"""
        Extract key information from this insurance ID card document:
        
        {text}
        
        Extract the following information and return as JSON:
        {{
            "patient_name": "Patient Name",
            "insurance_id": "Member ID",
            "policy_number": "Policy Number",
            "group_number": "Group Number",
            "effective_date": "2024-01-01",
            "expiration_date": "2024-12-31"
        }}
        
        If information is not found, use null for that field.
        IMPORTANT: Return ONLY valid JSON, no other text.
        """
        
        try:
            response = await self.generate_async(prompt)
            # Clean the response to extract JSON
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"ID card extraction error: {str(e)}")
            return {}
    
    async def validate_claim_data(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate claim data for consistency and completeness"""
        prompt = f"""
        Analyze these processed claim documents for validation:
        
        {json.dumps(documents, indent=2)}
        
        Check for:
        1. Missing required documents (bill, discharge summary recommended)
        2. Data inconsistencies between documents (dates, names, amounts)
        3. Data quality issues (missing critical fields)
        
        Return validation results as JSON:
        {{
            "missing_documents": ["document_type1", "document_type2"],
            "discrepancies": ["Description of discrepancy 1"],
            "data_quality_issues": ["Missing critical field X"],
            "validation_passed": true
        }}
        
        IMPORTANT: Return ONLY valid JSON, no other text.
        """
        
        try:
            response = await self.generate_async(prompt)
            # Clean the response to extract JSON
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                "missing_documents": [],
                "discrepancies": [f"Validation failed: {str(e)}"],
                "data_quality_issues": [],
                "validation_passed": False
            }
    
    async def make_claim_decision(self, documents: List[Dict[str, Any]], validation: Dict[str, Any]) -> Dict[str, Any]:
        """Make final claim decision based on processed data"""
        prompt = f"""
        Make a claim decision based on the processed documents and validation results:
        
        Documents:
        {json.dumps(documents, indent=2)}
        
        Validation Results:
        {json.dumps(validation, indent=2)}
        
        Decision criteria:
        - Approve if all required documents present and no major discrepancies
        - Reject if critical information missing or major discrepancies found
        - Require review if minor issues that need human attention
        
        Return decision as JSON:
        {{
            "status": "approved|rejected|requires_review",
            "reason": "Detailed explanation of decision",
            "confidence": 0.95,
            "recommended_actions": ["Action 1", "Action 2"]
        }}
        
        IMPORTANT: Return ONLY valid JSON, no other text.
        """
        
        try:
            response = await self.generate_async(prompt)
            # Clean the response to extract JSON
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Decision making error: {str(e)}")
            return {
                "status": "requires_review",
                "reason": f"Decision making failed: {str(e)}",
                "confidence": 0.0,
                "recommended_actions": ["Manual review required"]
            }