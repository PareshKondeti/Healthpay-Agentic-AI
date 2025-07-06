from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.llm_service import LLMService

class DischargeAgent(BaseAgent):
    """Agent specialized in processing discharge summaries"""
    
    def __init__(self, llm_service: LLMService):
        super().__init__("DischargeAgent")
        self.llm_service = llm_service
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process discharge summary document
        
        Args:
            data: Dict containing document text and metadata
            
        Returns:
            Dict with extracted discharge summary information
        """
        try:
            self.log_info("Processing discharge summary document")
            
            text = data['text']
            
            # Extract structured data from discharge summary
            extracted_data = await self.llm_service.extract_discharge_data(text)
            
            # Validate extracted data
            validation_errors = self._validate_discharge_data(extracted_data)
            
            result = {
                'type': 'discharge_summary',
                'extracted_data': extracted_data,
                'validation_errors': validation_errors,
                'processing_status': 'completed' if not validation_errors else 'completed_with_warnings'
            }
            
            self.log_info(f"Discharge summary processing completed. Found {len(validation_errors)} validation issues")
            
            return result
            
        except Exception as e:
            self.log_error(f"Discharge summary processing failed: {str(e)}")
            return {
                'type': 'discharge_summary',
                'extracted_data': {},
                'validation_errors': [f"Processing error: {str(e)}"],
                'processing_status': 'failed'
            }
    
    def _validate_discharge_data(self, data: Dict[str, Any]) -> list:
        """Validate extracted discharge summary data"""
        errors = []
        
        # Check for critical fields
        if not data.get('patient_name'):
            errors.append("Patient name not found")
        
        if not data.get('diagnosis'):
            errors.append("Diagnosis not found")
        
        if not data.get('admission_date'):
            errors.append("Admission date not found")
        
        if not data.get('discharge_date'):
            errors.append("Discharge date not found")
        
        # Validate date consistency
        if data.get('admission_date') and data.get('discharge_date'):
            # Basic date validation (could be enhanced)
            if data['admission_date'] > data['discharge_date']:
                errors.append("Admission date is after discharge date")
        
        return errors